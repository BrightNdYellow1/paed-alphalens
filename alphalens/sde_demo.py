"""Link fabricated vaccination records and publish a research review summary."""
import argparse
from collections import Counter
import csv
from datetime import date
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path

SCHEMAS = {
    "cohort.csv": ("synthetic_id", "practice"),
    "practice.csv": ("synthetic_id", "vaccination_date"),
    "external.csv": ("synthetic_id", "vaccination_date"),
}
STATES = (
    "confirmed_in_practice",
    "external_evidence_awaiting_review",
    "conflicting_dates_require_review",
    "no_evidence_in_loaded_sources",
)


def parse_csv(raw, columns):
    reader = csv.DictReader(StringIO(raw.decode("utf-8"), newline=""))
    if tuple(reader.fieldnames or ()) != columns:
        raise ValueError(f"Expected columns: {', '.join(columns)}")
    return list(reader)


def classify(practice_dates, external_dates):
    if len(practice_dates | external_dates) > 1:
        return "conflicting_dates_require_review"
    if practice_dates:
        return "confirmed_in_practice"
    if external_dates:
        return "external_evidence_awaiting_review"
    return "no_evidence_in_loaded_sources"


def analyse(sources):
    parsed = {name: parse_csv(sources[name], schema) for name, schema in SCHEMAS.items()}
    cohort = {}
    for row in parsed["cohort.csv"]:
        identifier, practice = row["synthetic_id"], row["practice"]
        if len(row) != 2 or not identifier or not practice or identifier in cohort:
            raise ValueError("Cohort must contain one valid row per synthetic ID")
        cohort[identifier] = practice

    dates = {source: {identifier: set() for identifier in cohort}
             for source in ("practice.csv", "external.csv")}
    counts = {}
    for source, by_person in dates.items():
        outcomes = Counter({key: 0 for key in ("accepted", "duplicate", "unmatched", "invalid")})
        for row in parsed[source]:
            try:
                if len(row) != 2 or not row["synthetic_id"]:
                    raise ValueError("Invalid row")
                observed = date.fromisoformat(row["vaccination_date"] or "")
                if observed.isoformat() != row["vaccination_date"]:
                    raise ValueError("Expected YYYY-MM-DD")
            except ValueError:
                outcomes["invalid"] += 1
                continue

            identifier = row["synthetic_id"]
            if identifier not in by_person:
                outcomes["unmatched"] += 1
                continue
            if observed in by_person[identifier]:
                outcomes["duplicate"] += 1
                continue
            by_person[identifier].add(observed)
            outcomes["accepted"] += 1
        counts[source] = {"rows_received": len(parsed[source]), **outcomes}

    totals = {practice: Counter({state: 0 for state in STATES})
              for practice in sorted(set(cohort.values()))}
    for identifier, practice in cohort.items():
        status = classify(dates["practice.csv"][identifier], dates["external.csv"][identifier])
        totals[practice][status] += 1

    return {
        "schema_version": 1,
        "data_classification": "synthetic demonstration only",
        "sources": {name: {"sha256": sha256(raw).hexdigest(), "rows": len(parsed[name])}
                    for name, raw in sorted(sources.items())},
        "quality": counts,
        "practices": {
            practice: {"cohort_size": sum(statuses.values()), **statuses}
            for practice, statuses in totals.items()
        },
        "interpretation": "No evidence in the loaded sources cannot establish vaccination status.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    sources = {name: (args.input / name).read_bytes() for name in SCHEMAS}
    report = analyse(sources)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
