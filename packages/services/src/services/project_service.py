"""Project orchestration (Phase 3).

The use-case layer: it coordinates the engine and a repository to fulfil
application operations (create project, add activity, schedule). It depends on
the engine and the persistence *interface* — never on a concrete database, never
on the API or UI (the dependency rule).
"""
from __future__ import annotations

from typing import List

from schema import Activity, Project
from engine import CPMScheduler, SchedulerError
from persistence.repository import ProjectRepository

__all__ = ["ProjectService", "ServiceError"]


class ServiceError(Exception):
    """User-facing service error (bad input, missing entity)."""


class ProjectService:
    def __init__(self, repo: ProjectRepository) -> None:
        self._repo = repo

    # ---- projects ----
    def list_projects(self) -> List[Project]:
        return self._repo.list_projects()

    def create_project(self, project_id: str, name: str = "My Project") -> Project:
        if self._repo.get(project_id):
            raise ServiceError(f"Project '{project_id}' already exists.")
        project = Project(id=project_id, name=name)
        self._repo.save(project)
        return project

    def get_project(self, project_id: str) -> Project:
        project = self._repo.get(project_id)
        if not project:
            raise ServiceError(f"No project '{project_id}'.")
        return project

    def delete_project(self, project_id: str) -> None:
        self.get_project(project_id)
        self._repo.delete(project_id)

    # ---- activities ----
    def add_activity(self, project_id: str, activity: Activity) -> Project:
        project = self.get_project(project_id)
        if any(a.id == activity.id for a in project.activities):
            raise ServiceError(f"Activity '{activity.id}' already exists.")
        project.activities.append(activity)
        self._repo.save(project)
        return project

    def delete_activity(self, project_id: str, activity_id: str) -> Project:
        project = self.get_project(project_id)
        before = len(project.activities)
        project.activities = [a for a in project.activities if a.id != activity_id]
        if len(project.activities) == before:
            raise ServiceError(f"No activity '{activity_id}'.")
        self._repo.save(project)
        return project

    # ---- scheduling ----
    def schedule(self, project_id: str) -> dict:
        project = self.get_project(project_id)
        if not project.activities:
            raise ServiceError("No activities to schedule.")
        acts = {a.id: a for a in project.activities}
        scheduler = CPMScheduler(acts)
        try:
            scheduler.schedule()
        except SchedulerError as e:
            raise ServiceError(str(e))
        self._repo.save(project)  # persist computed CPM fields
        return {
            "project_id": project.id,
            "duration": scheduler.project_duration(),
            "critical_path": scheduler.get_critical_path(),
            "activities": [a.model_dump() for a in project.activities],
        }

    def load_sample(self, project_id: str) -> Project:
        """Replace the project's activities with the canonical demo network."""
        project = self.get_project(project_id)
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
