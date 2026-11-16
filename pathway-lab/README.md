# Synthetic patient pathway reporting lab

This lab uses invented referrals and fictional sites. Each accepted row is
one referral. Wait days measure calendar days from referral to the first
recorded attendance for the attended cohort. These are demo definitions,
not NHS RTT rules or a live PAS extract.

## Generate and check the reporting data

Run from the repository root:

```bash
python -m alphalens.pathway_report --input pathway-lab/referrals.csv --output ./pathway-output
python -m pytest -q tests/test_pathway_report.py
```

The workflow rejects both copies of an ambiguous duplicate rather than
picking a row, and excludes inconsistent attendance and invalid dates.
It produces a typed-by-contract CSV and a SQLite reconciliation report.
The test fixture has nine inputs, five accepted rows and four rejected rows.
Among accepted rows there are two attended, two open and one cancelled.
The attended waits are 10 and 24 days, averaging 17. Open and cancelled
referrals do not enter the wait denominator. Counts describe the accepted
rows only. Review the four exceptions before drawing wider conclusions.

## Build and validate the Power BI report

1. Open Power BI Desktop and create a text parameter named `PathwaysCsv`
   containing the full path to the generated pathways.csv.
2. Create a blank query named `Pathways`. Paste Pathways.m in the Advanced
   Editor, then Close & Apply.
3. Add each measure from measures.dax separately using New measure.
4. Create cards for referrals, attended, open, cancelled, mean attended
   wait and status reconciliation. Add slicers for site, specialty and
   referral month. Use a matrix for the same breakdown as reconciliation.json.
5. Compare unfiltered cards and each matrix row to the SQL reference.
   Reconciliation should be zero. In November the mean attended wait
   should be blank. With the October Cardiology filter there should be
   three accepted referrals, two attendances and a 17-day mean.
6. Refresh from a fresh export and repeat the checks. Save the PBIX and
   capture the validation evidence locally after checking the visuals.

Power Query and DAX are supplied as source files. Report assembly and DAX
execution require Power BI Desktop. The automated checks here exercise the
source validation and SQLite calculations.
