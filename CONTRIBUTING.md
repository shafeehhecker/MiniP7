# Contributing

Thanks for contributing to Mini-P7. Two rules matter most here, because they are
what the project is *about*.

## 1. Docs ship with code

A behaviour change without a matching documentation change is incomplete and will
be blocked in review. Before opening a PR, walk the
[documentation Definition of Done](docs/DOCUMENTATION_STANDARDS.md#3-the-documentation-definition-of-done).

## 2. Respect the dependency rule

`apps/` may import `packages/`; `packages/` may import strictly *lower* packages;
nothing imports `apps/`; no feature vertical imports another. This is enforced by
CI ([ADR-0002](docs/adr/0002-dependency-rule.md)). If you think you need to break
it, you need an ADR first.

## Workflow

1. Branch off `main` with a short, descriptive name.
2. Use [Conventional Commits](https://www.conventionalcommits.org) (`feat:`,
   `fix:`, `docs:`, `refactor:`, …).
3. Add or update tests; add or update docs.
4. Open a PR; fill in the template; ensure CI is green.
5. A decision of any architectural weight gets an ADR in `docs/adr/`.

## Adding a new commons package

Follow [docs/guides/adding-a-package.md](docs/guides/adding-a-package.md). It
requires an ADR if it changes the dependency graph.
