"""Generate synthetic AlphaLens warehouse fixtures and an executable SQL drill."""
import argparse
import csv
from io import StringIO
import json
from pathlib import Path

from alphalens.core import synthetic_case
from alphalens.pipeline import transform


def fixture():
    raw = synthetic_case().to_csv(index=False).encode()
    outputs, count = transform(raw, True)
    finding = json.loads(outputs["evidence.json"])
    observations = list(csv.DictReader(StringIO(outputs["curated.csv"].decode())))
    return {
        "case_label": finding["case"],
        "row_count": count,
        "original_sharpe": finding["original_sharpe"],
        "corrected_sharpe": finding["corrected_sharpe"],
        "observations": observations,
    }


def sql_literal(payload):
    encoded = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    chunks = [encoded[offset:offset + 1500] for offset in range(0, len(encoded), 1500)]
    literals = ["N'" + chunk.replace("'", "''") + "'" for chunk in chunks]
    return "CAST(N'' AS nvarchar(max)) +\n" + " +\n".join(literals)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    valid = fixture()
    rejected_rows = [dict(row) for row in valid["observations"][:3]]
    rejected_rows[1]["period"] = rejected_rows[0]["period"]
    invalid = dict(valid, row_count=3, observations=rejected_rows)
    corrected_rows = [dict(row) for row in rejected_rows]
    corrected_rows[1]["period"] = "1"
    corrected = dict(invalid, observations=corrected_rows)

    for name, payload in [("valid", valid), ("invalid", invalid), ("corrected", corrected)]:
        (args.output / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")

    sql = f"""
USE AlphaLensWarehouseLab;
SET NOCOUNT ON;
DECLARE @start bigint = ISNULL((SELECT MAX(attempt_id) FROM dbo.LoadAttempt), 0);
DECLARE @valid nvarchar(max) = {sql_literal(valid)};
DECLARE @invalid nvarchar(max) = {sql_literal(invalid)};
DECLARE @corrected nvarchar(max) = {sql_literal(corrected)};
DECLARE @existing bit = CASE WHEN EXISTS (
    SELECT 1 FROM dbo.Batch WHERE batch_id = CONVERT(char(64), HASHBYTES('SHA2_256', @valid), 2)
) THEN 1 ELSE 0 END;

EXEC dbo.LoadEvidence @valid;
EXEC dbo.LoadEvidence @valid;
BEGIN TRY
    EXEC dbo.LoadEvidence @invalid;
    THROW 51002, 'Unexpected success for duplicate periods.', 1;
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() <> 51001 OR ERROR_MESSAGE() <> 'Duplicate period identifiers.' THROW;
END CATCH;
EXEC dbo.LoadEvidence @corrected;

IF (SELECT COUNT(*) FROM dbo.Observation
    WHERE batch_id = CONVERT(char(64), HASHBYTES('SHA2_256', @valid), 2)) <> 420
    THROW 51002, 'Valid batch has missing or duplicate observations.', 1;
IF (SELECT COUNT(*) FROM dbo.Observation
    WHERE batch_id = CONVERT(char(64), HASHBYTES('SHA2_256', @corrected), 2)) <> 3
    THROW 51002, 'Corrected batch did not load three rows.', 1;
IF EXISTS (SELECT 1 FROM dbo.Batch
    WHERE batch_id = CONVERT(char(64), HASHBYTES('SHA2_256', @invalid), 2))
    THROW 51002, 'Rejected input appeared in reporting.', 1;
IF (SELECT COUNT(*) FROM dbo.LoadAttempt WHERE attempt_id > @start AND status = 'rejected'
    AND inserted_rows = 0 AND payload = @invalid) <> 1
    THROW 51002, 'Rejection or raw payload was not recorded.', 1;
IF (SELECT COUNT(*) FROM dbo.LoadAttempt WHERE attempt_id > @start AND status = 'replayed'
    AND inserted_rows = 0 AND payload = @valid) <> 1 + @existing
    THROW 51002, 'Valid rerun was not recorded as a replay.', 1;

SELECT attempt_id, case_label, status, input_rows, inserted_rows, error_message
FROM dbo.LoadStatus WHERE attempt_id > @start ORDER BY attempt_id;
"""
    (args.output / "drill.sql").write_text(sql, encoding="utf-8")


if __name__ == "__main__":
    main()
