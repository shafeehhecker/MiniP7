"""Tests for the canonical schema — validation and the new value objects.

Locks in the invariants that other layers rely on: a milestone cannot carry a
duration, an activity defaults to a task, preferences default safely, and a
currency code is shaped like ISO 4217.
"""
import pytest

from schema import (
    Activity, ActivityType,
    UserPreferences, UnitSystem, DateFormat, Theme,
    Currency, COMMON_CURRENCIES,
    User, Organization,
)


# ---- activity type ----
def test_activity_defaults_to_task():
    a = Activity(id="A", name="Start", duration=3)
    assert a.type == ActivityType.TASK


def test_milestone_requires_zero_duration():
    with pytest.raises(ValueError):
        Activity(id="M", name="Gate", duration=2, type=ActivityType.MILESTONE)


def test_milestone_with_zero_duration_is_valid():
    m = Activity(id="M", name="Gate", duration=0, type=ActivityType.MILESTONE)
    assert m.type == ActivityType.MILESTONE and m.duration == 0


def test_loe_and_summary_are_accepted():
    loe = Activity(id="L", name="PM", duration=5, type=ActivityType.LEVEL_OF_EFFORT)
    summ = Activity(id="S", name="Phase 1", duration=0, type=ActivityType.SUMMARY)
    assert loe.type == ActivityType.LEVEL_OF_EFFORT
    assert summ.type == ActivityType.SUMMARY


def test_type_appears_in_summary_line():
    a = Activity(id="A", name="Start", duration=2, type=ActivityType.TASK)
    assert "task" in a.summary()


# ---- user preferences ----
def test_preferences_have_safe_defaults():
    p = UserPreferences()
    assert p.units == UnitSystem.DAYS
    assert p.date_format == DateFormat.ISO
    assert p.theme == Theme.SYSTEM


def test_user_gets_default_preferences():
    u = User(id="u1", email="a@b.com")
    assert u.preferences == UserPreferences()


def test_preferences_round_trip_through_user_json():
    u = User(id="u1", email="a@b.com",
             preferences=UserPreferences(theme=Theme.DARK, units=UnitSystem.HOURS))
    again = User.model_validate_json(u.model_dump_json())
    assert again.preferences.theme == Theme.DARK
    assert again.preferences.units == UnitSystem.HOURS


# ---- currency ----
def test_currency_default_is_usd():
    c = Currency.default()
    assert c.code == "USD" and c.symbol == "$"


def test_currency_code_is_normalised_and_validated():
    assert Currency(code="eur", symbol="€", name="Euro").code == "EUR"
    with pytest.raises(ValueError):
        Currency(code="US", symbol="$", name="bad")
    with pytest.raises(ValueError):
        Currency(code="US1", symbol="$", name="bad")


def test_organization_defaults_to_usd():
    org = Organization(id="o1", name="Acme")
    assert org.currency.code == "USD"


def test_catalogue_is_non_empty_and_valid():
    assert COMMON_CURRENCIES
    assert all(len(c.code) == 3 for c in COMMON_CURRENCIES)
