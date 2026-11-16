# Synthetic vaccination evidence data product

This independent AlphaLens exercise models a question from primary care.
Can a researcher distinguish an absent vaccination entry from external
evidence that has not yet been reviewed? The inputs are entirely fabricated.
The exercise concerns one hypothetical dose and uses a shared synthetic key.
It does not perform real patient matching or calculate vaccine uptake.

## Run the example

From the repository root:

```bash
python -m alphalens.sde_demo --input sde-lab/fixtures --output vaccination-review.json
python -m pytest -q tests/test_sde_demo.py
```

## Data contract

| Source or field | Grain and meaning |
|---|---|
| cohort.csv | One row per synthetic ID with one fictional practice. Duplicate IDs fail the run. |
| practice.csv | One recorded vaccination date per source row. The lab assumes valid practice records are confirmed. |
| external.csv | External evidence per source row. It has no clinical confirmation in this lab. |
| practice cohort_size | Number of synthetic IDs assigned to that practice. The four output statuses partition this denominator. |
| quality | Input counts for each evidence feed, partitioned into accepted, duplicate, unmatched and invalid rows. |
| sources | SHA-256 of each exact input file and its parsed row count. |

Dates must use YYYY-MM-DD. Exact duplicate dates for the same ID within a
source count once. Rows with invalid values and rows that do not match the
cohort are counted separately and excluded from classification. Distinct
valid dates for an ID are flagged for review, including disagreements
within a source. If there is one date and it appears in the practice feed,
the dose is counted as confirmed. External evidence alone awaits review.
No usable evidence in the loaded sources leaves vaccination status unknown.
That category can include an invalid source row.

The supplied fixtures yield six cohort members, one confirmed dose, two
awaiting review, one date conflict and two without usable evidence. The
report contains practice-level counts and source metadata. It does not emit
the source rows or synthetic IDs. Re-running the same inputs yields the same
report.

## Handover for research use

The status counts are a data-quality and review summary. A downstream
researcher would need a clinical definition of the dose, a time window,
an agreed denominator and details of source completeness before estimating uptake.
The small practice counts are safe to share here because all inputs are invented.
A real SDE release would require an approved purpose, controlled access,
documented linkage and field definitions, and disclosure review of any outputs.
This lab does not implement those controls or connect to a live SDE.
