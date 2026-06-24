# ADR-0002: Enforce the inward dependency rule

- **Status:** Accepted
- **Date:** 2026-06-24
- **Deciders:** Core team

## Context

Clean separation only survives if it is enforced. Architectures documented but
not checked erode within weeks as contributors take shortcuts under deadline.

## Options considered

### Option A — Convention only (documented, not enforced)
- Pros: zero tooling.
- Cons: erodes silently; violations found late, in review if at all.

### Option B — Enforced by lint/CI
- Pros: violations fail the build immediately, at the point of authorship.
- Cons: requires boundary configuration and occasional explicit exceptions.

## Decision

Enforce the dependency rule mechanically: `apps/` may import `packages/`;
`packages/` may import strictly lower `packages/`; nothing may import `apps/`; and
no feature vertical may import another. Implemented via import-boundary lint rules
(e.g. Nx module boundaries / import-linter for Python) wired into CI.

## Consequences

- The architecture cannot quietly degrade — a forbidden import is a failed build.
- Genuine exceptions require an explicit, reviewed allow-list entry, creating a
  visible audit trail of every deviation.
