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

`experimental`. The CPM core is stable and well-tested; calendar support and
relationship types beyond finish-to-start are in progress.

## Public API

- `CPMScheduler(activities)` — construct with a `{id: Activity}` mapping.
- `.schedule()` — run forward + backward passes, populate CPM fields in place.
- `.get_critical_path()` — list of activity ids with zero total float.
- `.project_duration()` — the largest early finish.
- `SchedulerError` — raised on cycles or unknown predecessors.

## Invariants

- The scheduler never mutates the *set* of activities it is given (only fills
  their computed CPM fields).
- A network with a cycle raises `SchedulerError` rather than looping.
- An unknown predecessor reference raises `SchedulerError`.

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
