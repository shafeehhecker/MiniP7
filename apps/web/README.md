# `apps/web` — the Mini-P7 UI

**Stability:** `experimental` (Phase 5, first cut). Covers auth, project/activity
CRUD, scheduling, the Gantt, and earned value. Drag-to-reschedule, baselines,
and zoom are Phase 6 (see [ADR-0014](../../docs/adr/0014-frontend-stack.md)).

React 18 + TypeScript + Tailwind, built with Vite. Talks to `apps/api` over
HTTP using the exact types `packages/schema` generates — see "Where the
types come from" below.

## Setup

```bash
# from the repo root — installs apps/web AND packages/client together
npm install

# run the API in one terminal (see apps/api/README.md)
./run.sh   # or run.bat on Windows

# run the UI in another terminal
npm run dev --workspace apps/web
```

Open `http://localhost:5173`. The dev server proxies `/api/*` to
`http://localhost:8000` (the FastAPI default); override with
`MINIP7_API_URL` if your backend runs elsewhere.

## Where the types come from

This app never hand-writes a type for anything the API returns. It imports
`@minip7/client`, an npm workspace package that **is**
`packages/client/src/models.ts` — the file `tooling/codegen/generate_ts.py`
generates from the Pydantic schema (ADR-0003). If the backend adds a field,
`npm run build` here won't type-check until the frontend accounts for it.
That's deliberate: it's the same drift gate CI already runs for the schema,
extended one layer further into the UI.

```ts
import type { Activity, EVMResult } from "@minip7/client";
```

Never edit `packages/client/src/models.ts` by hand — see its own README.

## Structure

```
src/
  context/     AuthContext — session state (token + current user)
  hooks/       SWR-backed data hooks (useProjects, useProject, useEvm, ...)
  lib/         api.ts (typed fetch client), formatters.ts
  components/
    common/    Button, Input, Select, Modal, Card, Table, Badge, Alert, Spinner
    layout/    Header, MainLayout
    gantt/     Gantt.tsx — the blueprint-style schedule chart
    forms/     ActivityModal
  pages/       one file per route
```

## Design system

See [ADR-0014](../../docs/adr/0014-frontend-stack.md) for the reasoning.
Short version: this is a drafting-table tool, not a marketing site — graph-paper
grid, hazard-orange for the critical path, IBM Plex Mono for every number
(durations, dates, floats). Tokens live in `tailwind.config.js`; components
pull from `ink` / `paper` / `hazard` / `slack` / `steel`, never raw hex.

## The Gantt

`components/gantt/Gantt.tsx` is hand-built SVG, not a third-party chart
library. It draws all four relationship types from ADR-0011 — FS, SS, FF, SF —
as right-angle drafting connectors, not just finish-to-start arrows. This is
the piece that actually exercises Phase 2's engine work; a generic Gantt
library would have flattened everything back down to FS.

It currently plots on a working-day axis (`ES`/`EF` as given by the API), not
calendar dates — `WorkdayCalendar` (ADR-0012) exists in the engine but isn't
exposed over HTTP yet. That's a small, contained Phase 6 addition: one new
endpoint field, one formatter change here.

## What's deliberately deferred to Phase 6

- Drag-to-reschedule on the Gantt
- Calendar dates instead of working-day offsets
- Baseline overlay, zoom levels, image/PDF export
- Resource capacity view (waits on Phase 7's resource model)

## Scripts

| Command | Does |
|---|---|
| `npm run dev --workspace apps/web` | Vite dev server with API proxy |
| `npm run build --workspace apps/web` | Type-check (`tsc -b`) then production build to `dist/` |
| `npm run typecheck --workspace apps/web` | Type-check only, no build |
| `npm run preview --workspace apps/web` | Serve the production build locally |
