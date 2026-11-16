"""Run the simulated review queue audit before and after a routing correction."""
import argparse
import json
from pathlib import Path

from alphalens.chis_merge import assess


def drill(scenario):
    baseline_config = (scenario / "config.json").read_bytes()
    sources = {path.stem: path.read_bytes() for path in scenario.glob("unit-*.json")}
    baseline = assess(baseline_config, sources)

    changed_config = json.loads(baseline_config)
    prior_owner = changed_config["review_queue"]["routes"].pop("unit-south")
    after_merge = assess(json.dumps(changed_config).encode(), sources)

    changed_config["review_queue"]["routes"]["unit-south"] = prior_owner
    after_correction = assess(json.dumps(changed_config).encode(), sources)

    snapshots = (baseline, after_merge, after_correction)
    if ([item["decision"] for item in snapshots] != ["GO", "NO_GO", "GO"]
            or [item["review_queue"]["unassigned"] for item in snapshots] != [0, 1, 0]
            or any(item["proposed_target_status_counts"] != baseline["proposed_target_status_counts"]
                   for item in snapshots)):
        raise RuntimeError("The drill did not reproduce the expected queue failure and recovery")

    return {
        "baseline": baseline,
        "after_simulated_merge": after_merge,
        "after_correction": after_correction,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = drill(args.scenario)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for phase, snapshot in report.items():
        queue = snapshot["review_queue"]
        print(f"{phase}: {snapshot['decision']}, {queue['visible_tasks']}/{queue['expected_tasks']} visible")


if __name__ == "__main__":
    main()
