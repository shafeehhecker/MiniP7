# ADR-0004: Gantt component — build vs buy

- **Status:** Proposed
- **Date:** 2026-06-24
- **Deciders:** Core team (DECISION PENDING — needs product input)

## Context

The interactive Gantt (dependency arrows, baselines, drag-to-reschedule, WBS
rollup, resource histogram) is roughly half the total frontend effort if built
from scratch. It is also the single most visible surface of the product.

## Options considered

### Option A — Build a custom Gantt (SVG/Canvas)
- Pros: full control; no licence cost; no third-party styling to fight.
- Cons: months of work to reach parity with mature components; ongoing maintenance
  of a hard, edge-case-heavy widget.

### Option B — Buy / adopt a component
- **Syncfusion Gantt** — free community licence under a revenue threshold; full-featured.
- **DHTMLX Gantt** — affordable commercial; solid.
- **Bryntum Gantt** — highest fidelity, closest to the target mockup; paid per dev.
- Pros: weeks of integration instead of months; battle-tested behaviour.
- Cons: licence cost and/or revenue conditions; we wrap it behind our own
  interface in `packages/ui` to avoid lock-in.

## Decision

PENDING. Recommendation: adopt a component (Option B) and isolate it behind a
`packages/ui` wrapper so the rest of the app depends on *our* Gantt interface, not
the vendor's — keeping the option to swap or replace later at low cost.

## Consequences

To be recorded once decided. The wrapper boundary is required either way, so the
rest of the UI work is unblocked before this is finalised.
