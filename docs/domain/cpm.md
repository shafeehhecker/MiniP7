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
## Typed relationships and lag

Everything above used the default relationship: **finish-to-start** — "B starts
after A finishes". Real schedules need three more (see
[ADR-0011](../adr/0011-typed-relationships.md) for the full semantics table):

- **SS, start-to-start** — "paint starts 2 days after plastering starts":
  `ES(B) ≥ ES(A) + 2`.
- **FF, finish-to-finish** — "commissioning finishes when installation
  finishes": `EF(B) ≥ EF(A)`.
- **SF, start-to-finish** — rare: the predecessor's *start* releases the
  successor's *finish* (classic example: the old shift may only end once the
  new shift has started).

A **lag** delays the constraint; a **negative lag** (a *lead*) overlaps it:
FS with lag −2 lets B begin during A's final two days.

### Worked example

A is 5 days. B (3 days) may start 2 days after A starts — SS with lag 2.

- Forward: `ES(B) = ES(A) + 2 = 2`, `EF(B) = 5`. Project finish: **5**.
- Backward: B is terminal, so `LF(B) = 5`, `LS(B) = 2`. A's start constrains
  B's start, so `LS(A) ≤ LS(B) − 2 = 0` — A cannot slip at all.

Both activities are critical, and note *why* A is critical: not because its
finish drives anything, but because its **start** does. Start-driven
criticality only exists once SS/SF relationships do; FS-only intuition says
"critical = my finish matters", which is no longer the whole story.

### The float hierarchy survived a real bug

Free float must never exceed total float. The Hypothesis property suite found
a network — a zero-duration activity with an FS *lead* into a successor
clamped at day 0 — where the naive per-relationship slack broke that
hierarchy. The fix (free float is also bounded by the slack to the project
finish, for every activity) is recorded in ADR-0011, and the property test
that caught it now guards the invariant permanently. This is exactly the
role of the property suite: it is the engine's specification, expressed as
invariants no network may violate.

## From working days to dates

The passes above never mention a date — deliberately
([ADR-0012](../adr/0012-calendars.md)). A project `start_date` plus a
`Calendar` (working weekdays and holidays) map working-day offsets to real
dates at the edge: day 0 is the first working date on or after the start,
an activity's finish date is the date of day `EF − 1`, and a milestone
occurs at day `ES`. The maths stays pure integers; the dates are a view.

## Measuring progress: earned value

Once activities carry a `budget`, `percent_complete` and `actual_cost`, the
engine can answer "are we on plan?" quantitatively — planned value, earned
value, actual cost, and the SPI/CPI indices and EAC forecast derived from
them. The definitions live in the [glossary](glossary.md) and the decisions
in [ADR-0013](../adr/0013-earned-value.md).
