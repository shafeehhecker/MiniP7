# ADR-0006: Self-hosted authentication (bcrypt + JWT)

- **Status:** Accepted
- **Date:** 2026-06-24
- **Deciders:** Core team

## Context

The multi-tenant authorization model (ADR-0005) is enforced, but identity was
passed via an `X-User-Id` header, which is insecure — anyone could claim any
identity. We need real authentication that yields a *verified* user identity.

## Options considered

### Option A — Managed identity provider (Clerk, Auth0, Supabase Auth)
- Pros: secure signup, social login, password reset, MFA out of the box.
- Cons: external dependency and cost; less control; data lives with a vendor.

### Option B — Self-hosted authentication
- Passwords hashed with bcrypt; login issues a signed, expiring JWT; a FastAPI
  dependency validates the token and yields the current user.
- Pros: full control; no external dependency; consistent with the project's
  "own and understand your internals" philosophy.
- Cons: we own the security-sensitive code (hashing, token handling, reset flows)
  and must follow the standard patterns carefully.

## Decision

Adopt Option B. The security primitives live in a single, isolated `packages/auth`
commons (the only place hashing and token signing happen), so the sensitive code
is auditable in one spot. The service layer registers and authenticates users; the
API replaces the header with a token-derived `current_user` dependency. The
authorization model from ADR-0005 is unchanged — it already takes a user id.

## Security decisions (recorded for audit)

- Passwords are hashed with **bcrypt** (per-password salt); plaintext is never
  stored, returned, or logged.
- `verify_password` is constant-time and never raises on malformed input.
- Tokens are **JWT (HS256)** carrying the user id (`sub`) and an expiry (`exp`);
  expired or tampered tokens are rejected with 401.
- The signing secret is read from the `MINIP7_SECRET` environment variable; the
  default is insecure and must be overridden in any real deployment.

## Consequences

- Unauthenticated requests to protected routes get 401; the header path is gone.
- We are responsible for future hardening: token refresh, password-reset email
  flows, rate-limiting login, and rotating the secret. These are tracked as
  follow-ups, not blockers.
- `MINIP7_SECRET` must be set (and kept secret) in production.
