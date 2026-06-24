"""FastAPI server (Phase 4).

Exposes the ProjectService over REST. It is a thin transport layer: it validates
input with the schema models, calls services, and serialises the result. All
business logic lives below it (services -> engine), never here.

The OpenAPI spec this produces (at /openapi.json) is the contract from which the
typed TypeScript client in packages/client is generated.

Run:  uvicorn api.main:app --reload   (from apps/api/src)
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from schema import Activity, Project
from persistence import SQLiteProjectRepository
from services import ProjectService, ServiceError

DB_PATH = os.environ.get("MINIP7_DB", "minip7.db")
service = ProjectService(SQLiteProjectRepository(DB_PATH))

app = FastAPI(
    title="Mini-P7 API",
    version="0.1.0",
    description="CPM scheduler — projects, activities, and scheduling.",
)


def _guard(fn):
    try:
        return fn()
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- projects ----
@app.get("/api/projects", response_model=list[Project], tags=["projects"])
def list_projects():
    return service.list_projects()


@app.post("/api/projects", response_model=Project, tags=["projects"])
def create_project(id: str, name: str = "My Project"):
    return _guard(lambda: service.create_project(id, name))


@app.get("/api/projects/{project_id}", response_model=Project, tags=["projects"])
def get_project(project_id: str):
    return _guard(lambda: service.get_project(project_id))


@app.delete("/api/projects/{project_id}", tags=["projects"])
def delete_project(project_id: str):
    _guard(lambda: service.delete_project(project_id))
    return {"deleted": project_id}


@app.post("/api/projects/{project_id}/sample", response_model=Project, tags=["projects"])
def load_sample(project_id: str):
    return _guard(lambda: service.load_sample(project_id))


# ---- activities ----
@app.post("/api/projects/{project_id}/activities", response_model=Project, tags=["activities"])
def add_activity(project_id: str, activity: Activity):
    return _guard(lambda: service.add_activity(project_id, activity))


@app.delete("/api/projects/{project_id}/activities/{activity_id}",
            response_model=Project, tags=["activities"])
def delete_activity(project_id: str, activity_id: str):
    return _guard(lambda: service.delete_activity(project_id, activity_id))


# ---- scheduling ----
@app.post("/api/projects/{project_id}/schedule", tags=["scheduling"])
def schedule(project_id: str):
    return _guard(lambda: service.schedule(project_id))


# ---- serve the zero-build UI ----
_static = Path(__file__).resolve().parents[2] / "static"
if _static.exists():
    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(_static / "index.html")
    app.mount("/", StaticFiles(directory=_static), name="static")
