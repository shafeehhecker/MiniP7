# ADR-0009: Organization-level currency

- **Status:** Accepted
- **Date:** 2026-06-30
- **Deciders:** Core team
- **Supersedes:** —
- **Superseded by:** —

## Context

Costs and earned-value are on the roadmap, and when they arrive every monetary
figure must be expressed in a currency. We want to capture that choice now —
while it is cheap — rather than retrofit it across cost displays later. There are
no costs in the product yet, so today the choice is purely a display setting.

## Options considered

### Option A — Defer currency until costs exist
- Pros: nothing to build now.
- Cons: when costs land, currency becomes load-bearing and has to be threaded
  through models, storage, and UI in a hurry; existing orgs would need a backfill.

### Option B — Add an organization-level currency now
- A `Currency` value object (ISO 4217 code, symbol, name) is a field on
  `Organization`, defaulting to USD. Owners and admins can change it. A small
  catalogue is exposed for pickers.
- Pros: the choice is captured and validated from day one; defaults mean no
  migration; the seam is ready for cost rollups.
- Cons: a setting with no functional effect yet (acceptable — it is cheap and
  forward-looking).

## Decision

Adopt Option B. `Organization.currency` is a `Currency` defaulting to USD. The
code is validated as three letters (ISO 4217). Setting it is an organization-wide
action gated to owners and admins, consistent with other administrative changes.
Currency is a display setting until cost rollups exist.

## Consequences

- Existing organizations load as USD (the default); no migration is required.
- Currency is cosmetic today. Its value is realised when costs and EVM arrive,
  at which point this setting is already in place and validated.
- A fixed catalogue (`COMMON_CURRENCIES`) is a starting set, not exhaustive; it
  can grow without an ADR because it is data, not a decision.
