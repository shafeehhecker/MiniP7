# `auth` — password hashing + JWT (Milestone 1 commons)

> Category: **Reference**. The single, auditable home for security-sensitive auth
> primitives. Self-hosted (ADR-0006). Pure functions, no framework, no config.

## Purpose
Hash and verify passwords (bcrypt), and create/decode signed expiring JWTs. The
service layer uses these to register and authenticate users; the API uses token
decode to derive the current user on every protected route.

## Public API
- `hash_password(plaintext) -> str`
- `verify_password(plaintext, hashed) -> bool`
- `create_access_token(user_id, secret, expires_minutes=1440) -> str`
- `decode_access_token(token, secret) -> str`  (returns user id, raises `TokenError`)

## Invariants
- Plaintext passwords are never stored, returned, or logged.
- `verify_password` is constant-time (bcrypt) and never raises on bad input.
- Tokens expire; expired or tampered tokens raise `TokenError`.

## Dependencies
`bcrypt`, `pyjwt`. No internal packages — this is a leaf commons.

## Testing
```bash
pytest packages/auth/tests
```
nill
