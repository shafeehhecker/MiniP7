"""SQLite adapter for ProjectRepository (Phase 3).

Stores each project as one JSON row keyed by id. Simple, dependency-light, and
sufficient for single-node use; Postgres would be another adapter behind the same
interface. Serialisation goes through the Pydantic models, so the stored shape is
always the canonical schema.
"""
from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from schema import Project


class SQLiteProjectRepository:
    def __init__(self, db_path: str = "minip7.db") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )
        self._conn.commit()

    def list_projects(self) -> List[Project]:
        rows = self._conn.execute("SELECT data FROM projects").fetchall()
        return [Project.model_validate_json(r[0]) for r in rows]

    def get(self, project_id: str) -> Optional[Project]:
        row = self._conn.execute(
            "SELECT data FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return Project.model_validate_json(row[0]) if row else None

    def save(self, project: Project) -> None:
        self._conn.execute(
            "INSERT INTO projects (id, data) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
            (project.id, project.model_dump_json()),
        )
        self._conn.commit()

    def delete(self, project_id: str) -> None:
        self._conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self._conn.commit()
