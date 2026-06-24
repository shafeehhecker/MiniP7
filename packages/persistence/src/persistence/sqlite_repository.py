"""SQLite adapter implementing the org + project repositories (Phase 3).

Stores orgs and projects as JSON rows. Projects carry an organization_id column
so listing is always tenant-scoped (ADR-0005). Postgres would be another adapter
behind the same interface.
"""
from __future__ import annotations

import sqlite3
from typing import List, Optional

from schema import Organization, Project


class SQLiteRepository:
    def __init__(self, db_path: str = "minip7.db") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS organizations (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS projects ("
            "id TEXT PRIMARY KEY, organization_id TEXT NOT NULL, data TEXT NOT NULL)"
        )
        self._conn.commit()

    # ---- organizations ----
    def get_org(self, org_id: str) -> Optional[Organization]:
        row = self._conn.execute(
            "SELECT data FROM organizations WHERE id = ?", (org_id,)
        ).fetchone()
        return Organization.model_validate_json(row[0]) if row else None

    def save_org(self, org: Organization) -> None:
        self._conn.execute(
            "INSERT INTO organizations (id, data) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
            (org.id, org.model_dump_json()),
        )
        self._conn.commit()

    def list_orgs_for_user(self, user_id: str) -> List[Organization]:
        rows = self._conn.execute("SELECT data FROM organizations").fetchall()
        orgs = [Organization.model_validate_json(r[0]) for r in rows]
        return [o for o in orgs if any(m.user_id == user_id for m in o.memberships)]

    # ---- projects ----
    def list_projects_for_org(self, org_id: str) -> List[Project]:
        rows = self._conn.execute(
            "SELECT data FROM projects WHERE organization_id = ?", (org_id,)
        ).fetchall()
        return [Project.model_validate_json(r[0]) for r in rows]

    def get(self, project_id: str) -> Optional[Project]:
        row = self._conn.execute(
            "SELECT data FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return Project.model_validate_json(row[0]) if row else None

    def save(self, project: Project) -> None:
        self._conn.execute(
            "INSERT INTO projects (id, organization_id, data) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET organization_id = excluded.organization_id, "
            "data = excluded.data",
            (project.id, project.organization_id, project.model_dump_json()),
        )
        self._conn.commit()

    def delete(self, project_id: str) -> None:
        self._conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self._conn.commit()
