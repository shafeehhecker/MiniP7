"""Services tests run against the in-memory repository — no database needed,
proving the service is storage-agnostic (the point of the repository seam)."""
import pytest
from schema import Activity
from persistence import InMemoryProjectRepository
from services import ProjectService, ServiceError


@pytest.fixture
def svc():
    s = ProjectService(InMemoryProjectRepository())
    s.create_project("p", "Test")
    return s


def test_sample_and_schedule(svc):
    svc.load_sample("p")
    r = svc.schedule("p")
    assert r["duration"] == 14
    assert r["critical_path"] == ["A", "B", "C", "E"]


def test_add_and_reschedule(svc):
    svc.load_sample("p")
    svc.add_activity("p", Activity(id="F", name="Handover", duration=1, predecessors=["E"]))
    r = svc.schedule("p")
    assert r["duration"] == 15
    assert "F" in r["critical_path"]


def test_duplicate_activity_rejected(svc):
    svc.load_sample("p")
    with pytest.raises(ServiceError):
        svc.add_activity("p", Activity(id="A", name="dup", duration=1))


def test_schedule_empty_rejected(svc):
    with pytest.raises(ServiceError):
        svc.schedule("p")


def test_cycle_rejected(svc):
    svc.add_activity("p", Activity(id="X", name="X", duration=1, predecessors=["Y"]))
    svc.add_activity("p", Activity(id="Y", name="Y", duration=1, predecessors=["X"]))
    with pytest.raises(ServiceError):
        svc.schedule("p")
