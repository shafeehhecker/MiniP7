# ADR-0014: Frontend stack — React, a real commons workspace, and a drafting-table design system

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Core team

## Context

Phase 5 needed a UI that could show off what Phase 2–4 actually built: typed
relationships with lag, not just finish-to-start; earned value, not just a
task list. Three separate decisions were needed — a framework, how the
frontend consumes the schema commons, and a visual language — and all three
follow directly from decisions already on record.

## Decision 1: React + TypeScript + Tailwind + Vite

FastAPI already serves a zero-build static UI (`apps/api/static`); Phase 5
doesn't replace that ethos everywhere, it adds a proper app where the
project's complexity — typed relationships, an interactive Gantt, earned
value — outgrows what hand-written HTML/JS can hold. React was chosen over
Vue or Svelte for the same reason `packages/schema` chose Pydantic over a
hand-rolled validator in ADR-0001: the largest ecosystem, the least
bespoke-tooling risk for a project that already carries a lot of its own
infrastructure (a hand-written codegen tool, a hand-rolled CPM engine).
Tailwind was chosen over a component library (Chakra, MUI) because this
project has a genuine design point of view (see Decision 3) that a
component library would fight rather than support. Vite over Next.js/CRA:
this is a single-page app talking to a separate API, not a
server-rendered site — Vite is the leaner tool for that shape.

## Decision 2: `packages/client` becomes a real commons dependency, not a copy

**The alternative considered:** hand-write TypeScript interfaces in
`apps/web` matching what the API returns. This is what most Phase 5-stage
projects actually do, and it is precisely the failure mode ADR-0003
(schema as single source of truth) and ADR-0010 (codegen) exist to prevent —
except one layer further out, in the UI that end users actually touch.

**The decision:** a root `package.json` with npm workspaces
(`packages/client`, `apps/web`) makes `@minip7/client` — which **is**
`packages/client/src/models.ts`, generated from the Pydantic schema — an
installable dependency of the UI, the same way `engine` is an installable
dependency of `services` on the Python side. `apps/web` imports
`Activity`, `EVMResult`, `RelationshipType` and everything else directly:

```ts
import type { Activity, EVMResult } from "@minip7/client";
```

This is the "commons" strategy applied one layer further than it has been
before. The dependency graph gains a JS-side inward edge that mirrors the
Python one:

```
apps/web  ──depends on──>  packages/client  ──generated from──>  packages/schema
```

**Consequence, already caught once:** `AuthResponse` in the generated types
is a flat shape (`access_token`, `user_id`, `email`, `organization_id`), not
the nested `{ token, user }` a hand-written type would have guessed at. The
first draft of `AuthContext` assumed the nested shape and `tsc -b` refused to
compile it. That failure is exactly what this decision buys: a
frontend/backend shape mismatch became a build error caught before commit,
not a runtime bug found by a user. No test was written to catch this
specifically — the type system was the test.

## Decision 3: A drafting-table design system, not a generic SaaS palette

CPM scheduling — critical path, float, milestones — comes from construction
and civil engineering, not from software. The UI leans into that instead of
defaulting to a rounded-corners, soft-shadow consumer palette:

- **Color:** blueprint navy (`ink`) for chrome, graph-paper blue-white
  (`paper`) for the canvas, construction-safety orange (`hazard`) for the
  critical path, engineering "go" green (`slack`) for on-track metrics.
  Hazard-orange over a generic red: it's the color the domain itself already
  uses for "pay attention here."
- **Type:** Space Grotesk (display) + IBM Plex Sans (body) + IBM Plex Mono
  for every number — durations, IDs, ES/EF, floats, money. A scheduling tool
  is a numbers tool; the numbers should look like data, not like prose.
  IBM Plex was designed for technical documentation, which is what a CPM
  network essentially is.
- **Layout:** hairline (1px) borders, 2px corner radius, a literal graph-paper
  grid behind the canvas. Sharp, not soft — a drafting table, not a dashboard.
- **The Gantt specifically:** hand-built SVG (`components/gantt/Gantt.tsx`),
  not a third-party chart library. A generic Gantt library draws
  finish-to-start arrows and stops there; ours draws all four relationship
  types from ADR-0011 as right-angle drafting connectors, which is the one
  piece of the UI that actually exercises the engine's Phase 2 work. Building
  it was the only way to show typed relationships correctly — buying it would
  have flattened the network back down to FS-only, silently discarding what
  Phase 2 built.

## Consequences

- The frontend/backend contract has the same drift protection the
  Python/TypeScript contract has always had, extended one hop further.
- `apps/web` has zero hand-duplicated model types; every shape it works with
  traces back to `packages/schema/src/schema/models.py`.
- The Gantt currently plots working-day offsets, not calendar dates —
  `WorkdayCalendar` (ADR-0012) exists but isn't exposed over HTTP yet. Small,
  deliberate, and recorded here rather than silently deferred: Phase 6 wires
  one endpoint field and one formatter change, not new engine work.
- The design system is a real constraint, not decoration: new components
  pull colors from the `ink`/`paper`/`hazard`/`slack`/`steel` Tailwind tokens,
  never raw hex, so the drafting-table language stays consistent as the UI
  grows through Phase 6 and 7.
