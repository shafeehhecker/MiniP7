"""Storage-agnostic repository contracts (Phase 3, extended for multi-tenancy).

Defines *what* persistence must do, not *how*. Services depend on these
interfaces; concrete adapters (SQLite, in-memory) implement them. This is the seam
that makes storage swappable.

Multi-tenancy (ADR-0005): projects are always scoped to an organization. The
repository never returns a project list without an org id, so cross-tenant data
leakage is structurally hard.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from schema import Organization, Project


class OrganizationRepository(Protocol):
    def get_org(self, org_id: str) -> Optional[Organization]: ...
    def save_org(self, org: Organization) -> None: ...
    def list_orgs_for_user(self, user_id: str) -> List[Organization]: ...


class ProjectRepository(Protocol):
    def list_projects_for_org(self, org_id: str) -> List[Project]: ...
    def get(self, project_id: str) -> Optional[Project]: ...
    def save(self, project: Project) -> None: ...
    def delete(self, project_id: str) -> None: ...


class InMemoryRepository:
    """A fake adapter for tests — same contract, no I/O. Implements both
    repository protocols (orgs + projects)."""

    def __init__(self) -> None:
        self._orgs: Dict[str, Organization] = {}
        self._projects: Dict[str, Project] = {}

    # ---- organizations ----
    def get_org(self, org_id: str) -> Optional[Organization]:
        return self._orgs.get(org_id)

    def save_org(self, org: Organization) -> None:
        self._orgs[org.id] = org

    def list_orgs_for_user(self, user_id: str) -> List[Organization]:
        return [o for o in self._orgs.values()
                if any(m.user_id == user_id for m in o.memberships)]

    # ---- projects ----
    def list_projects_for_org(self, org_id: str) -> List[Project]:
        return [p for p in self._projects.values() if p.organization_id == org_id]

    def get(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)

    def save(self, project: Project) -> None:
        self._projects[project.id] = project

    def delete(self, project_id: str) -> None:
        self._projects.pop(project_id, None)
