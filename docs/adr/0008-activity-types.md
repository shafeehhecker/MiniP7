# ADR-0008: Activity types (task, milestone, level-of-effort, summary)

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Core team
- **Supersedes:** —
- **Superseded by:** —

## Context

Real schedules distinguish *kinds* of activity. A task consumes working days; a
milestone marks a point in time with no duration; a level-of-effort (LOE)
activity is sustained work whose span is driven by other activities; a summary
rolls up the activities beneath a WBS node. Until now every activity was an
untyped task, with a zero-duration task standing in informally for a milestone.
We want an explicit taxonomy without overreaching into behaviour the rest of the
system cannot yet support faithfully.

## Options considered

### Option A — Implement all four types' scheduling behaviour now
- Pros: full fidelity immediately.
- Cons: LOE needs typed *successor* relationships (we only model finish-to-start
  predecessors today), and summary needs the WBS hierarchy — neither exists. We
  would be shipping a guessed algorithm, which contradicts the project's bar for
  a correct, tested engine (cf. the float fix in [cpm.md](../domain/cpm.md)).

### Option B — Model the taxonomy; fully schedule only what we can verify
- Add an `ActivityType` enum and an `Activity.type` field. Enforce the milestone
  invariant (`duration == 0`) in the schema. Schedule `TASK` and `MILESTONE`
  fully and correctly; accept `LEVEL_OF_EFFORT` and `SUMMARY` and schedule them
  as tasks for now, with their special behaviour explicitly deferred.
- Pros: honest and incremental; the data model is ready, and downstream UIs can
  show the type today; no incorrect maths ship.
- Cons: two of the four types are not yet "special".

## Decision

Adopt Option B. `ActivityType` is `task | milestone | level_of_effort | summary`,
defaulting to `task`. A milestone must have `duration == 0`, enforced at
construction so an inconsistent milestone cannot exist. The engine schedules
tasks and milestones correctly (a milestone is simply a zero-duration task) and
schedules LOE and summary as tasks for now, never rejecting them.

## Consequences

- The schema and API carry `type` immediately; the UI can mark milestones and
  filter by type.
- LOE gains its span-from-relationships behaviour only once typed relationships
  land; summary gains its roll-up only once the WBS lands. Both are tracked as
  follow-ups, not blockers, and this ADR records why they are deferred.
- Existing stored activities load as `task` (the default), so no migration is
  required.
