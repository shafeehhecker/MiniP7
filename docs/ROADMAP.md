# Roadmap

> Category: **Explanation**. The delivery plan. Each phase produces exactly one
> reusable commons that later phases consume. For the packages themselves, see
> [the commons registry](architecture/commons.md).

Each phase has an objective, a single deliverable (the commons), a definition of
done, and a reusability contract — what downstream gets for free.

## Phase 0 — Repository & toolchain commons
- **Deliverable:** the monorepo, CI, shared configs, commit conventions, ADR process.
- **Done when:** a trivial package can be added, tested, and released through CI.
- **Reuse:** every later package inherits CI, versioning, and conventions.

## Phase 1 — Domain schema commons (`schema`)
- **Deliverable:** the canonical model in Pydantic, generating TypeScript types.
- **Done when:** a model change regenerates both languages in one command and CI
  fails on drift.
- **Reuse:** every package and both languages share one definition.

## Phase 2 — Core engine commons (`engine`)
- **Deliverable:** pure CPM extended for calendars and relationship types, plus EVM.
- **Done when:** it passes property-based tests and runs identically in tests, the
  CLI, and batch jobs.
- **Reuse:** the single source of scheduling truth for every interface.

## Phase 3 — Services + persistence commons (`services`, `persistence`)
- **Deliverable:** storage-agnostic repositories and the orchestration layer.
- **Done when:** the same service tests pass against an in-memory repo and a real DB.
- **Reuse:** API and CLI drive identical business logic.

## Phase 4 — API contract + typed client commons (`client`)
- **Deliverable:** FastAPI server and a TypeScript client generated from its OpenAPI.
- **Done when:** a breaking API change fails the frontend build at compile time.
- **Reuse:** the frontend never hand-writes a fetch call or a response type.

## Phase 5 — UI commons (`ui`)
- **Deliverable:** design tokens, primitives, wrapped Gantt + data grid, data hooks.
- **Done when:** a new view is assembled from primitives with zero raw styling.
- **Reuse:** every feature vertical is composition, not construction.

## Built since: core-job web UI

A zero-build web app (served by the API) now provides the core job end to end:
sign up / log in, a projects list, create projects, add / edit / delete tasks
through a form, run the schedule, and an interactive Gantt with dependency
arrows. A React migration remains an option if the component ecosystem is
needed later; the zero-build approach avoids a Node toolchain for now.

## Built since: activity types, preferences, currency

Three feature increments landed on top of the commons without changing the
dependency graph (each is documented by an ADR):

- **Activity types** (task / milestone / level-of-effort / summary) — schema +
  engine + UI, with task and milestone fully scheduled
  ([ADR-0008](adr/0008-activity-types.md)).
- **User preferences** (theme / units / date format) — embedded in the user and
  applied in the UI ([ADR-0007](adr/0007-user-preferences.md)).
- **Organization currency** — an ISO 4217 setting per organization, ready for
  costs ([ADR-0009](adr/0009-currency.md)).

## Phases 6+ — Feature verticals
Schedule/Gantt, Resources & loading, Costs & EVM, Dashboard/Portfolio, then
Risks/Issues/Docs. These consume all the commons. When a vertical finds shared
logic, it pushes it *down* into a commons — never sideways into another vertical.
