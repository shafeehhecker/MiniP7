# Roadmap

> Category: **Explanation**. The delivery plan. Each phase produces exactly one
> reusable commons that later phases consume. For the packages themselves, see
> [the commons registry](architecture/commons.md).

Each phase has an objective, a single deliverable (the commons), a definition of
done, and a reusability contract — what downstream gets for free.

## Phase 0 — Repository & toolchain commons ✅
- **Deliverable:** the monorepo, CI, shared configs, commit conventions, ADR process.
- **Done when:** a trivial package can be added, tested, and released through CI.
- **Reuse:** every later package inherits CI, versioning, and conventions.
- **Status:** done. `.github/workflows/ci.yml` runs the test suites (3.11/3.12),
  enforces the dependency rule with import-linter, gates schema→TypeScript
  drift, and builds + deploys the docs site strictly.

## Phase 1 — Domain schema commons (`schema`) ✅
- **Deliverable:** the canonical model in Pydantic, generating TypeScript types.
- **Done when:** a model change regenerates both languages in one command and CI
  fails on drift.
- **Reuse:** every package and both languages share one definition.
- **Status:** done. `python tooling/codegen/generate_ts.py` regenerates
  `packages/client/src/models.ts`; CI fails on drift and type-checks the output
  with `tsc --strict` ([ADR-0010](adr/0010-typescript-codegen-tooling.md)).

## Phase 2 — Core engine commons (`engine`) ✅
- **Deliverable:** pure CPM extended for calendars and relationship types, plus EVM.
- **Done when:** it passes property-based tests and runs identically in tests, the
  CLI, and batch jobs.
- **Reuse:** the single source of scheduling truth for every interface.
- **Status:** done. All four relationship types (FS/SS/FF/SF) with lag
  ([ADR-0011](adr/0011-typed-relationships.md)), calendars mapping working days
  to real dates ([ADR-0012](adr/0012-calendars.md)), earned value
  ([ADR-0013](adr/0013-earned-value.md)), and level-of-effort spanning
  (completing ADR-0008). Guarded by a Hypothesis property-based suite that
  found and now permanently guards against a real float-hierarchy bug.

## Phase 3 — Services + persistence commons (`services`, `persistence`)
- **Deliverable:** storage-agnostic repositories and the orchestration layer.
- **Done when:** the same service tests pass against an in-memory repo and a real DB.
- **Reuse:** API and CLI drive identical business logic.

## Phase 4 — API contract + typed client commons (`client`)
- **Deliverable:** FastAPI server and a TypeScript client generated from its OpenAPI.
- **Done when:** a breaking API change fails the frontend build at compile time.
- **Reuse:** the frontend never hand-writes a fetch call or a response type.

## Phase 5 — UI commons (`ui`) ✅ (first cut)
- **Deliverable:** design tokens, primitives, wrapped Gantt + data grid, data hooks.
- **Done when:** a new view is assembled from primitives with zero raw styling.
- **Reuse:** every feature vertical is composition, not construction.
- **Status:** the React migration mentioned below as "an option" has happened.
  `apps/web` (React + TypeScript + Tailwind + Vite) now covers auth, project
  and activity CRUD, scheduling, an interactive Gantt drawing all four
  relationship types, and earned value — built from a small primitive set
  (`Button`/`Input`/`Select`/`Modal`/`Card`/`Table`/`Badge`/`Alert`) under a
  drafting-table design system ([ADR-0014](adr/0014-frontend-stack.md)). It
  consumes `packages/client` as a real npm-workspace dependency, so the
  frontend/backend type contract has the same drift protection as the rest of
  the commons. Deferred to Phase 6: drag-to-reschedule, calendar dates on the
  Gantt (the engine supports them — ADR-0012 — the endpoint doesn't expose
  them yet), baseline overlay, zoom, export. The zero-build static UI in
  `apps/api/static` remains in place as a lightweight fallback and has been
  brought current with Phase 2 (see below) — it is no longer stuck at Phase 1.

## Built since: core-job web UI

A zero-build web app (served by the API, no npm/build step) provides the core
job end to end: sign up / log in, a projects list, create projects, add /
edit / delete tasks through a form, run the schedule, and an interactive
Gantt. It originally only understood finish-to-start dependencies — a gap
against Phase 2 that sat open until now. It has since been updated to match
Phase 2 and Phase 5's EVM work: the task form builds typed relationships
(FS/SS/FF/SF with lag, matching ADR-0011) instead of a plain comma-separated
predecessor list; budget, actual cost, and percent-complete fields are on the
form; the task table shows cost columns and typed predecessor labels
(`D·SS+1d`); the Gantt draws all four relationship types, flagging
start-to-finish links in the critical-path color since they're the type most
often used by mistake; and a new Earned Value card calls the `/evm` endpoint
for BAC/PV/EV/AC/SV/CV/SPI/CPI/EAC/VAC at a chosen status day. Phase 5's
React app remains the primary UI for anyone running a Node toolchain; this
one is for anyone who isn't.

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
