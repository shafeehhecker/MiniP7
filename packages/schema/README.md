# `schema` — canonical domain model

> Category: **Reference**. The single source of truth for the domain. Every other
> package and both languages derive their types from here. Produced in **Phase 1**.

## Purpose

Defines the canonical model — Activity, Relationship, WBS node, Resource,
Assignment, Calendar, Baseline, Project — exactly once, in Pydantic. The JSON
Schema it exports is used to generate the TypeScript types in `packages/client`,
so Python and TypeScript can never disagree about the model (see
[ADR-0003](../../docs/adr/0003-schema-single-source-of-truth.md)).

## Stability

`experimental` — the model is still expanding (relationship types, costs, EVM
fields). Breaking changes are expected until `1.0.0`.

The TypeScript generation pipeline is **built**: `tooling/codegen/generate_ts.py`
emits `packages/client/src/models.ts` from this package's public API, and CI
fails on drift (see [ADR-0010](../../docs/adr/0010-typescript-codegen-tooling.md)
and the [how-to guide](../../docs/guides/regenerating-types.md)).

## Public API

- `Activity` — a unit of work with duration, predecessors, a `type`
  (`ActivityType`), and computed CPM fields.
- `ActivityType` — `task | milestone | level_of_effort | summary`
  (see [ADR-0008](../../docs/adr/0008-activity-types.md)).
- `ActivityStatus`, `Relationship`, `RelationshipType` — status and (modelled)
  typed dependencies.
- `Project`, `Organization`, `Membership`, `Role` — multi-tenant containers and
  roles.
- `User`, `UserPreferences`, `UnitSystem`, `DateFormat`, `Theme` — identity plus
  per-user display settings (see [ADR-0007](../../docs/adr/0007-user-preferences.md)).
- `Currency`, `COMMON_CURRENCIES` — organization currency value object and a
  starter catalogue (see [ADR-0009](../../docs/adr/0009-currency.md)).
- `SignupRequest`, `LoginRequest`, `AuthResponse` — auth payloads.
- (planned) `WBSNode`, `Resource`, `Assignment`, `Calendar`, `Baseline`.

## Invariants

- Models validate on construction; an invalid model cannot exist. In particular,
  a `MILESTONE` activity must have `duration == 0`, and a `Currency` code must be
  three letters (ISO 4217).
- Models are serialisable to and from JSON via Pydantic; new fields carry
  defaults, so older stored records load without migration.
- The schema imports nothing from other packages — it is the bottom of the graph.

## Dependencies

None. This is the root of the dependency graph.

## Usage

```python
from schema import Activity

a = Activity(id="A", name="Start", duration=2)
print(a.model_dump_json())
```

## Testing

```bash
# from the repo root, once tooling is wired:
nx test schema        # or: pytest packages/schema/tests
```
