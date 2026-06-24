"""Storage-agnostic repository contract (Phase 3).

Defines *what* persistence must do, not *how*. Services depend on this interface;
concrete adapters (SQLite, in-memory) implement it. This is the seam that makes
storage swappable (ADR rationale: computation, storage, transport are independent).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from schema import Project


class ProjectRepository(Protocol):
    def list_projects(self) -> List[Project]: ...
    def get(self, project_id: str) -> Optional[Project]: ...
    def save(self, project: Project) -> None: ...
    def delete(self, project_id: str) -> None: ...


class InMemoryProjectRepository:
    """A fake adapter for tests — same contract, no I/O."""

    def __init__(self) -> None:
        self._store: Dict[str, Project] = {}

    def list_projects(self) -> List[Project]:
        return list(self._store.values())

    def get(self, project_id: str) -> Optional[Project]:
        return self._store.get(project_id)

    def save(self, project: Project) -> None:
        self._store[project.id] = project

    def delete(self, project_id: str) -> None:
        self._store.pop(project_id, None)
