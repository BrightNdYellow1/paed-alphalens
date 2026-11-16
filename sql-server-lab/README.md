# AlphaLens SQL Server warehouse lab

This lab uses synthetic AlphaLens outputs. It demonstrates a T-SQL warehouse
load, reconciled reporting data, repeat-safe processing and recovery. It
requires a disposable SQL Server 2022 Developer instance. The GitHub Actions
workflow provisions an isolated Linux container and runs the executable drill.

From the repository root, generate the fixtures and run the schema and drill
with an authenticated sqlcmd session:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python sql-server-lab/prepare_drill.py /tmp/alphalens-sql
sqlcmd -S localhost -U sa -C -b -i sql-server-lab/schema.sql
sqlcmd -S localhost -U sa -C -b -i /tmp/alphalens-sql/drill.sql
```

Use `SQLCMDPASSWORD` or an interactive credential prompt. The workflow creates
a one-off password, masks it and exposes no SQL Server port to the host.
Run `recovery.sql` on a clean Linux lab instance to back up the warehouse,
restore to a separate database and compare table counts. Its paths are for
the Linux container. The lab never needs NHS records or an Azure subscription.

## Data dictionary and source mapping

| Table | Grain and key | Mapping |
|---|---|---|
| Batch | One row per exact warehouse payload. SHA-256 is the primary key. | Case label, row count and Sharpe metrics from the AlphaLens evidence. This hash identifies the JSON submitted to SQL Server. |
| Observation | One row per batch and period. Composite primary key. | Period, market return, position and both equity values from the curated dataset. |
| LoadAttempt | One row per submission, keyed by attempt ID. | Submitted JSON, UTC timestamps, reported counts, status and diagnostic message. |
| LoadStatus | One row per submission, including rejections. | Joins attempt metadata to published batch metrics for reporting without exposing the payload. |

The stored procedure validates row counts, numeric values, and uniqueness.
It retains rejected payloads in the attempt history, rolls back failed loads,
and uses a transaction and key-range locking to prevent concurrent duplicates.
The drill checks 420 published rows, zero additional rows on replay, no
reporting batch for the duplicate-period input and three rows after correction.

## Windows BI exercises

These are setup exercises to complete in a Windows SQL Server 2022 lab.
The Linux workflow verifies the database engine path.

- **SSIS:** In SSDT create an Integration Services package. Read one generated
  JSON fixture with a Script Task, pass its full text as an NVARCHAR(MAX)
  parameter to an Execute SQL Task calling `dbo.LoadEvidence`, and use task
  failure handling to surface a rejected load. Repeat with the invalid and
  corrected fixtures. Query `dbo.LoadStatus` to reconcile the outcomes.
- **SSRS:** Create a paginated report with a dataset over `dbo.LoadStatus`.
  Display status, start/end timestamps, row counts and error text, then
  publish to a SQL Server 2022 Reporting Services lab server and run it.
- **SSAS:** Create a Tabular model over Batch and Observation, linked by
  batch ID. Add measures for observation count and distinct batch count,
  deploy to an Analysis Services Tabular instance and reconcile against SQL.

The first query in `report.sql` can serve as the SSRS dataset. In SSAS,
use measures `Observations := COUNTROWS(Observation)` and
`Batches := DISTINCTCOUNT(Batch[batch_id])`. A fresh drill should show
423 observations and two published batches.

Capture the package log, a report export and the Tabular query result when
you run each exercise. Those are separate evidence from the T-SQL drill.

The [Windows BI artifacts](bi/README.md) include a package builder, an RDL
report and generated Tabular deployment commands, with steps for running
each against the lab warehouse.
