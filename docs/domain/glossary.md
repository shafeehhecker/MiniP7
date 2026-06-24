# Domain glossary

> Category: **Reference**. Every domain term is defined once, here. No other
> document redefines these — they link here instead. This is the project's shared
> language.

## Scheduling (CPM)

**Activity** — A unit of work with a duration and dependencies. The atom of a
schedule.

**Duration** — How long an activity takes, in working days. May be zero (a
milestone).

**Predecessor / Successor** — If B depends on A, then A is a predecessor of B and
B is a successor of A.

**Relationship** — A typed dependency between two activities, with an optional
lag. Four types: **FS** (finish-to-start), **SS** (start-to-start), **FF**
(finish-to-finish), **SF** (start-to-finish). FS is the default and by far the
most common.

**Lag** — A delay added to a relationship (e.g. "B starts 2 days after A finishes"
is FS + 2 lag). Negative lag is a *lead*.

**ES / EF — Early Start / Early Finish** — The earliest an activity can start and
finish, computed in the forward pass. `EF = ES + Duration`.

**LS / LF — Late Start / Late Finish** — The latest an activity can start and
finish without delaying the project, computed in the backward pass.
`LS = LF − Duration`.

**Total float (TF)** — Slack: how long an activity can slip without delaying the
project. `TF = LS − ES`.

**Free float (FF)** — How long an activity can slip without delaying *any* of its
successors. `FF = min(successor ES) − EF`.

**Critical path** — The longest path through the network; the chain of activities
with zero total float. Delaying any of them delays the whole project.

**Forward pass** — The left-to-right sweep computing ES/EF from the start.

**Backward pass** — The right-to-left sweep computing LS/LF from the end.

**Data date** — The "as-of" date dividing actuals (past) from plan (future). Used
when a schedule is in progress.

**Calendar** — The definition of working vs non-working time (e.g. Mon–Fri skips
weekends). Durations are measured in *working* days against a calendar.

**WBS — Work Breakdown Structure** — The hierarchical decomposition of the project
into nested groups of work. Activities live at the leaves.

**Baseline** — A saved snapshot of the schedule used to compare plan vs actual.

## Resources

**Resource** — Labour or equipment that performs work (e.g. "Electrical Team",
"Tower Crane 1").

**Assignment** — A link between a resource and an activity, with an allocation
(units or percentage).

**Resource loading** — Total demand on a resource over time, often shown as a
heatmap or histogram. Over-allocation is when demand exceeds capacity.

**Levelling** — Adjusting the schedule to remove resource over-allocation.

## Earned Value Management (EVM)

**PV / BCWS — Planned Value** — The budgeted cost of work *scheduled* by the data
date.

**EV / BCWP — Earned Value** — The budgeted cost of work *actually performed* by
the data date.

**AC / ACWP — Actual Cost** — The real cost of the work performed.

**SV — Schedule Variance** — `EV − PV`. Negative means behind schedule.

**CV — Cost Variance** — `EV − AC`. Negative means over budget.

**SPI — Schedule Performance Index** — `EV / PV`. Below 1.0 means behind schedule.

**CPI — Cost Performance Index** — `EV / AC`. Below 1.0 means over budget.

**BAC — Budget at Completion** — The total planned budget.

**EAC — Estimate at Completion** — The forecast total cost, commonly `BAC / CPI`.
