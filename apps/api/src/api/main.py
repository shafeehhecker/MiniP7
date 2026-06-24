"""FastAPI server (Phase 4, multi-tenant).

Thin transport layer over ProjectService. All business logic and tenancy
enforcement live in the service below it.

AUTH NOTE: real authentication (Milestone 1 / ADR-0006) is not wired yet. For now
the caller identifies themselves with two headers — X-User-Id and X-Org-Id — which
a future auth layer will replace by deriving both from a verified token. The
service already enforces membership and roles, so the security model is in place;
only the identity *source* is temporary.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from schema import Activity, Project, Organization, User, Role
from persistence import SQLiteRepository
from services import ProjectService, ServiceError, PermissionError_

DB_PATH = os.environ.get("MINIP7_DB", "minip7.db")
service = ProjectService(SQLiteRepository(DB_PATH))

app = FastAPI(
    title="Mini-P7 API",
    version="0.2.0",
    description="Multi-tenant CPM scheduler — organizations, projects, scheduling.",
)


def _guard(fn):
    try:
        return fn()
    except PermissionError_ as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- organizations ----
@app.post("/api/organizations", response_model=Organization, tags=["orgs"])
def create_org(id: str, name: str, user_id: str = Header(..., alias="X-User-Id"),
               email: str = Header("user@example.com", alias="X-User-Email")):
    owner = User(id=user_id, email=email)
    return _guard(lambda: service.create_organization(id, name, owner))


@app.post("/api/organizations/{org_id}/members", response_model=Organization, tags=["orgs"])
def add_member(org_id: str, user_id: str, role: Role = Role.MEMBER,
               actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.add_member(org_id, actor_id, user_id, role))


# ---- projects (org-scoped) ----
@app.get("/api/organizations/{org_id}/projects", response_model=list[Project], tags=["projects"])
def list_projects(org_id: str, actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.list_projects(org_id, actor_id))


@app.post("/api/organizations/{org_id}/projects", response_model=Project, tags=["projects"])
def create_project(org_id: str, id: str, name: str = "My Project",
                   actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.create_project(org_id, actor_id, id, name))


@app.get("/api/organizations/{org_id}/projects/{project_id}", response_model=Project, tags=["projects"])
def get_project(org_id: str, project_id: str, actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.get_project(org_id, actor_id, project_id))


@app.post("/api/organizations/{org_id}/projects/{project_id}/sample",
          response_model=Project, tags=["projects"])
def load_sample(org_id: str, project_id: str, actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.load_sample(org_id, actor_id, project_id))


@app.post("/api/organizations/{org_id}/projects/{project_id}/activities",
          response_model=Project, tags=["activities"])
def add_activity(org_id: str, project_id: str, activity: Activity,
                 actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.add_activity(org_id, actor_id, project_id, activity))


@app.post("/api/organizations/{org_id}/projects/{project_id}/schedule", tags=["scheduling"])
def schedule(org_id: str, project_id: str, actor_id: str = Header(..., alias="X-User-Id")):
    return _guard(lambda: service.schedule(org_id, actor_id, project_id))


# ---- serve the zero-build UI ----
_static = Path(__file__).resolve().parents[2] / "static"
if _static.exists():
    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(_static / "index.html")
    app.mount("/", StaticFiles(directory=_static), name="static")
