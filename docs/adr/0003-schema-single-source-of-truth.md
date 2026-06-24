# ADR-0003: One schema, generated into every language

- **Status:** Accepted
- **Date:** 2026-06-24
- **Deciders:** Core team

## Context

Python and TypeScript both need the domain model. Hand-maintaining two copies
guarantees they drift. First principle #2: the model is the contract, so there
must be exactly one definition.

## Options considered

### Option A — Define types twice (once per language), keep in sync by review
- Cons: drifts; reviewers miss subtle mismatches; the bug surfaces at runtime.

### Option B — Define once, generate the rest
- Define the model once in Pydantic; export JSON Schema / OpenAPI; generate the
  TypeScript types from it. CI fails if generated types are stale.
- Cons: a generation step in the build; tooling to maintain.

## Decision

Define the canonical model once in Pydantic inside `packages/schema`. Generate
TypeScript types from its JSON Schema. A CI check regenerates and diffs; any drift
fails the build.

## Consequences

- The frontend and backend cannot disagree about the model — it is mechanically
  impossible to merge a mismatch.
- Changing a field is a single edit that propagates to both languages.
- We accept a code-generation step and must keep the generator pinned and
  reproducible.
