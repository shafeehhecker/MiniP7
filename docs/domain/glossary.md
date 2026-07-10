# Domain glossary

> Category: **Reference**. Every domain term is defined once, here. No other
> document redefines these — they link here instead. This is the project's shared
> language.

## Scheduling (CPM)

**Activity** — A unit of work with a duration and dependencies. The atom of a
schedule.

**Activity type** — The kind of an activity, which governs how it schedules:
**task** (ordinary work with a duration), **milestone** (a zero-duration marker
for a point in time), **level of effort** (sustained work whose span is driven by
other activities), and **summary** (a roll-up of the activities beneath a WBS
node). Task, milestone and level-of-effort are fully scheduled today (an LOE spans
the activities it supports — see [ADR-0011](../adr/0011-typed-relationships.md));
summary is modelled and scheduled as a task until the WBS lands
(see [ADR-0008](../adr/0008-activity-types.md)).

**Milestone** — A zero-duration activity marking a point in time, such as a
deliverable or a gate. A milestone always has `duration == 0`.

**Level of effort (LOE)** — An activity whose duration is determined by the
activities it supports rather than by its own estimate (e.g. project management
running for the life of a phase).

**Summary activity** — An activity that summarises the work of a WBS branch,
rolling up the dates of its children.

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
successors or the project finish: the tightest relationship slack toward any
successor, bounded by `project finish − EF`. Always `FF ≤ TF`
(see [ADR-0011](../adr/0011-typed-relationships.md)).

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

## Preferences & organization settings

**User preferences** — Per-user display settings that never change the computed
schedule: a colour **theme**, the **units** durations are shown in, and a **date
format**. Embedded in the user (see [ADR-0007](../adr/0007-user-preferences.md)).

**Units** — Whether a user sees durations in **days** or **hours** (an 8-hour
working day). The engine always computes in days; units are presentation only.

**Date format** — How calendar dates are rendered for a user (ISO, US, or EU).
Takes effect once the calendar maps day-offsets to real dates.

**Theme** — A user's colour preference: light, dark, or follow the system.

**Currency** — The ISO 4217 currency an organization's monetary values are
expressed in (code, symbol, name), set per organization. A display setting until
cost rollups exist (see [ADR-0009](../adr/0009-currency.md)).

## Calendars (see [ADR-0012](../adr/0012-calendars.md))

**Calendar** — The working-time definition: which weekdays count as working
days plus specific holiday dates. The engine always computes in working days;
a calendar and a project start date map those offsets onto real dates.

**Working day 0** — The first working date on or after the project start date.
An activity occupies working days `ES..EF−1`; a milestone occurs at day `ES`.

## Earned value (see [ADR-0013](../adr/0013-earned-value.md))

**BAC — Budget at completion** — The total budget: the sum of every activity's
budget.

**PV / BCWS — Planned value** — The budget that *should* have been consumed by
the status day, accruing linearly across each activity's scheduled span.

**EV / BCWP — Earned value** — The budgeted worth of work actually performed:
`budget × percent complete` per activity.

**AC / ACWP — Actual cost** — Money actually spent to date.

**SV / CV — Schedule / cost variance** — `SV = EV − PV` (negative = behind
schedule); `CV = EV − AC` (negative = over budget).

**SPI / CPI — Schedule / cost performance index** — `SPI = EV ÷ PV`,
`CPI = EV ÷ AC`. `None` when the denominator is zero — "no data yet" is never
"exactly on plan".

**EAC / ETC / VAC** — Forecasts assuming current cost performance continues:
estimate at completion `EAC = BAC ÷ CPI`, estimate to complete
`ETC = EAC − AC`, variance at completion `VAC = BAC − EAC`.
