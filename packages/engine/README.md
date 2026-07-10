# `engine` — pure CPM + EVM computation

> Category: **Reference**. The scheduling core. Pure functions, no I/O. Produced in
> **Phase 2**. For how the algorithm works, see
> [docs/domain/cpm.md](../../docs/domain/cpm.md).

## Purpose

Computes the schedule (ES/EF/LS/LF, total/free float, critical path) and — as it
grows — earned-value metrics, from a set of activities and relationships. It is a
pure transformation: same input, same output, every time. No database, no clock,
no framework.

## Stability

`stable`. All four relationship types with lag, calendars, level-of-effort
spanning, and earned value are implemented and guarded by a property-based
test suite (Hypothesis) as well as hand-worked cases — the Phase 2 bar
(see [ADR-0011](../../docs/adr/0011-typed-relationships.md),
[ADR-0012](../../docs/adr/0012-calendars.md),
[ADR-0013](../../docs/adr/0013-earned-value.md)).

## Public API

- `CPMScheduler(activities)` — construct with a `{id: Activity}` mapping.
- `.schedule()` — run forward + backward passes for all four relationship
  types (FS/SS/FF/SF) with lag, populate CPM fields in place.
- `.get_critical_path()` — list of activity ids with zero total float.
- `.get_milestones()` — list of activity ids that are milestones.
- `.project_duration()` — the largest early finish.
- `SchedulerError` — raised on cycles, unknown predecessors, or an activity
  depending on a level-of-effort activity.
- `WorkdayCalendar(calendar, anchor_date)` — maps working-day offsets to real
  dates: `.date_of(offset)`, `.span_of(activity)`, `.map_schedule(activities)`
  (see ADR-0012 for the conventions).
- `compute_evm(activities, as_of_day)` — earned-value snapshot of a scheduled
  network, returned as a schema `EVMResult` (see ADR-0013).

## Activity types

`TASK` and `MILESTONE` are scheduled by the standard passes (a milestone is a
zero-duration task). `LEVEL_OF_EFFORT` now has its true behaviour: it *spans*
the activities it supports (earliest ES to latest EF), never drives other work,
and is never on the critical path (ADR-0011 lifts the deferral recorded in
[ADR-0008](../../docs/adr/0008-activity-types.md)). `SUMMARY` is still
scheduled as a task until the WBS lands.

## Invariants

- The scheduler never mutates the *set* of activities it is given (only fills
  their computed CPM fields).
- A network with a cycle raises `SchedulerError` rather than looping.
- An unknown predecessor reference raises `SchedulerError`.
- `EF = ES + duration`, `ES ≥ 0`, `total_float ≥ 0`, `free_float ≤ total_float`,
  no `LF` beyond the project finish, and at least one critical activity — all
  enforced by the Hypothesis property suite (`tests/test_properties.py`) over
  randomly generated networks of every relationship type and lag sign.
- Scheduling is deterministic, idempotent, and independent of input order.
- Dates are never stored on activities; `WorkdayCalendar` computes them on
  demand (the engine's maths stays in abstract working days, ADR-0012).

## Dependencies

- `schema` (for the `Activity` model). Nothing else.

## Usage

```python
from schema import Activity
from engine import CPMScheduler

acts = {a.id: a for a in [
    Activity("A", "Start", 2, ()),
    Activity("B", "Foundation", 4, ("A",)),
    Activity("C", "Structure", 6, ("B",)),
    Activity("D", "Electrical", 3, ("B",)),
    Activity("E", "Finish", 2, ("C", "D")),
]}
s = CPMScheduler(acts)
s.schedule()
print(s.project_duration())     # 14
print(s.get_critical_path())    # ['A', 'B', 'C', 'E']
```

## Testing

```bash
pytest packages/engine/tests
```
