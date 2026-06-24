# How the Critical Path Method works

> Category: **Explanation**. This page builds intuition for the algorithm the
> `engine` package implements. For term definitions see the
> [glossary](glossary.md); for the API see the
> [engine README](../../packages/engine/README.md).

The Critical Path Method (CPM) answers two questions about a network of dependent
activities: *how long will the project take?* and *which activities can't slip
without delaying it?* It does so with two sweeps over the network — a forward
pass and a backward pass — followed by a float calculation.

## The network

Activities are nodes; relationships are edges. Because an activity cannot start
before its predecessors are done, the network must be a **directed acyclic graph**
— a cycle would mean an activity depends on itself, which is meaningless. The
engine detects cycles and raises rather than looping forever (see
[ADR rationale in the engine tests](../../packages/engine/tests/test_scheduler.py)).

We process activities in **topological order** (every activity after all its
predecessors) using Kahn's algorithm. This guarantees that when we reach an
activity in the forward pass, all its predecessors are already computed.

## Worked example

Five activities. Durations in working days.

| ID | Name | Duration | Predecessors |
|----|------|----------|--------------|
| A | Start | 2 | — |
| B | Foundation | 4 | A |
| C | Structure | 6 | B |
| D | Electrical | 3 | B |
| E | Finish | 2 | C, D |

### Forward pass — compute ES and EF

Start at the beginning. An activity's early start is the latest early finish among
its predecessors; its early finish is `ES + duration`.

- **A**: no predecessors → ES = 0, EF = 0 + 2 = **2**
- **B**: after A → ES = 2, EF = 2 + 4 = **6**
- **C**: after B → ES = 6, EF = 6 + 6 = **12**
- **D**: after B → ES = 6, EF = 6 + 3 = **9**
- **E**: after C *and* D → ES = max(12, 9) = 12, EF = 12 + 2 = **14**

The project duration is the largest EF: **14 days**.

### Backward pass — compute LS and LF

Start at the end and work back. An activity's late finish is the earliest late
start among its successors; its late start is `LF − duration`. The final
activity's LF is set to the project duration.

- **E**: LF = 14, LS = 14 − 2 = **12**
- **D**: before E → LF = 12, LS = 12 − 3 = **9**
- **C**: before E → LF = 12, LS = 12 − 6 = **6**
- **B**: before C and D → LF = min(6, 9) = 6, LS = 6 − 4 = **2**
- **A**: before B → LF = 2, LS = 2 − 2 = **0**

### Float and the critical path

Total float is `LS − ES`. An activity with zero total float is critical.

| ID | ES | EF | LS | LF | TF | Critical? |
|----|----|----|----|----|----|-----------|
| A | 0 | 2 | 0 | 2 | 0 | ✅ |
| B | 2 | 6 | 2 | 6 | 0 | ✅ |
| C | 6 | 12 | 6 | 12 | 0 | ✅ |
| D | 6 | 9 | 9 | 12 | **3** | — |
| E | 12 | 14 | 12 | 14 | 0 | ✅ |

The critical path is **A → B → C → E**, total **14 days**. Activity D has 3 days
of total float: it can start as late as day 9 without delaying the project.

> Note: an earlier version of this project's documentation claimed D had a float
> of 5. That was wrong — the engine computes 3, and the worked example above shows
> why. This is exactly the kind of error that a documented, worked example and a
> locking unit test prevent from recurring.

### Free float

Free float is how far an activity can slip without delaying *any successor*:
`min(successor ES) − EF`. For D, its successor E starts at 12 and D finishes at 9,
so D's free float is `12 − 9 = 3`.

## Calendars change the arithmetic, not the logic

Everything above counts in abstract working days. A **calendar** maps those day
offsets onto real dates by skipping non-working time. With a Mon–Fri calendar, an
activity that starts five working days after a Monday finishes the following
Monday, not mid-weekend. The CPM logic is unchanged; only the day-to-date
translation differs. This is why the engine keeps scheduling and calendar mapping
as separate, composable steps.
EOF
echo "cpm.md written"
