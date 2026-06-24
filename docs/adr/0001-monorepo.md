# ADR-0001: Use a single polyglot monorepo

- **Status:** Accepted
- **Date:** 2026-06-24
- **Deciders:** Core team

## Context

The product spans two languages: Python (engine, services, API, CLI) and
TypeScript (client, UI, web). All of them must agree on one domain model. The
biggest failure mode in projects like this is *contract drift* — the frontend and
backend silently diverging on what a field means.

## Options considered

### Option A — Polyrepo (one repository per package)
- Pros: independent histories; smaller clones.
- Cons: cross-cutting changes span many PRs across many repos; the shared schema
  can drift between repos; no single CI can validate a change end-to-end.

### Option B — Monorepo (all packages and apps in one repository)
- Pros: a schema change and all its consumers update in one atomic PR; one CI
  validates the whole graph; shared tooling and conventions; trivial local
  cross-package development.
- Cons: requires a monorepo-aware task runner to avoid rebuilding everything;
  larger single repository.

## Decision

Use a single polyglot monorepo with a `packages/` (commons) and `apps/`
(interfaces) split, managed by a monorepo task runner that executes
*affected-only* builds and tests.

## Consequences

- Contract drift becomes structurally impossible: the schema and its consumers
  live and change together.
- We take on a dependency on the task runner (Nx or pnpm+Turborepo with uv for
  Python) and must configure affected-graph builds so CI stays fast.
- The `packages/` vs `apps/` boundary becomes load-bearing and is enforced by a
  lint rule (see ADR-0002).
