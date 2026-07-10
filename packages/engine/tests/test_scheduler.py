"""Tests for the CPM scheduling engine.

Locks in correct float values — notably that sample activity D has TF = 3, FF = 3
(an earlier README claimed 5/5, which was wrong; see docs/domain/cpm.md)."""
import pytest

from schema import Activity
from engine import CPMScheduler, SchedulerError


def _run(activities):
    s = CPMScheduler({a.id: a for a in activities})
    s.schedule()
    return s


def test_documented_sample_critical_path_and_floats():
    s = _run([
        Activity(id="A", name="Start", duration=2),
        Activity(id="B", name="Foundation", duration=4, predecessors=["A"]),
        Activity(id="C", name="Structure", duration=6, predecessors=["B"]),
        Activity(id="D", name="Electrical", duration=3, predecessors=["B"]),
        Activity(id="E", name="Finish", duration=2, predecessors=["C", "D"]),
    ])
    assert s.project_duration() == 14
    assert s.get_critical_path() == ["A", "B", "C", "E"]
    d = s.activities["D"]
    assert d.total_float == 3
    assert d.free_float == 3
    assert d.is_critical is False


def test_single_activity():
    s = _run([Activity(id="X", name="Only", duration=7)])
    x = s.activities["X"]
    assert (x.ES, x.EF, x.LS, x.LF) == (0, 7, 0, 7)
    assert x.is_critical and x.total_float == 0


def test_empty_network_returns_empty():
    s = CPMScheduler({})
    assert s.schedule() == []
    assert s.project_duration() == 0


def test_parallel_paths_pick_longer():
    s = _run([
        Activity(id="A", name="A", duration=1),
        Activity(id="B", name="B", duration=2, predecessors=["A"]),
        Activity(id="C", name="C", duration=5, predecessors=["A"]),
        Activity(id="D", name="D", duration=1, predecessors=["B", "C"]),
    ])
    assert s.project_duration() == 7
    assert s.activities["B"].total_float == 3
    assert s.activities["C"].total_float == 0


def test_diamond_free_float():
    s = _run([
        Activity(id="A", name="A", duration=0),
        Activity(id="B", name="B", duration=2, predecessors=["A"]),
        Activity(id="C", name="C", duration=6, predecessors=["A"]),
        Activity(id="D", name="D", duration=1, predecessors=["B", "C"]),
    ])
    assert s.activities["B"].free_float == 4


def test_cycle_raises():
    with pytest.raises(SchedulerError):
        _run([
            Activity(id="A", name="A", duration=1, predecessors=["C"]),
            Activity(id="B", name="B", duration=1, predecessors=["A"]),
            Activity(id="C", name="C", duration=1, predecessors=["B"]),
        ])


def test_unknown_predecessor_raises():
    with pytest.raises(SchedulerError):
        _run([Activity(id="A", name="A", duration=1, predecessors=["ghost"])])


def test_zero_duration_milestone():
    s = _run([
        Activity(id="M", name="Milestone", duration=0),
        Activity(id="T", name="Task", duration=3, predecessors=["M"]),
    ])
    assert s.project_duration() == 3
    assert s.activities["M"].is_critical


def test_milestone_type_schedules_as_zero_duration():
    from schema import ActivityType
    s = _run([
        Activity(id="M", name="Kickoff", duration=0, type=ActivityType.MILESTONE),
        Activity(id="T", name="Work", duration=4, predecessors=["M"]),
    ])
    m = s.activities["M"]
    assert (m.ES, m.EF) == (0, 0)
    assert s.get_milestones() == ["M"]
    assert s.project_duration() == 4


def test_level_of_effort_is_scheduled_not_rejected():
    from schema import ActivityType
    # ADR-0008 deferred LOE behaviour until typed relationships landed; they
    # have (ADR-0011), so an LOE now *spans* the work it supports rather than
    # scheduling as a task after it.
    s = _run([
        Activity(id="A", name="Build", duration=5),
        Activity(id="PM", name="Manage", duration=5, predecessors=["A"],
                 type=ActivityType.LEVEL_OF_EFFORT),
    ])
    assert (s.activities["PM"].ES, s.activities["PM"].EF) == (0, 5)
    assert not s.activities["PM"].is_critical
