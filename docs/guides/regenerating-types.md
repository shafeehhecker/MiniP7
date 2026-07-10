# How to change the schema and regenerate the TypeScript types

> Category: **How-to guide**. Task-oriented; assumes you know why the schema is
> the single source of truth ([ADR-0003](../adr/0003-schema-single-source-of-truth.md),
> [ADR-0010](../adr/0010-typescript-codegen-tooling.md)).

The domain model lives once, in `packages/schema/src/schema/models.py`. The
TypeScript types in `packages/client/src/models.ts` are **generated** from it —
never edit that file by hand.

## Steps

1. Edit the Pydantic models in `packages/schema/src/schema/models.py`.
   Export anything new from `packages/schema/src/schema/__init__.py` — the
   generator emits exactly the public API (`__all__`).

2. Regenerate:

   ```bash
   python tooling/codegen/generate_ts.py
   ```

3. Commit **both** files in the same change. Reviewers see the Python and
   TypeScript sides of the model change in one diff.

4. Complete the documentation Definition of Done: update the schema
   `README.md` public API list, docstrings, and the glossary for any new term.

## How drift is caught

CI runs `generate_ts.py --check`, which regenerates in memory and fails if the
committed file differs, then compiles the result with `tsc --strict`. A schema
change that forgets step 2 cannot merge.

## If generation fails

The generator supports the constructs the schema uses today (primitives,
enums, nested models, lists, dicts, unions/optionals). An annotation it cannot
map is a deliberate hard error — extend `_ts_type()` in
`tooling/codegen/generate_ts.py` in the same PR, with the mapping reviewed.
