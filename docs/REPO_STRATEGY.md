# Repository strategy

> Category: **Explanation**. How the repo is organised, branched, versioned, and
> shipped. Decisions here are backed by ADRs in [docs/adr](adr/README.md).

## Monorepo

A single polyglot monorepo (Python + TypeScript) split into `packages/` (commons)
and `apps/` (interfaces). The rationale — preventing contract drift across
languages — is recorded in [ADR-0001](adr/0001-monorepo.md). The split is enforced
by import-boundary lint rules ([ADR-0002](adr/0002-dependency-rule.md)).

Tooling: **Nx** (polyglot-aware, runs affected-only tasks) or pnpm workspaces +
Turborepo for the TypeScript side with **uv** managing Python packages. The win
either way: a PR touching only `engine` runs only `engine`'s tests and its
dependents', keeping CI fast.

## Branching

Trunk-based development. Short-lived branches off `main`, opened as PRs with
required passing CI. `main` is protected: no direct pushes, required reviews via
`CODEOWNERS`, linear history.

## Commits & versioning

[Conventional Commits](https://www.conventionalcommits.org) drive automated
versioning. Each commons package is **independently versioned and changelogged**
(via Changesets or release-please); apps consume workspace versions. A breaking
change to a package bumps its major version and surfaces in its changelog.

## CI/CD

- **On every PR:** affected-only lint, type-check, test; docs link-check and site
  build; import-boundary check; a preview deployment of `apps/web`.
- **On merge to main:** version + changelog packages; publish internal package
  versions; deploy `api` and `web` to staging.
- **On release tag:** promote to production.

## Project management

Each roadmap phase is a **GitHub Milestone**. Work is tracked in **GitHub
Projects** (a board per active phase). Issues use templates (feature / bug /
ADR-needed) and carry a package label (`pkg:engine`, `pkg:ui`, …). A phase's
definition of done is its milestone checklist.

## Ownership

`CODEOWNERS` assigns each package a single owning reviewer, so PRs route
automatically and every package has a clear maintainer.
