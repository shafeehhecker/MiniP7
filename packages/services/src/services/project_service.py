"""Project + organization orchestration (Phase 3, multi-tenant).

The use-case layer. It coordinates the engine and repositories to fulfil
application operations, and it enforces tenancy: every project operation is
scoped to an organization, and the caller's membership is checked. It depends on
the engine and the repository *interfaces* — never a concrete database, never the
API or UI (the dependency rule).
"""
from __future__ import annotations

import uuid
from typing import List

from schema import (
    Activity, Project, Organization, User, Membership, Role,
)
from engine import CPMScheduler, SchedulerError
from auth import hash_password, verify_password, create_access_token

__all__ = ["ProjectService", "ServiceError", "PermissionError_"]


class ServiceError(Exception):
    """User-facing service error (bad input, missing entity)."""


class PermissionError_(ServiceError):
    """Raised when a user lacks the role required for an action."""


# Roles allowed to modify (create/edit/delete). Viewers are read-only.
_WRITE_ROLES = {Role.OWNER, Role.ADMIN, Role.MEMBER}


class ProjectService:
    def __init__(self, repo, token_secret: str = "dev-insecure-secret") -> None:
        # repo implements the org, user, and project repository protocols
        self._repo = repo
        self._secret = token_secret

    # ------------------------------------------------------------------
    # Authentication (Milestone 1)
    # ------------------------------------------------------------------
    def register_user(self, email: str, password: str, name: str | None = None,
                      organization_name: str = "My Organization") -> dict:
        """Create a user (with hashed password) and their first organization,
        making them its owner. Returns an access token."""
        if self._repo.get_user_by_email(email.strip().lower()):
            raise ServiceError("An account with that email already exists.")
        user = User(
            id=f"user_{uuid.uuid4().hex[:12]}",
            email=email,
            name=name,
            password_hash=hash_password(password),
        )
        self._repo.save_user(user)
        org = Organization(
            id=f"org_{uuid.uuid4().hex[:12]}",
            name=organization_name,
            memberships=[Membership(user_id=user.id, organization_id="",
                                    role=Role.OWNER)],
        )
        # fix the membership org id now that we have it
        org.memberships[0].organization_id = org.id
        self._repo.save_org(org)
        token = create_access_token(user.id, self._secret)
        return {"access_token": token, "token_type": "bearer",
                "user_id": user.id, "email": user.email,
                "organization_id": org.id}

    def authenticate(self, email: str, password: str) -> dict:
        """Verify credentials and return an access token, else raise."""
        user = self._repo.get_user_by_email(email.strip().lower())
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise ServiceError("Invalid email or password.")
        token = create_access_token(user.id, self._secret)
        orgs = self._repo.list_orgs_for_user(user.id)
        org_id = orgs[0].id if orgs else None
        return {"access_token": token, "token_type": "bearer",
                "user_id": user.id, "email": user.email,
                "organization_id": org_id}

    # ------------------------------------------------------------------
    # Organizations & membership
    # ------------------------------------------------------------------
    def create_organization(self, org_id: str, name: str, owner: User) -> Organization:
        if self._repo.get_org(org_id):
            raise ServiceError(f"Organization '{org_id}' already exists.")
        org = Organization(
            id=org_id, name=name,
            memberships=[Membership(user_id=owner.id, organization_id=org_id,
                                    role=Role.OWNER)],
        )
        self._repo.save_org(org)
        return org

    def add_member(self, org_id: str, actor_id: str, user_id: str,
                   role: Role = Role.MEMBER) -> Organization:
        org = self._get_org(org_id)
        self._require_role(org, actor_id, {Role.OWNER, Role.ADMIN})
        if any(m.user_id == user_id for m in org.memberships):
            raise ServiceError(f"User '{user_id}' is already a member.")
        org.memberships.append(
            Membership(user_id=user_id, organization_id=org_id, role=role)
        )
        self._repo.save_org(org)
        return org

    def list_my_organizations(self, user_id: str) -> List[Organization]:
        return self._repo.list_orgs_for_user(user_id)

    # ------------------------------------------------------------------
    # Projects (all tenant-scoped + permission-checked)
    # ------------------------------------------------------------------
    def list_projects(self, org_id: str, actor_id: str) -> List[Project]:
        org = self._get_org(org_id)
        self._require_member(org, actor_id)
        return self._repo.list_projects_for_org(org_id)

    def create_project(self, org_id: str, actor_id: str,
                       project_id: str, name: str = "My Project") -> Project:
        org = self._get_org(org_id)
        self._require_role(org, actor_id, _WRITE_ROLES)
        if self._repo.get(project_id):
            raise ServiceError(f"Project '{project_id}' already exists.")
        project = Project(id=project_id, organization_id=org_id, name=name)
        self._repo.save(project)
        return project

    def get_project(self, org_id: str, actor_id: str, project_id: str) -> Project:
        org = self._get_org(org_id)
        self._require_member(org, actor_id)
        project = self._repo.get(project_id)
        if not project or project.organization_id != org_id:
            raise ServiceError(f"No project '{project_id}' in this organization.")
        return project

    def add_activity(self, org_id: str, actor_id: str,
                     project_id: str, activity: Activity) -> Project:
        org = self._get_org(org_id)
        self._require_role(org, actor_id, _WRITE_ROLES)
        project = self.get_project(org_id, actor_id, project_id)
        if any(a.id == activity.id for a in project.activities):
            raise ServiceError(f"Activity '{activity.id}' already exists.")
        project.activities.append(activity)
        self._repo.save(project)
        return project

    def update_activity(self, org_id: str, actor_id: str,
                        project_id: str, activity: Activity) -> Project:
        org = self._get_org(org_id)
        self._require_role(org, actor_id, _WRITE_ROLES)
        project = self.get_project(org_id, actor_id, project_id)
        idx = next((i for i, a in enumerate(project.activities)
                    if a.id == activity.id), None)
        if idx is None:
            raise ServiceError(f"No activity '{activity.id}' to update.")
        project.activities[idx] = activity
        self._repo.save(project)
        return project

    def delete_activity(self, org_id: str, actor_id: str,
                        project_id: str, activity_id: str) -> Project:
        org = self._get_org(org_id)
        self._require_role(org, actor_id, _WRITE_ROLES)
        project = self.get_project(org_id, actor_id, project_id)
        before = len(project.activities)
        project.activities = [a for a in project.activities if a.id != activity_id]
        if len(project.activities) == before:
            raise ServiceError(f"No activity '{activity_id}' to delete.")
        self._repo.save(project)
        return project

    def schedule(self, org_id: str, actor_id: str, project_id: str) -> dict:
        project = self.get_project(org_id, actor_id, project_id)
        if not project.activities:
            raise ServiceError("No activities to schedule.")
        acts = {a.id: a for a in project.activities}
        scheduler = CPMScheduler(acts)
        try:
            scheduler.schedule()
        except SchedulerError as e:
            raise ServiceError(str(e))
        self._repo.save(project)
        return {
            "project_id": project.id,
            "organization_id": org_id,
            "duration": scheduler.project_duration(),
            "critical_path": scheduler.get_critical_path(),
            "activities": [a.model_dump() for a in project.activities],
        }

    def load_sample(self, org_id: str, actor_id: str, project_id: str) -> Project:
        org = self._get_org(org_id)
        self._require_role(org, actor_id, _WRITE_ROLES)
        project = self.get_project(org_id, actor_id, project_id)
        project.activities = [
            Activity(id="A", name="Start", duration=2),
            Activity(id="B", name="Foundation", duration=4, predecessors=["A"]),
            Activity(id="C", name="Structure", duration=6, predecessors=["B"]),
            Activity(id="D", name="Electrical", duration=3, predecessors=["B"],
                     resource="Electrical Team"),
            Activity(id="E", name="Finish", duration=2, predecessors=["C", "D"]),
        ]
        self._repo.save(project)
        return project

    # ------------------------------------------------------------------
    # Internal helpers — tenancy & permissions
    # ------------------------------------------------------------------
    def _get_org(self, org_id: str) -> Organization:
        org = self._repo.get_org(org_id)
        if not org:
            raise ServiceError(f"No organization '{org_id}'.")
        return org

    def _membership(self, org: Organization, user_id: str):
        return next((m for m in org.memberships if m.user_id == user_id), None)

    def _require_member(self, org: Organization, user_id: str) -> None:
        if not self._membership(org, user_id):
            raise PermissionError_("You are not a member of this organization.")

    def _require_role(self, org: Organization, actor_id: str, allowed: set) -> None:
        m = self._membership(org, actor_id)
        if not m:
            raise PermissionError_("You are not a member of this organization.")
        if m.role not in allowed:
            raise PermissionError_(
                f"Your role '{m.role.value}' is not permitted to do this."
            )
