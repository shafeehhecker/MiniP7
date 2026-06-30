# ADR-0007: User preferences embedded in the user

- **Status:** Accepted
- **Date:** 2026-06-27
- **Deciders:** Core team
- **Supersedes:** —
- **Superseded by:** —

## Context

Users want control over how the app presents information: a colour theme, the
unit durations are shown in (days vs hours), and a date format. These are
*display* concerns — they must never change the computed schedule, which the
engine always produces in abstract working days (see
[cpm.md](../domain/cpm.md)). We need somewhere to store a handful of per-user
settings, and a rule for what they are allowed to affect.

## Options considered

### Option A — A separate `preferences` table / repository
- Pros: clean separation; room to grow into many settings.
- Cons: a new repository protocol, a new table, and a new join for every read of
  a user — heavy for three fields that always travel with identity.

### Option B — Embed preferences in the `User` model
- A `UserPreferences` value object is a field on `User`; it serialises with the
  user and is saved through the existing `save_user`.
- Pros: no new persistence surface; preferences load exactly when the user does;
  defaults fill in for existing users with no migration.
- Cons: preferences are coupled to the user record (acceptable — they are
  per-user by definition).

## Decision

Adopt Option B. `UserPreferences` (units, date format, theme) is embedded in
`User` with safe defaults. A member may set their own preferences without any
role check, because preferences are presentation-only and cannot affect another
user or the schedule. The API exposes `GET`/`PUT /api/me/preferences`.

## Consequences

- Existing stored users load unchanged: missing preferences fall back to the
  model defaults, so no data migration is required.
- Preferences are strictly presentational. The engine and services never read
  them; only the UI does. This keeps the computational core pure.
- `date_format` has no visible effect until the calendar feature maps day
  offsets to real dates; it is stored now so the choice is preserved.
