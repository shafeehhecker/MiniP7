"""Earned-value calculations (ADR-0013). Expected values worked by hand."""
import pytest
from schema import Activity
from engine import CPMScheduler, compute_evm


def scheduled(acts):
    d = {a.id: a for a in acts}
    CPMScheduler(d).schedule()
    return d.values()


def test_worked_example():
    # A: 100 over days 0-5; B: 60 over days 5-8 (FS after A).
    acts = scheduled([
        Activity(id="A", name="a", duration=5, budget=100,
                 percent_complete=100, actual_cost=110),
        Activity(id="B", name="b", duration=3, budget=60, predecessors=["A"],
                 percent_complete=50, actual_cost=20),
    ])
    r = compute_evm(acts, as_of_day=6)
    assert r.bac == 160
    assert r.pv == pytest.approx(120)   # 100 + 60*(1/3)
    assert r.ev == pytest.approx(130)   # 100 + 30
    assert r.ac == 130
    assert r.sv == pytest.approx(10) and r.cv == pytest.approx(0)
    assert r.spi == pytest.approx(130 / 120) and r.cpi == pytest.approx(1.0)
    assert r.eac == pytest.approx(160) and r.etc == pytest.approx(30)
    assert r.vac == pytest.approx(0)


def test_milestone_value_accrues_at_its_day():
    acts = scheduled([
        Activity(id="A", name="a", duration=4),
        Activity(id="M", name="gate", duration=0, budget=50, predecessors=["A"]),
    ])
    assert compute_evm(acts, 3).pv == 0
    assert compute_evm(acts, 4).pv == 50


def test_ratios_are_none_not_zero_or_inf():
    acts = scheduled([Activity(id="A", name="a", duration=5, budget=100)])
    r = compute_evm(acts, 0)  # nothing planned yet, nothing spent, nothing earned
    assert r.pv == 0 and r.ev == 0 and r.ac == 0
    assert r.spi is None and r.cpi is None
    assert r.eac is None and r.etc is None and r.vac is None


def test_before_start_and_after_finish_clamped():
    acts = scheduled([Activity(id="A", name="a", duration=5, budget=100)])
    assert compute_evm(acts, 0).pv == 0
    assert compute_evm(acts, 99).pv == 100


def test_negative_status_day_rejected():
    with pytest.raises(ValueError):
        compute_evm([], -1)
