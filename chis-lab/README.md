# Synthetic CHIS consolidation rehearsal

This exercise models two fictional unit exports with different field names,
local identifiers and status codes. It produces an assurance report and
does not connect to SystmOne, write to an EPR or process patient data. The
configuration file represents a mapping agreed for this demonstration.

## Run the drill

From the repository root:

```bash
python -m alphalens.chis_merge --scenario chis-lab --output chis-assurance.json
```

A clean run receives two rows per unit, collapses one identical overlap and
reconciles three proposed target records: one confirmed and two awaiting
review. The output includes source and mapping fingerprints and row outcomes
by unit. A missing mapping, invalid value, conflicting record or count
variance returns `NO_GO` and exit code 2. Invalid configuration or unreadable
input also exits unsuccessfully.

Copy the scenario to a temporary directory and change the first evidence
date in unit-south.json to 2026-01-13. Rerun and record the blocked decision.
The lab excludes the contested child-dose pair from the proposed counts
and never selects a conflicting date by feed order. Investigate against the
original synthetic evidence, restore the fixture in the copy and rerun.
Do not change the baseline merely to pass reconciliation.

## Operational assurance exercise

| Phase | Rehearsal evidence or proposed control |
|---|---|
| Requirements and configuration | Agree which fields, codes, review statuses and workflows must survive consolidation. Record old-to-new mappings. Use an approved crosswalk. The lab never guesses identity matches. |
| Pre-cutover | Take an agreed source snapshot, baseline volumes and exception counts, test staff access and workflow readiness in an approved environment, and record who makes the go/no-go decision. |
| Reconciliation | Check source counts by unit, proposed target counts by status, duplicate and conflict handling, and whether outstanding review work is still visible. A failed threshold blocks progression. |
| Rollback and continuity | Agree how staff would continue working and what would trigger rollback before the cutover. In this dry run, a failure changes no system and previous reports can be retained independently. |
| Post-merge audit | Reconcile report totals and spot-check mapped records, permissions, review queues and interfaces with operational and technical owners. Record exceptions and escalation owners. |

The dry run uses one hypothetical dose and a pre-supplied identity crosswalk.
A real migration needs approved tooling, governed data access, stakeholder
sign-off, clinical safety assurance and separate testing of local interfaces.
