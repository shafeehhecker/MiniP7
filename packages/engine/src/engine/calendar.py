"""Map abstract working days onto real calendar dates (ADR-0012).

The scheduler computes in working-day offsets (day 0, day 1, ...). This module
turns those offsets into dates using a :class:`schema.Calendar` (which weekdays
work, which dates are holidays) anchored at a project start date. The engine's
maths never changes — dates are a *presentation* of the schedule, computed on
demand and never stored on the activity.

Conventions
-----------
- Working day 0 is the first working date on or after the anchor date.
- An activity occupies working days ``ES .. EF-1`` inclusive, so its finish
  date is the date of working day ``EF - 1``.
- A milestone (``ES == EF``) occurs at the start of working day ``ES``; its
  start and finish dates are the same.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Iterable, Tuple

from schema import Activity, Calendar


class WorkdayCalendar:
    """Resolves working-day offsets to calendar dates.

    Pure and deterministic: the same calendar and anchor always produce the
    same dates. Lookups are cached, so mapping a whole schedule is O(days).
    """

    def __init__(self, calendar: Calendar, anchor: date):
        if not calendar.working_days:
            raise ValueError("Calendar has no working days.")
        self._working = set(calendar.working_days)
        self._holidays = set(calendar.holidays)
        self._anchor = anchor
        self._cache: list[date] = []  # index = working-day offset

    def is_working_day(self, d: date) -> bool:
        """True if ``d`` is a working date under this calendar."""
        return d.weekday() in self._working and d not in self._holidays

    def date_of(self, day_offset: int) -> date:
        """The calendar date of working day ``day_offset`` (0-based)."""
        if day_offset < 0:
            raise ValueError("Working-day offsets are non-negative.")
        d = self._cache[-1] + timedelta(days=1) if self._cache else self._anchor
        while len(self._cache) <= day_offset:
            if self.is_working_day(d):
                self._cache.append(d)
            d += timedelta(days=1)
        return self._cache[day_offset]

    def span_of(self, activity: Activity) -> Tuple[date, date]:
        """The (start_date, finish_date) of a *scheduled* activity.

        Follows the module conventions: finish is the date of the last working
        day the activity occupies; a milestone's start and finish coincide.
        """
        start = self.date_of(activity.ES)
        finish = self.date_of(max(activity.ES, activity.EF - 1))
        return start, finish

    def map_schedule(
        self, activities: Iterable[Activity]
    ) -> Dict[str, Tuple[date, date]]:
        """Map every scheduled activity to its (start_date, finish_date)."""
        return {a.id: self.span_of(a) for a in activities}
