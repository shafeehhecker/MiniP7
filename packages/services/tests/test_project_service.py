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


# ---- authentication (Milestone 1) ----
def test_register_and_authenticate():
    from persistence import InMemoryRepository
    s = ProjectService(InMemoryRepository(), token_secret="t")
    r = s.register_user("founder@acme.com", "hunter2pass", organization_name="Acme")
    assert r["organization_id"]
    log = s.authenticate("founder@acme.com", "hunter2pass")
    assert log["user_id"] == r["user_id"]


def test_duplicate_email_rejected():
    from persistence import InMemoryRepository
    s = ProjectService(InMemoryRepository(), token_secret="t")
    s.register_user("dup@acme.com", "password1")
    with pytest.raises(ServiceError):
        s.register_user("dup@acme.com", "password2")


def test_wrong_password_rejected():
    from persistence import InMemoryRepository
    s = ProjectService(InMemoryRepository(), token_secret="t")
    s.register_user("a@acme.com", "rightpass1")
    with pytest.raises(ServiceError):
        s.authenticate("a@acme.com", "wrongpass1")


def test_update_and_delete_activity():
    from persistence import InMemoryRepository
    from schema import User, Activity
    s = ProjectService(InMemoryRepository(), token_secret="t")
    owner = User(id="u1", email="o@acme.com")
    s.create_organization("acme", "Acme", owner)
    s.create_project("acme", "u1", "p1")
    s.add_activity("acme", "u1", "p1", Activity(id="A", name="Start", duration=2))
    # update
    s.update_activity("acme", "u1", "p1", Activity(id="A", name="Start v2", duration=5))
    p = s.get_project("acme", "u1", "p1")
    assert p.activities[0].name == "Start v2" and p.activities[0].duration == 5
    # delete
    s.delete_activity("acme", "u1", "p1", "A")
    assert len(s.get_project("acme", "u1", "p1").activities) == 0
    # delete missing
    with pytest.raises(ServiceError):
        s.delete_activity("acme", "u1", "p1", "ghost")


# ---- user preferences ----
def test_preferences_default_then_update(svc, owner):
    from schema import UserPreferences, Theme, UnitSystem
    svc.register_user("dev@acme.com", "password123", "Dev")
    user = svc._repo.get_user_by_email("dev@acme.com")
    prefs = svc.get_preferences(user.id)
    assert prefs == UserPreferences()  # safe defaults

    updated = svc.update_preferences(
        user.id, UserPreferences(theme=Theme.DARK, units=UnitSystem.HOURS))
    assert updated.theme == Theme.DARK
    # persisted
    assert svc.get_preferences(user.id).units == UnitSystem.HOURS


def test_preferences_unknown_user_raises(svc):
    with pytest.raises(ServiceError):
        svc.get_preferences("nobody")


# ---- currency ----
def test_owner_can_set_currency(svc, owner):
    from schema import Currency
    svc.create_organization("acme", "Acme", owner)
    org = svc.set_organization_currency(
        "acme", owner.id, Currency(code="EUR", symbol="€", name="Euro"))
    assert org.currency.code == "EUR"


def test_viewer_cannot_set_currency(svc, owner):
    from schema import Currency, Role, User
    svc.create_organization("acme", "Acme", owner)
    viewer = User(id="v1", email="v@acme.com")
    svc._repo.save_user(viewer)
    svc.add_member("acme", owner.id, viewer.id, Role.VIEWER)
    with pytest.raises(PermissionError_):
        svc.set_organization_currency(
            "acme", viewer.id, Currency(code="GBP", symbol="£", name="Pound"))


# ---- activity type flows through scheduling ----
def test_activity_type_survives_schedule(svc, owner):
    from schema import Activity, ActivityType
    org, proj = _org_with_project(svc, owner)
    svc.add_activity(org, owner.id, proj,
                     Activity(id="M", name="Gate", duration=0,
                              type=ActivityType.MILESTONE))
    svc.add_activity(org, owner.id, proj,
                     Activity(id="T", name="Work", duration=3, predecessors=["M"]))
    r = svc.schedule(org, owner.id, proj)
    types = {a["id"]: a["type"] for a in r["activities"]}
    assert types["M"] == "milestone"
    assert types["T"] == "task"
