# `client` — typed API client (TypeScript)

> Category: **Reference**. Produced in **Phase 4**. Generated types are
> **built**; the runtime API client is **planned**.

## Purpose

The TypeScript side of the contract. Today it holds `src/models.ts` — the
domain types generated from `packages/schema` (see
[ADR-0003](../../docs/adr/0003-schema-single-source-of-truth.md),
[ADR-0010](../../docs/adr/0010-typescript-codegen-tooling.md)). Phase 4 adds a
runtime client generated from the FastAPI OpenAPI spec, so the frontend never
hand-writes a fetch call or a response type.

## Stability

`experimental` — types track the schema (which is pre-1.0); the runtime client
does not exist yet.

## Public API

- `src/models.ts` — enums and interfaces for the entire schema public API.
  **Generated; never edit by hand.** Regenerate with
  `python tooling/codegen/generate_ts.py`
  ([how-to](../../docs/guides/regenerating-types.md)).

## Invariants

- `models.ts` is byte-identical to what the generator produces from the current
  schema — enforced by the CI drift gate.
- Compiles under `tsc --strict` — enforced in CI.

## Consumers

`apps/web` (Phase 5) depends on this package as `@minip7/client` via npm
workspaces — see the root `package.json` and
[apps/web/README.md](../../apps/web/README.md#where-the-types-come-from). It
imports these types directly rather than redeclaring them, so a schema change
that isn't reflected here fails the frontend's type-check, not just CI's
drift gate.

## Dependencies

`schema` (as its generation source). Nothing else.
