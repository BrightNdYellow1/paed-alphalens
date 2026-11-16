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

## Review queues and repeat audit

```bash
python -m alphalens.chis_queue_drill --scenario chis-lab --output queue-audit.json
```

The drill runs the same unit files through three configuration snapshots.
The source hashes and proposed record counts stay the same throughout.
Only the routing configuration changes.

| Phase | Proposed records | Visible review tasks | Unassigned | Decision |
|---|---:|---:|---:|---|
| Baseline | 3 | 2 of 2 | 0 | GO |
| Simulated merge with missing South route | 3 | 1 of 2 | 1 | NO_GO |
| After the route is restored | 3 | 2 of 2 | 0 | GO |

Each task records its fictional owner, contributing units, any exception
and the next action. The acceptance check also blocks an ambiguous route
or a task that the assigned team cannot see under the simulated access
settings. A reviewer can use the stored snapshots to compare outcomes
without editing the original unit files.

### Staff walkthrough

1. Take the role of Review South. Find synthetic child C03 and explain why
   there should be a review task. Check the baseline result.
2. Find C03 in the simulated merge snapshot. The task is present in the
   audit, but its owner is missing. Compare its source unit to the routes
   in the mapping. Restore the agreed route and rerun to verify visibility.
3. As a separate fault, copy the scenario and set Review South's list in
   visible_queues to an empty list. Run chis_merge against the copy. C03
   has an owner but is not visible. Restore the simulated access and
   rerun. Explain why this fix differs from restoring a route.
4. Ask a colleague to repeat the exercise from these instructions and
   record where they needed guidance and what made the problem clear.

The walkthrough is for practising how to investigate and explain a change.
The route and access checks are synthetic and do not configure SystmOne.
