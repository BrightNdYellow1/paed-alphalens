import json
from pathlib import Path

from alphalens.chis_merge import assess


def test_dry_run_blocks_conflict_and_recovers_with_signed_off_mapping():
    scenario = Path(__file__).resolve().parents[1] / "chis-lab"
    config = (scenario / "config.json").read_bytes()
    sources = {path.stem: path.read_bytes() for path in scenario.glob("unit-*.json")}
    good = assess(config, sources)

    assert good["decision"] == "GO"
    assert good["proposed_target_status_counts"] == {"confirmed": 1, "awaiting_review": 2}
    assert good["per_unit"]["unit-south"]["duplicate"] == 1

    changed = json.loads(sources["unit-south"])
    changed[0]["evidence_date"] = "2026-01-13"
    bad = assess(config, dict(sources, **{"unit-south": json.dumps(changed).encode()}))
    assert bad["decision"] == "NO_GO"
    assert bad["per_unit"]["unit-south"]["conflicts"] == 1
    assert bad["proposed_target_status_counts"] == {"awaiting_review": 2}

    assert assess(config, sources) == good


def test_unknown_local_id_and_missing_source_row_block_cutover():
    scenario = Path(__file__).resolve().parents[1] / "chis-lab"
    config = (scenario / "config.json").read_bytes()
    north = (scenario / "unit-north.json").read_bytes()
    south = [{"child_key": "UNKNOWN", "dose_code": "X1", "evidence_date": "2026-01-12", "review_code": "V"}]
    report = assess(config, {"unit-north": north, "unit-south": json.dumps(south).encode()})
    assert report["decision"] == "NO_GO"
    assert report["per_unit"]["unit-south"]["unmapped"] == 1
    assert any("source row count" in reason for reason in report["reasons"])
