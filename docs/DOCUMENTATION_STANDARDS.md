# Documentation standards

> Documentation is a product surface here, not an afterthought. This file is the
> contract for how we write it. It is enforced in review and in CI.

Most scheduling tools rot because their internals are undocumented and their
decisions are unrecorded. Mini-P7 differentiates on the opposite: a disciplined
**commons** graph and **documentation treated as code**. This document defines
what "good docs" means here and how we keep it true over time.

---

## 1. The Diátaxis model

We organise all documentation into the four [Diátaxis](https://diataxis.fr)
categories. Every document belongs to exactly one. Mixing them is the most
common documentation failure, so we keep them physically separated.

| Category | Answers | Lives in | Voice |
|---|---|---|---|
| **Tutorial** | "Teach me, I'm new" | `docs/guides/` (getting-started) | Learning-oriented, hand-held |
| **How-to guide** | "How do I do X?" | `docs/guides/` | Task-oriented, assumes context |
| **Reference** | "What exactly is X?" | `docs/reference/`, package READMEs | Information-oriented, dry, complete |
| **Explanation** | "Why is it this way?" | `docs/architecture/`, `docs/domain/`, `docs/adr/` | Understanding-oriented, discursive |

The mental test before writing: *Am I teaching, instructing, describing, or
explaining?* If a page does two of these, split it.

---

## 2. Documentation lives next to code

Docs are committed in the same repository as the code they describe, reviewed in
the same pull request, and versioned together. A change to behaviour that does
not update its documentation is an incomplete change and will be blocked in
review.

- **Every package** (`packages/*`) has a `README.md` documenting its *contract*:
  purpose, public API, invariants, dependencies, and stability. See
  [§4](#4-the-package-readme-contract).
- **Every public function, class, and endpoint** has a docstring or doc comment
  stating what it does, its inputs/outputs, what it raises, and any invariants.
- **Every irreversible decision** is captured as an ADR in `docs/adr/`. See
  [§5](#5-architecture-decision-records).
- **Every domain term** is defined once in [`docs/domain/glossary.md`](domain/glossary.md)
  and never redefined elsewhere.

---

## 3. The documentation Definition of Done

A change is not "done" until all of these hold. This list is part of the PR
template and is checked in review.

- [ ] Public API changes are reflected in the package `README.md`.
- [ ] New or changed behaviour has updated docstrings/doc comments.
- [ ] New domain terms are added to the glossary; none are redefined.
- [ ] Any architectural decision is recorded as an ADR (or an existing ADR is
      superseded, not silently contradicted).
- [ ] New public functions have at least one worked example.
- [ ] Internal links resolve (checked by the docs CI job).
- [ ] Prose is in the correct Diátaxis category for its location.

---

## 4. The package README contract

Every commons package documents itself to a fixed template so that any engineer
can understand and consume it without reading its source. The required sections:

1. **Purpose** — one paragraph: what problem this package solves and for whom.
2. **Stability** — `experimental` | `stable` | `deprecated`, and the semver policy.
3. **Public API** — the exported surface. Anything not listed here is private and
   may change without notice.
4. **Invariants** — the guarantees callers may rely on (e.g. "the scheduler never
   mutates its input"; "dates are always working-day-adjusted").
5. **Dependencies** — which other commons it imports. Must obey the
   [dependency rule](architecture/ARCHITECTURE.md#the-dependency-rule).
6. **Usage** — a minimal, copy-pasteable worked example.
7. **Testing** — how to run this package's tests in isolation.

A template lives at [`docs/reference/package-readme-template.md`](reference/package-readme-template.md).

---

## 5. Architecture Decision Records

An ADR records *why* a decision was made, the alternatives considered, and the
consequences — so future contributors don't relitigate settled questions or,
worse, silently reverse them.

- Stored in `docs/adr/`, numbered sequentially (`0001-…`, `0002-…`).
- Use the template at [`docs/adr/0000-template.md`](adr/0000-template.md).
- An ADR is **immutable once accepted**. To change a decision, write a new ADR
  that supersedes the old one and update the old one's status to `Superseded by
  ADR-NNNN`. Never edit an accepted decision in place.
- Statuses: `Proposed` → `Accepted` → (`Superseded` | `Deprecated`).

---

## 6. Style rules

- **Sentence case** for all headings.
- **Active voice, present tense.** "The scheduler computes floats", not "Floats
  will be computed by the scheduler".
- **Code, names, and paths** go in `inline code`, never bold.
- **One concept per paragraph.** Long walls of text are a sign the page is doing
  too much — split it by Diátaxis category.
- **Worked examples over prose.** A runnable example is worth three paragraphs.
- **Link, don't repeat.** Each fact has one home; everything else links to it.
  Duplicated documentation drifts and lies.
- **Diagrams** are committed as source (Mermaid or SVG) so they're diffable and
  reviewable, never pasted as opaque images.

---

## 7. Published docs site

The Markdown in `docs/` is the source of truth and renders directly on GitHub.
It is also published as a static site via **MkDocs Material** (see
[`mkdocs.yml`](../mkdocs.yml)), so the documentation is browsable, searchable,
and versioned alongside releases. The site build runs in CI; a broken link or a
missing page fails the build.

---

## 8. Why this is the differentiator

A new contributor should be able to: understand the architecture from
`docs/architecture/`, learn the domain from `docs/domain/`, find out *why*
anything is the way it is from `docs/adr/`, and consume any commons from its
README — all without reading implementation code or asking a maintainer. When
that is true, the project scales past its original authors. That is the goal.
