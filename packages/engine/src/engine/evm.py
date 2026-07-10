"""Earned Value Method over a scheduled network (ADR-0013).

Given activities that have been through :class:`engine.CPMScheduler` (so ES/EF
are populated) and carry a ``budget``, ``percent_complete`` and ``actual_cost``,
compute the standard earned-value metrics as of a status day.

Definitions (see the glossary for the full vocabulary):

- **PV / BCWS** — the budget that *should* have been consumed by the status
  day, assuming each activity's budget accrues linearly across ES..EF. A
  milestone's value accrues entirely at its day.
- **EV / BCWP** — ``budget × percent_complete`` per activity: the budgeted
  worth of the work actually performed.
- **AC / ACWP** — the actual money spent, straight from ``actual_cost``.

Ratios are ``None`` — never 0, never infinity — when their denominator is
zero, so "we haven't planned/spent anything yet" is distinguishable from
"we are exactly on plan".
"""
from __future__ import annotations

from typing import Iterable, Optional

from schema import Activity, ActivityType, EVMResult


def _planned_fraction(act: Activity, as_of_day: int) -> float:
    """The fraction of an activity's budget planned to be consumed by
    ``as_of_day``, under linear accrual across its scheduled span."""
    if act.duration == 0:  # milestone (or zero-duration task): all-at-once
        return 1.0 if as_of_day >= act.EF else 0.0
    if as_of_day <= act.ES:
        return 0.0
    if as_of_day >= act.EF:
        return 1.0
    return (as_of_day - act.ES) / act.duration


def _ratio(num: float, den: float) -> Optional[float]:
    return None if den == 0 else num / den


def compute_evm(activities: Iterable[Activity], as_of_day: int) -> EVMResult:
    """Compute an :class:`schema.EVMResult` snapshot for a scheduled network.

    Level-of-effort activities are included like any other: their span is
    driven by the work they support, and their budget accrues across it.
    Activities must already be scheduled; ``as_of_day`` is in working days.
    """
    if as_of_day < 0:
        raise ValueError("Status day must be >= 0.")

    acts = list(activities)
    bac = sum(a.budget for a in acts)
    pv = sum(a.budget * _planned_fraction(a, as_of_day) for a in acts)
    ev = sum(a.budget * a.percent_complete / 100 for a in acts)
    ac = sum(a.actual_cost for a in acts)

    cpi = _ratio(ev, ac)
    eac = _ratio(bac, cpi) if cpi else None  # None or 0 CPI -> no forecast

    return EVMResult(
        as_of_day=as_of_day,
        bac=bac,
        pv=pv,
        ev=ev,
        ac=ac,
        sv=ev - pv,
        cv=ev - ac,
        spi=_ratio(ev, pv),
        cpi=cpi,
        eac=eac,
        etc=(eac - ac) if eac is not None else None,
        vac=(bac - eac) if eac is not None else None,
    )
