# ADR-0013: Earned value — linear planned value, percent-complete earned value

- **Status:** Accepted
- **Date:** 2026-07-10
- **Deciders:** Core team

## Context

Earned value management answers "are we on schedule and on budget, and where
will we land?" with three time series — planned value (PV/BCWS), earned value
(EV/BCWP) and actual cost (AC/ACWP) — and ratios derived from them. ADR-0009
prepared the currency; the engine's typed-relationship work (ADR-0011) gives
every activity a verified span. What remained was choosing the accrual and
progress models.

## Decision

- **Inputs on the activity:** `budget` (its share of the budget at completion)
  and `actual_cost` (spend to date), alongside the existing
  `percent_complete`. All costs are in the organization's currency (ADR-0009).
- **PV accrues linearly** across the activity's scheduled span `ES..EF`. A
  zero-duration activity (milestone) earns its full value at its day. Linear
  accrual is the industry default and needs no extra modelling; S-curves or
  weighted steps can be added later per-activity without changing the metric
  definitions.
- **EV is `budget × percent_complete`** — the percent-complete technique.
  Physical-progress and 0/100 or 50/50 milestone techniques are future options
  expressible through how `percent_complete` is set, not new engine code.
- **Ratios are `None` when undefined, never 0 or ∞.** SPI with nothing planned,
  CPI with nothing spent, EAC with a zero CPI: all `None`, so "no data yet" can
  never masquerade as "exactly on plan". The generated TypeScript carries the
  same nullability.
- **Formulas:** SV = EV−PV, CV = EV−AC, SPI = EV/PV, CPI = EV/AC,
  EAC = BAC/CPI, ETC = EAC−AC, VAC = BAC−EAC. Computed by
  `engine.evm.compute_evm(activities, as_of_day)` returning a schema
  `EVMResult`, so the API can serve it and the TypeScript types already exist.

## Consequences

- The engine remains pure: EVM is a function of scheduled activities and a
  status day. The property suite asserts PV/EV never exceed BAC, the variance
  identities hold, and PV is monotonic in time.
- Cost *rollups by resource* and rate-based budgets (hours × rate) belong to
  the resources vertical (Phase 7); this ADR deliberately models activity-level
  money only.
- `EAC = BAC/CPI` is the standard "current cost performance continues"
  forecast. Alternative EAC formulas (schedule-adjusted, management estimate)
  can be added as variants without breaking this one.
