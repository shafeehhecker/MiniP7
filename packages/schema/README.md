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

## Public API

- `Activity` — a unit of work with duration, predecessors, and computed CPM fields.
- (planned) `Relationship`, `WBSNode`, `Resource`, `Assignment`, `Calendar`,
  `Baseline`, `Project`.

## Invariants

- Models validate on construction; an invalid model cannot exist.
- Models are serialisable to and from plain dicts (`to_dict` / `from_dict`).
- The schema imports nothing from other packages — it is the bottom of the graph.

## Dependencies

None. This is the root of the dependency graph.

## Usage

```python
from schema import Activity

a = Activity("A", "Start", duration=2, predecessors=())
print(a.to_dict())
```

## Testing

```bash
# from the repo root, once tooling is wired:
nx test schema        # or: pytest packages/schema/tests
```
