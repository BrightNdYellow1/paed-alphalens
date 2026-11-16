from pathlib import Path

import pytest

from alphalens.sde_demo import SCHEMAS, analyse


def inputs():
    root = Path(__file__).resolve().parents[1] / "sde-lab" / "fixtures"
    return {name: (root / name).read_bytes() for name in SCHEMAS}


def test_report_preserves_uncertainty_and_reconciles_both_sources():
    sources = inputs()
    report = analyse(sources)

    assert report == analyse(sources)
    assert report["practices"]["Fictional North"] == {
        "cohort_size": 3, "confirmed_in_practice": 1,
        "external_evidence_awaiting_review": 1, "conflicting_dates_require_review": 1,
        "no_evidence_in_loaded_sources": 0,
    }
    assert report["practices"]["Fictional South"]["no_evidence_in_loaded_sources"] == 2
    for quality in report["quality"].values():
        assert quality["rows_received"] == sum(
            quality[key] for key in ("accepted", "duplicate", "unmatched", "invalid")
        )
    assert report["quality"]["practice.csv"]["duplicate"] == 1
    assert report["quality"]["practice.csv"]["invalid"] == 1
    assert report["quality"]["external.csv"]["unmatched"] == 1
    assert "synthetic_id" not in str(report)


def test_duplicate_cohort_key_is_rejected():
    sources = inputs()
    sources["cohort.csv"] += b"S01,Fictional South\n"
    with pytest.raises(ValueError, match="one valid row"):
        analyse(sources)
