from pathlib import Path

from alphalens.pathway_report import write_report


def test_pathway_report_reconciles_referrals_and_excludes_bad_rows(tmp_path):
    fixture = Path(__file__).resolve().parents[1] / "pathway-lab" / "referrals.csv"
    report = write_report(fixture, tmp_path)

    assert report["source_rows"] == 9
    assert report["accepted_rows"] == 5
    assert report["rejected_rows_by_reason"] == {
        "duplicate_referral": 2, "invalid_date": 1, "inconsistent_attendance": 1,
    }
    assert report["summary"][0] == {
        "site": "Fictional North", "specialty": "Cardiology", "referral_month": "2026-10",
        "referrals": 3, "attended": 2, "open_referrals": 1, "cancelled": 0,
        "mean_attended_wait_days": 17.0,
    }
    assert all(
        row["referrals"] == row["attended"] + row["open_referrals"] + row["cancelled"]
        for row in report["summary"]
    )
    assert report["summary"][-1]["mean_attended_wait_days"] is None
