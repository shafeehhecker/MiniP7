# `ui` — deliberately still a placeholder

> Category: **Commons** (planned). The design system this package is meant
> to hold currently lives in `apps/web/src/components` instead. See
> [ADR-0014](../../docs/adr/0014-frontend-stack.md) for why, and read on for
> when that changes.

## Why the components aren't here yet

Phase 5 built a full component set — `Button`, `Input`, `Select`, `Modal`,
`Card`, `Table`, `Badge`, `Alert`, `Spinner`, plus the domain-specific
`Gantt` and `ActivityModal` — but placed them in
[`apps/web/src/components`](../../apps/web/src/components), not here.

That's YAGNI, not an oversight: `packages/ui` earns its keep once a *second*
consumer needs the same primitives — a future admin app, a marketing site
reusing the design tokens, `apps/cli` output formatting, whatever it turns
out to be. With exactly one consumer, extracting a commons package now would
add an indirection with nothing on the other side of it. `packages/client`
was different: `packages/schema` was already generating TypeScript before
`apps/web` existed, so the commons package came first by construction, not
by choice.

## The extraction path (when it's needed)

1. `npm init` a real `package.json` here (`@minip7/ui`), same shape as
   `packages/client/package.json`.
2. Move `apps/web/src/components/common/*` here; keep `gantt/` and `forms/`
   in `apps/web` since those are domain-specific, not generic primitives.
3. Move the Tailwind design tokens (`apps/web/tailwind.config.js`'s
   `theme.extend`) here as a shared preset the consuming app's own Tailwind
   config extends.
4. Add `packages/ui` to the root `package.json` workspaces list; add
   `@minip7/ui` as a dependency of `apps/web` (and the new consumer).
5. Add `ui` to `tooling/importlinter.ini` if/when a Python-side analogue
   applies, and an import-linter equivalent on the TS side if the dependency
   graph needs enforcing beyond what `tsc` already catches through the
   workspace's type imports.

Until then, `apps/web/src/components/common/` **is** the design system, and
its README documents the token names in use.
