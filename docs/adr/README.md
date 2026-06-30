# Architecture Decision Records

> Category: **Explanation**. ADRs record *why* a decision was made — the context,
> the options weighed, and the consequences — so settled questions stay settled.

## How it works

- ADRs are numbered sequentially and stored here as `NNNN-title.md`.
- Use [`0000-template.md`](0000-template.md) to start a new one.
- An accepted ADR is **immutable**. To change a decision, write a *new* ADR that
  supersedes it; set the old one's status to `Superseded by ADR-NNNN`. Never edit
  an accepted decision in place — the history is the point.
- Statuses: `Proposed` → `Accepted` → (`Superseded` | `Deprecated`).

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-monorepo.md) | Use a single polyglot monorepo | Accepted |
| [0002](0002-dependency-rule.md) | Enforce the inward dependency rule | Accepted |
| [0003](0003-schema-single-source-of-truth.md) | One schema, generated into every language | Accepted |
| [0004](0004-gantt-build-vs-buy.md) | Gantt component: build vs buy | Proposed |
| [0005](0005-multi-tenancy.md) | Multi-tenant model (org → user → project) | Accepted |
| [0006](0006-authentication.md) | Authentication approach | Proposed |
| [0007](0007-user-preferences.md) | User preferences embedded in the user | Accepted |
| [0008](0008-activity-types.md) | Activity types (task / milestone / LOE / summary) | Accepted |
| [0009](0009-currency.md) | Organization-level currency | Accepted |
