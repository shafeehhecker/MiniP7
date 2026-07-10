"""Working-day → calendar-date mapping (ADR-0012)."""
from datetime import date
import pytest
from schema import Activity, Calendar
from engine import CPMScheduler, WorkdayCalendar

MON = date(2026, 7, 6)  # a Monday


def test_default_calendar_skips_weekends():
    cal = WorkdayCalendar(Calendar(), MON)
    assert cal.date_of(0) == date(2026, 7, 6)   # Mon
    assert cal.date_of(4) == date(2026, 7, 10)  # Fri
    assert cal.date_of(5) == date(2026, 7, 13)  # next Mon, weekend skipped


def test_anchor_on_non_working_day_rolls_forward():
    sat = date(2026, 7, 4)
    cal = WorkdayCalendar(Calendar(), sat)
    assert cal.date_of(0) == MON


def test_holidays_are_skipped():
    cal = WorkdayCalendar(Calendar(holidays=[date(2026, 7, 8)]), MON)  # Wed off
    assert cal.date_of(2) == date(2026, 7, 9)  # Mon, Tue, then Thu


def test_custom_working_week():
    # Sunday-Thursday week (e.g. Qatar): 6=Sun .. 3=Thu
    cal = WorkdayCalendar(Calendar(working_days=[6, 0, 1, 2, 3]), date(2026, 7, 5))
    assert cal.date_of(0) == date(2026, 7, 5)   # Sunday works
    assert cal.date_of(4) == date(2026, 7, 9)   # Thursday
    assert cal.date_of(5) == date(2026, 7, 12)  # Fri+Sat skipped → next Sunday


def test_activity_span_and_milestone_convention():
    acts = {
        "A": Activity(id="A", name="a", duration=5),
        "M": Activity(id="M", name="done", duration=0, predecessors=["A"]),
    }
    CPMScheduler(acts).schedule()
    cal = WorkdayCalendar(Calendar(), MON)
    spans = cal.map_schedule(acts.values())
    assert spans["A"] == (date(2026, 7, 6), date(2026, 7, 10))  # Mon..Fri
    assert spans["M"] == (date(2026, 7, 13), date(2026, 7, 13))  # start == finish


def test_negative_offset_rejected():
    cal = WorkdayCalendar(Calendar(), MON)
    with pytest.raises(ValueError):
        cal.date_of(-1)


def test_determinism_and_cache_consistency():
    cal = WorkdayCalendar(Calendar(), MON)
    late = cal.date_of(30)
    assert cal.date_of(30) == late and cal.date_of(0) == MON
