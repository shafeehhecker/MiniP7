# How to add a new commons package

> Category: **How-to guide**. Task-oriented. Assumes you know the
> [architecture](../architecture/ARCHITECTURE.md).

1. **Check it belongs.** A commons is shared, reusable logic. If only one app
   needs it, it is not a commons — it lives in that app.
2. **Place it correctly in the graph.** Decide what it depends on. It may only
   depend on packages *below* it. If it changes the dependency graph, write an ADR.
3. **Scaffold the package** under `packages/<name>/` with `src/`, `tests/`, a
   build manifest, and a `README.md` following the
   [package README template](../reference/package-readme-template.md).
4. **Write the README first.** Document the contract before the implementation —
   it forces a clean public API.
5. **Register it** in [the commons registry](../architecture/commons.md) and add a
   `CODEOWNERS` entry.
6. **Wire CI:** the package is picked up by affected-only test/lint automatically
   once it has the standard manifest.
