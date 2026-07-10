# ADR-0012: Calendars — the engine stays in working days

- **Status:** Accepted
- **Date:** 2026-07-10
- **Deciders:** Core team

## Context

The engine computes in abstract working days (day 0, day 1, …), but people plan
against real dates: "the structure finishes Friday the 14th", not "on day 12".
We need weekends, holidays, and non-Western working weeks (e.g. Sunday–Thursday)
without complicating the scheduling maths.

## Options considered

### Option A — Teach the scheduler about dates
Run the forward/backward passes directly over calendar dates.
- Pros: one representation everywhere.
- Cons: every pass, float and lag calculation acquires calendar arithmetic;
  the property-based suite would have to reason about weekends; undated
  projects (all our existing data) need a fake date. The pure, integer core —
  the thing that makes the engine easy to verify — is lost.

### Option B — Keep the engine abstract; map to dates at the edge
The scheduler stays exactly as it is. A `Calendar` (working weekdays +
holiday dates) plus a project `start_date` feed a separate mapping layer,
`engine.calendar.WorkdayCalendar`, which resolves working-day offsets to real
dates on demand.
- Pros: the verified integer core is untouched; dates are a pure presentation,
  never stored on the activity; undated projects remain valid (no start date →
  no dates shown); per-project calendars are trivial.
- Cons: two representations exist; UIs must call the mapper.

## Decision

Option B. `Calendar` and `Project.start_date` live in the schema (defaults:
Monday–Friday, no holidays, undated), and the mapping lives in the engine so
every interface — API, CLI, tests — maps identically. Conventions, fixed here:
working day 0 is the first working date **on or after** the start date; an
activity occupies working days `ES..EF-1`, so its finish date is the date of
day `EF-1`; a milestone (`ES == EF`) occurs at day `ES`, start and finish
coinciding.

## Consequences

- Existing stored projects load unchanged (defaults cover both new fields).
- `UserPreferences.date_format` (ADR-0007) becomes fully meaningful: the UI can
  render the mapped dates in the user's chosen format.
- Per-*resource* calendars (different teams, different weeks) are a future
  extension: the mapper takes any `Calendar`, so the design already permits it.
- Lags are in working days, consistent with durations. Calendar-day lags (e.g.
  "concrete cures for 3 elapsed days") are out of scope and would need a lag
  unit on the relationship.
