# ADR-0011: Typed relationships (FS/SS/FF/SF) with lag

- **Status:** Accepted
- **Date:** 2026-07-10
- **Deciders:** Core team
- **Supersedes:** — (lifts the deferral of LOE behaviour recorded in ADR-0008)

## Context

The schema has modelled a `Relationship` (predecessor, type, lag) since ADR-0003,
but the engine only understood plain predecessor ids — implicitly finish-to-start
with no lag. Real schedules routinely need the other three types ("paint starts
2 days after plastering *starts*", "commissioning finishes when installation
finishes") and lags in both directions (a negative lag is a *lead*: overlap).
This also blocked level-of-effort activities, whose behaviour ADR-0008 explicitly
deferred "until typed relationships land".

## Decision

### Two dependency forms, one canonical

`Activity` now carries both `predecessors: List[str]` (the pre-existing simple
form) and `relationships: List[Relationship]` (the typed form). A schema
validator makes them impossible to disagree: bare ids become implicit FS/0
relationships, and `predecessors` is rebuilt as the ids of `relationships`.
Existing callers, stored data, and the current UI keep working unchanged; no
migration is needed.

### Constraint semantics

For a relationship P → S with lag L (working days, may be negative):

| Type | Forward pass enforces | Backward pass enforces |
|------|----------------------|------------------------|
| FS   | ES(S) ≥ EF(P) + L    | LF(P) ≤ LS(S) − L      |
| SS   | ES(S) ≥ ES(P) + L    | LS(P) ≤ LS(S) − L      |
| FF   | EF(S) ≥ EF(P) + L    | LF(P) ≤ LF(S) − L      |
| SF   | EF(S) ≥ ES(P) + L    | LS(P) ≤ LF(S) − L      |

Two boundary rules complete the algorithm, and both were deliberate decisions:

1. **ES is clamped at 0.** Nothing starts before the project. A lead or an
   FF/SF constraint on a short successor can otherwise imply a negative start.
2. **LF is capped at the project finish — for every activity.** Nothing may
   finish after the project without, by definition, delaying it. Without the
   cap, an activity whose only successors constrain its *start* (e.g. via SS)
   would show a late finish beyond the end of the project.

### Free float includes the project finish for every activity

Free float is the tightest relationship slack toward any successor **and** the
slack to the project finish. The finish term is not just for terminal
activities: the Hypothesis property suite produced a counterexample (a
zero-duration predecessor with an FS lead into a clamped successor) where
relationship slack alone made free float exceed total float, violating the
float hierarchy. With the finish term, FF ≤ TF is provable for all four types.

### Level of effort (completes ADR-0008)

An LOE with relationships now *spans* the activities it supports — earliest ES
to latest EF — instead of scheduling as a task. It stretches with the work, so
it has no float of its own and is never on the critical path. Because an LOE
follows work rather than driving it, an LOE appearing as anyone's predecessor
is rejected with a clear error. An LOE with no relationships schedules as an
ordinary task. `SUMMARY` remains deferred pending the WBS, as ADR-0008 records.

## Consequences

- The engine implements the full P6-style relationship vocabulary; the Gantt
  (Phase 5/6) can draw all four link types with lags.
- Start-driven criticality now exists: an SS predecessor of critical work is
  itself critical even though its finish constrains nobody. This is correct
  and matches industry tools, but may surprise users used to FS-only networks;
  the explanation lives in [cpm.md](../domain/cpm.md).
- Negative float cannot occur yet — it requires deadline constraints, which
  are not modelled. When deadlines land, the "TF ≥ 0" property test must be
  relaxed deliberately, not accidentally.
- The property-based suite (`test_properties.py`) is now the engine's
  specification-by-invariant; new scheduling features must extend it.
