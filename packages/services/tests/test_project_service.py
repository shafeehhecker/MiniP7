"""Services tests against the in-memory repo — no database needed.

These cover both the scheduling logic and the multi-tenant guarantees: data is
scoped per organization, and roles gate writes."""
import pytest
from schema import Activity, User, Role
from persistence import InMemoryRepository
from services import ProjectService, ServiceError, PermissionError_


@pytest.fixture
def svc():
    return ProjectService(InMemoryRepository())


@pytest.fixture
def owner():
    return User(id="u1", email="owner@acme.com", name="Owner")


def _org_with_project(svc, owner, org_id="acme", proj_id="p1"):
    svc.create_organization(org_id, "Acme", owner)
    svc.create_project(org_id, owner.id, proj_id, "Internal Project")
    return org_id, proj_id


def test_sample_and_schedule(svc, owner):
    org, proj = _org_with_project(svc, owner)
    svc.load_sample(org, owner.id, proj)
    r = svc.schedule(org, owner.id, proj)
    assert r["duration"] == 14
    assert r["critical_path"] == ["A", "B", "C", "E"]


def test_projects_are_scoped_to_their_org(svc, owner):
    # Two orgs, each with a project. One owner is in both; a stranger in neither.
    svc.create_organization("acme", "Acme", owner)
    svc.create_organization("globex", "Globex", owner)
    svc.create_project("acme", owner.id, "a1", "Acme project")
    svc.create_project("globex", owner.id, "g1", "Globex project")

    acme_projects = svc.list_projects("acme", owner.id)
    assert [p.id for p in acme_projects] == ["a1"]          # only Acme's
    assert "g1" not in [p.id for p in acme_projects]        # never Globex's


def test_cannot_access_other_orgs_project_by_id(svc, owner):
    svc.create_organization("acme", "Acme", owner)
    svc.create_organization("globex", "Globex", owner)
    svc.create_project("globex", owner.id, "g1", "secret")
    # Asking for g1 *via acme* must fail even though the same user owns both.
    with pytest.raises(ServiceError):
        svc.get_project("acme", owner.id, "g1")


def test_non_member_is_denied(svc, owner):
    org, proj = _org_with_project(svc, owner)
    with pytest.raises(PermissionError_):
        svc.get_project(org, "stranger", proj)


def test_viewer_cannot_write(svc, owner):
    org, proj = _org_with_project(svc, owner)
    viewer = User(id="v1", email="viewer@acme.com")
    svc.add_member(org, owner.id, viewer.id, Role.VIEWER)
    # viewer can read...
    svc.get_project(org, viewer.id, proj)
    # ...but not write
    with pytest.raises(PermissionError_):
        svc.add_activity(org, viewer.id, proj,
                         Activity(id="X", name="X", duration=1))


def test_member_can_write(svc, owner):
    org, proj = _org_with_project(svc, owner)
    member = User(id="m1", email="member@acme.com")
    svc.add_member(org, owner.id, member.id, Role.MEMBER)
    svc.add_activity(org, member.id, proj, Activity(id="A", name="Start", duration=2))
    p = svc.get_project(org, member.id, proj)
    assert [a.id for a in p.activities] == ["A"]


def test_only_admins_add_members(svc, owner):
    org, proj = _org_with_project(svc, owner)
    member = User(id="m1", email="member@acme.com")
    svc.add_member(org, owner.id, member.id, Role.MEMBER)
    # a plain member may not add others
    with pytest.raises(PermissionError_):
        svc.add_member(org, member.id, "m2", Role.MEMBER)


def test_cycle_rejected(svc, owner):
    org, proj = _org_with_project(svc, owner)
    svc.add_activity(org, owner.id, proj, Activity(id="X", name="X", duration=1, predecessors=["Y"]))
    svc.add_activity(org, owner.id, proj, Activity(id="Y", name="Y", duration=1, predecessors=["X"]))
    with pytest.raises(ServiceError):
        svc.schedule(org, owner.id, proj)
