# ADR-0010: Pure-Python TypeScript generator, committed output

- **Status:** Accepted
- **Date:** 2026-07-10
- **Deciders:** Core team

## Context

ADR-0003 decided the model is defined once in Pydantic and the TypeScript types
are generated from it, with CI failing on drift. It left the *mechanism* open.
Two questions remained: which generator, and whether the generated file is
committed or built on demand.

## Options considered

### Option A — Node-based generator (`json-schema-to-typescript` or similar)
- Pros: mature ecosystem, handles exotic JSON Schema.
- Cons: adds a Node toolchain to a repo that deliberately runs zero-build
  (contributors currently need only Python); an extra lockfile to maintain;
  output style is not under our control.

### Option B — Small pure-Python generator in `tooling/codegen`
- Introspects the schema package's `__all__` directly (enums → TS string enums,
  models → interfaces, defaults → optional fields). ~150 lines, deterministic.
- Pros: no Node required to contribute; the generator is code we own, versioned
  with the schema it reads; byte-identical output makes the drift check a plain
  file diff.
- Cons: we maintain the type mapping; it intentionally supports only the
  constructs the schema actually uses and fails loudly on anything else.

### Committed vs generated-on-demand output
Committing `packages/client/src/models.ts` means consumers (and reviewers) see
type changes in the diff, and no generation step is needed to build the
frontend. The cost — the file can go stale — is exactly what the CI drift gate
eliminates.

## Decision

Option B, with committed output. `tooling/codegen/generate_ts.py` generates
`packages/client/src/models.ts`. CI regenerates and diffs (`--check`), then
compiles the result with `tsc --strict`. Any drift or type error fails the
build.

## Consequences

- Phase 1's definition of done is met: one command regenerates, CI fails on
  drift, and reviewers see both sides of every model change in one diff.
- The generator must grow alongside the schema; an unmappable annotation is a
  loud generation-time error, never silently wrong TypeScript.
- If the schema outgrows the small generator, superseding this ADR with a
  Node-based one is a contained change: the output file and drift gate stay.
