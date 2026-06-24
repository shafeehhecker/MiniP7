# The commons registry

> Category: **Reference**. The authoritative list of shared packages, what each
> guarantees, and what may depend on what. For the *why*, see
> [ARCHITECTURE.md](ARCHITECTURE.md).

A "commons" is a versioned, independently-tested, independently-installable
package that downstream code imports. Each is produced by exactly one delivery
phase and must obey the [dependency rule](ARCHITECTURE.md#the-dependency-rule).

| Package | Phase | Language | Stability | Depends on | Purpose |
|---|---|---|---|---|---|
| [`schema`](../../packages/schema/README.md) | 1 | Python → TS | experimental | — | Canonical domain model; the single source of truth |
| [`engine`](../../packages/engine/README.md) | 2 | Python | experimental | `schema` | Pure CPM + EVM computation, no I/O |
| `persistence` | 3 | Python | planned | `schema` | Storage-agnostic repositories |
| `services` | 3 | Python | planned | `engine`, `persistence` | Orchestration / use-cases |
| `client` | 4 | TypeScript | planned | `schema` | Generated, typed API client |
| `ui` | 5 | TypeScript | planned | `client`, `schema` | Design system + Gantt/grid + data hooks |

## Rules that keep the registry honest

- **One producer per package.** A package has a single owning phase and a single
  `CODEOWNERS` entry. Shared ownership means no ownership.
- **The public API is only what the README lists.** Anything not documented in a
  package's `## Public API` section is private and may change without a major
  version bump.
- **Dependencies only point inward.** A package may import packages strictly below
  it in the table, never above, never an app. CI enforces this.
- **Shared logic moves down, never sideways.** If two consumers need the same
  thing, it belongs in a commons below them — not duplicated, not imported across.

## How to add a new commons

See the how-to guide: [docs/guides/adding-a-package.md](../guides/adding-a-package.md).
Adding a commons requires an ADR if it changes the dependency graph.
