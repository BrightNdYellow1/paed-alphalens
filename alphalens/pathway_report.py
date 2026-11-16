"""Validate fabricated referral data and reconcile reporting measures in SQLite."""
import argparse
from collections import Counter
import csv
from datetime import date
import json
from pathlib import Path
import sqlite3

COLUMNS = ("referral_id", "site", "specialty", "referral_date", "first_attendance_date", "status")
OUTPUT_COLUMNS = (*COLUMNS, "wait_days", "referral_month")

SUMMARY_SQL = """
SELECT site, specialty, referral_month, COUNT(*) AS referrals,
       SUM(CASE WHEN status = 'attended' THEN 1 ELSE 0 END) AS attended,
       SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_referrals,
       SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(AVG(wait_days), 2) AS mean_attended_wait_days
FROM pathways GROUP BY site, specialty, referral_month
ORDER BY referral_month, site, specialty
"""


def read_date(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Expected YYYY-MM-DD")
    return parsed


def prepare(rows):
    id_counts = Counter(row["referral_id"] for row in rows if row.get("referral_id"))
    accepted = []
    errors = Counter()
    for row in rows:
        identifier = row.get("referral_id")
        if not identifier or len(row) != len(COLUMNS) or any(row.get(k) is None for k in COLUMNS):
            errors["invalid_structure"] += 1
            continue
        if id_counts[identifier] > 1:
            errors["duplicate_referral"] += 1
            continue
        status = row["status"]
        if not row["site"] or not row["specialty"] or status not in ("attended", "open", "cancelled"):
            errors["invalid_category"] += 1
            continue
        attendance = row["first_attendance_date"]
        if bool(attendance) != (status == "attended"):
            errors["inconsistent_attendance"] += 1
            continue
        try:
            referred = read_date(row["referral_date"])
            elapsed = (read_date(attendance) - referred).days if attendance else None
            if elapsed is not None and elapsed < 0:
                raise ValueError("Attendance precedes referral")
        except ValueError:
            errors["invalid_date"] += 1
            continue
        accepted.append({**row, "wait_days": elapsed, "referral_month": referred.isoformat()[:7]})
    return accepted, dict(errors)


def write_report(source, destination):
    with source.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError("Unexpected referral columns")
        rows = list(reader)
    accepted, errors = prepare(rows)

    with sqlite3.connect(":memory:") as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("""CREATE TABLE pathways (
            referral_id TEXT PRIMARY KEY, site TEXT, specialty TEXT, referral_date TEXT,
            first_attendance_date TEXT, status TEXT, wait_days INTEGER, referral_month TEXT
        )""")
        connection.executemany(
            "INSERT INTO pathways VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ([row[k] for k in OUTPUT_COLUMNS] for row in accepted),
        )
        summary = [dict(row) for row in connection.execute(SUMMARY_SQL)]

    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "pathways.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(accepted)
    report = {
        "source_rows": len(rows), "accepted_rows": len(accepted),
        "rejected_rows_by_reason": errors, "summary": summary,
    }
    (destination / "reconciliation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_report(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
