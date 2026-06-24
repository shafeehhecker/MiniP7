# Mini-P7

A Critical Path Method (CPM) project scheduler — engine, API, CLI, and web app —
built on two principles most tools in this space neglect: a disciplined
**commons** architecture and **documentation treated as a product**.

## What makes this different

- **Commons, not a monolith.** The codebase is a strict dependency graph of small,
  reusable, independently-versioned packages. A pure scheduling engine sits at the
  bottom and is reused unchanged by the API, the CLI, and tests. See
  [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md).
- **Documentation as a first-class surface.** Every package documents its
  contract, every decision is recorded as an ADR, every domain term is defined
  once, and all of it is enforced in review and CI. See
  [docs/DOCUMENTATION_STANDARDS.md](docs/DOCUMENTATION_STANDARDS.md).

## Repository map

```
packages/        the commons — reusable, versioned, documented
  schema/        Phase 1 · canonical domain model (the contract)
  engine/        Phase 2 · pure CPM + EVM computation
  persistence/   Phase 3 · storage-agnostic repositories
  services/      Phase 3 · orchestration / use-cases
  client/        Phase 4 · generated typed API client
  ui/            Phase 5 · design system + Gantt/grid + hooks
apps/            the interfaces — consumers, never imported
  api/           FastAPI server
  cli/           Typer command line
  web/           React app
docs/            the documentation product (see below)
tooling/         shared lint/format/type/CI config
infra/           Docker, IaC, deploy
```

## Documentation

The `docs/` tree is organised by the [Diátaxis](https://diataxis.fr) model:

- **Learn** — [docs/guides/getting-started.md](docs/guides/getting-started.md)
- **Do** — [docs/guides/](docs/guides/) (how-to guides)
- **Look up** — [docs/reference/](docs/reference/), package READMEs, and the
  [glossary](docs/domain/glossary.md)
- **Understand** — [docs/architecture/](docs/architecture/),
  [docs/domain/](docs/domain/), and the
  [decision log](docs/adr/README.md)

## Status

Early. The `engine` and `schema` packages contain working, tested code; the rest
of the graph is scaffolded and scheduled across phases in
[docs/ROADMAP.md](docs/ROADMAP.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: docs ship with code, the
dependency rule is enforced, and decisions are recorded as ADRs.
