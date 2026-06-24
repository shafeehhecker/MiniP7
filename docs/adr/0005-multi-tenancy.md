# ADR-0005: Multi-tenant model (organization → user → project)

- **Status:** Accepted
- **Date:** 2026-06-24
- **Deciders:** Core team
- **Supersedes:** —

## Context

The product's target user is a small business or startup running internal
projects. That means several people in one company share the same projects from
day one. The original model had a bare `Project` with no notion of who owns it or
who may see it. Retrofitting tenancy after data and code accumulate is expensive
and error-prone (every query must later be audited for leakage), so the boundary
is designed in now.

## Options considered

### Option A — Single-tenant, add sharing later
- Pros: simplest model now.
- Cons: every project query, endpoint, and UI must be reworked later to add
  scoping; high risk of cross-tenant data leaks introduced during the retrofit.

### Option B — Multi-tenant from the start
- An `Organization` owns projects. A `User` is identity only. A `Membership`
  joins user↔org and carries a `Role` (owner/admin/member/viewer). Every
  `Project` carries an `organization_id`. All project operations are scoped to an
  org and permission-checked in the service layer.
- Pros: data is always tenant-scoped; roles gate writes; matches the product's
  audience; the boundary cannot be forgotten because the repository requires an
  org id to list projects.
- Cons: slightly more model and service code up front.

## Decision

Adopt Option B. Tenancy and authorization live in the service layer (the
use-case boundary), not in the engine or schema — consistent with the dependency
rule. The schema gains `Organization`, `User`, `Membership`, and `Role`, and
`Project` gains `organization_id`.

## Consequences

- Cross-tenant access is structurally hard: listing projects requires an org id,
  and fetching a project by id verifies it belongs to the caller's org.
- Roles (owner/admin/member/viewer) gate actions; viewers are read-only.
- Identity *source* is still temporary (header-based) until authentication lands
  (ADR-0006); the authorization model, however, is already enforced and tested.
- A future Postgres adapter must preserve the `organization_id` scoping.
