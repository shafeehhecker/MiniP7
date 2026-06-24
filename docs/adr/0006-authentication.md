# ADR-0006: Authentication approach

- **Status:** Proposed
- **Date:** 2026-06-24
- **Deciders:** Core team (DECISION PENDING)

## Context

The multi-tenant authorization model (ADR-0005) is enforced, but identity is
currently passed via headers (X-User-Id), which is not secure. We need real
authentication that yields a verified user identity, which the API will use in
place of the headers.

## Options considered

### Option A — Managed identity provider (Clerk, Auth0, Supabase Auth, Cognito)
- Pros: secure signup, social login, password reset, MFA, and org invitations out
  of the box; fastest path to maturity; no home-grown crypto.
- Cons: external dependency and cost; vendor lock-in mitigated by verifying tokens
  behind our own `packages/auth` interface.

### Option B — Self-hosted OAuth2 + JWT in FastAPI
- Pros: no external dependency; full control.
- Cons: we own password storage, reset flows, and security hardening — more
  surface area to get wrong.

## Decision

PENDING. Recommendation: Option A for speed and security, isolated behind a
`packages/auth` commons so the rest of the app depends on our interface, not the
vendor. The API swaps header-based identity for token-derived identity; the
service layer is unchanged because it already takes a user id and org id.

## Consequences

To be recorded once decided.
