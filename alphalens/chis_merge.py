"""Rehearse reconciliation for two fabricated child health units."""
import argparse
from collections import Counter, defaultdict
from datetime import date
from hashlib import sha256
import json
from pathlib import Path


def audit_review_queue(settings, awaiting, source_units):
    routes = settings["routes"]
    visible_queues = settings["visible_queues"]
    tasks = []
    issues = Counter({kind: 0 for kind in ("unassigned", "ambiguous_route", "not_visible")})
    for child, dose in sorted(awaiting):
        units = sorted(source_units[(child, dose)])
        owners = {routes.get(unit) for unit in units}
        owner = None
        issue = None
        if None in owners:
            issue = "unassigned"
        elif len(owners) != 1:
            issue = "ambiguous_route"
        else:
            owner = owners.pop()
            if owner not in visible_queues.get(owner, []):
                issue = "not_visible"
        if issue:
            issues[issue] += 1
        tasks.append({
            "synthetic_child": child, "dose": dose, "source_units": units,
            "owner": owner, "issue": issue,
            "next_action": {
                "unassigned": "Restore the agreed team route and rerun",
                "ambiguous_route": "Agree one owner across contributing units",
                "not_visible": "Check the assigned team's simulated queue access",
                None: "Review evidence in the assigned queue",
            }[issue],
        })
    return {
        "expected_tasks": len(tasks),
        "visible_tasks": len(tasks) - sum(issues.values()),
        **issues,
        "tasks": tasks,
    }


def assess(config_bytes, source_bytes):
    config = json.loads(config_bytes)
    units = config["units"]
    if set(units) != set(source_bytes):
        raise ValueError("Provide exactly the units listed in the configuration")

    totals = {}
    target = {}
    conflicts = set()
    source_units = defaultdict(set)
    for unit, raw in sorted(source_bytes.items()):
        settings = units[unit]
        rows = json.loads(raw)
        if not isinstance(rows, list):
            raise ValueError("Each unit feed must be a JSON array")
        counts = Counter({key: 0 for key in ("mapped", "duplicate", "unmapped", "invalid", "conflicts")})
        for row in rows:
            if not isinstance(row, dict):
                counts["invalid"] += 1
                continue
            try:
                values = {field: row[source] for field, source in settings["fields"].items()}
                if not all(isinstance(value, str) and value for value in values.values()):
                    raise ValueError("Empty or invalid field")
                observed = date.fromisoformat(values["date"])
                if observed.isoformat() != values["date"]:
                    raise ValueError("Expected YYYY-MM-DD")
            except (KeyError, ValueError):
                counts["invalid"] += 1
                continue

            child = settings["crosswalk"].get(values["child"])
            dose = settings["dose_codes"].get(values["dose"])
            status = settings["status_codes"].get(values["status"])
            if any(value is None for value in (child, dose, status)):
                counts["unmapped"] += 1
                continue

            key = (child, dose)
            record = (observed.isoformat(), status)
            source_units[key].add(unit)
            if key not in target:
                target[key] = record
                counts["mapped"] += 1
            elif target[key] == record:
                counts["duplicate"] += 1
            else:
                conflicts.add(key)
                counts["conflicts"] += 1

        totals[unit] = {"received": len(rows), **counts}

    statuses = Counter(record[1] for key, record in target.items() if key not in conflicts)
    expected = config["expected"]
    blocked = []
    for unit, counts in totals.items():
        if counts["received"] != expected["source_rows"].get(unit):
            blocked.append(f"{unit}: source row count does not match the signed-off baseline")
        for issue in ("invalid", "unmapped", "conflicts"):
            if counts[issue]:
                blocked.append(f"{unit}: {counts[issue]} {issue}")
    if dict(statuses) != expected["target_status_counts"]:
        blocked.append("Proposed target counts do not match the signed-off baseline")

    queue = None
    if "review_queue" in config:
        awaiting = [key for key, record in target.items()
                    if key not in conflicts and record[1] == "awaiting_review"]
        queue = audit_review_queue(config["review_queue"], awaiting, source_units)
        if queue["expected_tasks"] != expected["target_status_counts"].get("awaiting_review", 0):
            blocked.append("Review task total does not match the signed-off baseline")
        if queue["visible_tasks"] != queue["expected_tasks"]:
            blocked.append("Outstanding review tasks lack an agreed owner or staff visibility")
    return {
        **({"review_queue": queue} if queue is not None else {}),
        "decision": "NO_GO" if blocked else "GO",
        "scope": "Synthetic rehearsal only. No EPR writes.",
        "reasons": blocked,
        "per_unit": totals,
        "proposed_target_status_counts": dict(sorted(statuses.items())),
        "fingerprints": {
            "configuration": sha256(config_bytes).hexdigest(),
            "sources": {unit: sha256(raw).hexdigest() for unit, raw in sorted(source_bytes.items())},
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = (args.scenario / "config.json").read_bytes()
    sources = {path.stem: path.read_bytes() for path in args.scenario.glob("unit-*.json")}
    report = assess(config, sources)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["decision"])
    if report["decision"] == "NO_GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
