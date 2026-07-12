"""FastAPI server (Milestone 1 — real authentication).

Thin transport layer over ProjectService. Identity now comes from a verified JWT
(self-hosted auth, ADR-0006), not a header: clients sign up / log in to get a
token, then send it as `Authorization: Bearer <token>`. The `current_user`
dependency validates the token and yields the user id, which the service uses to
enforce membership and roles.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles

from schema import (
    Activity, Project, Organization, Role,
    SignupRequest, LoginRequest, AuthResponse,
    UserPreferences, Currency, COMMON_CURRENCIES, EVMResult,
)
from persistence import SQLiteRepository
from services import ProjectService, ServiceError, PermissionError_
from auth import decode_access_token, TokenError

DB_PATH = os.environ.get("MINIP7_DB", "minip7.db")
SECRET = os.environ.get("MINIP7_SECRET", "dev-insecure-secret-change-me")
service = ProjectService(SQLiteRepository(DB_PATH), token_secret=SECRET)

app = FastAPI(
    title="Mini-P7 API",
    version="0.4.0",
    description="Multi-tenant CPM scheduler with self-hosted authentication.",
)

_bearer = HTTPBearer(auto_error=True)


def current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    """Validate the bearer token and return the user id, else 401."""
    try:
        return decode_access_token(creds.credentials, SECRET)
    except TokenError as e:
        raise HTTPException(status_code=401, detail=str(e))


def _guard(fn):
    try:
        return fn()
    except PermissionError_ as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- auth (public) ----
@app.post("/api/auth/signup", response_model=AuthResponse, tags=["auth"])
def signup(body: SignupRequest):
    return _guard(lambda: service.register_user(
        body.email, body.password, body.name, body.organization_name))


@app.post("/api/auth/login", response_model=AuthResponse, tags=["auth"])
def login(body: LoginRequest):
    return _guard(lambda: service.authenticate(body.email, body.password))


# ---- organizations (authenticated) ----
@app.get("/api/organizations", response_model=list[Organization], tags=["orgs"])
def my_organizations(uid: str = Depends(current_user)):
    return _guard(lambda: service.list_my_organizations(uid))


@app.post("/api/organizations/{org_id}/members", response_model=Organization, tags=["orgs"])
def add_member(org_id: str, user_id: str, role: Role = Role.MEMBER,
               uid: str = Depends(current_user)):
    return _guard(lambda: service.add_member(org_id, uid, user_id, role))


@app.put("/api/organizations/{org_id}/currency", response_model=Organization, tags=["orgs"])
def set_currency(org_id: str, body: Currency, uid: str = Depends(current_user)):
    return _guard(lambda: service.set_organization_currency(org_id, uid, body))


# ---- user preferences (authenticated; a user manages their own) ----
@app.get("/api/me/preferences", response_model=UserPreferences, tags=["preferences"])
def get_preferences(uid: str = Depends(current_user)):
    return _guard(lambda: service.get_preferences(uid))


@app.put("/api/me/preferences", response_model=UserPreferences, tags=["preferences"])
def update_preferences(body: UserPreferences, uid: str = Depends(current_user)):
    return _guard(lambda: service.update_preferences(uid, body))


# ---- currency catalogue (public reference data) ----
@app.get("/api/currencies", response_model=list[Currency], tags=["preferences"])
def list_currencies():
    return COMMON_CURRENCIES


# ---- projects (authenticated + org-scoped) ----
@app.get("/api/organizations/{org_id}/projects", response_model=list[Project], tags=["projects"])
def list_projects(org_id: str, uid: str = Depends(current_user)):
    return _guard(lambda: service.list_projects(org_id, uid))


@app.post("/api/organizations/{org_id}/projects", response_model=Project, tags=["projects"])
def create_project(org_id: str, id: str, name: str = "My Project",
                   uid: str = Depends(current_user)):
    return _guard(lambda: service.create_project(org_id, uid, id, name))


@app.get("/api/organizations/{org_id}/projects/{project_id}", response_model=Project, tags=["projects"])
def get_project(org_id: str, project_id: str, uid: str = Depends(current_user)):
    return _guard(lambda: service.get_project(org_id, uid, project_id))


@app.post("/api/organizations/{org_id}/projects/{project_id}/sample",
          response_model=Project, tags=["projects"])
def load_sample(org_id: str, project_id: str, uid: str = Depends(current_user)):
    return _guard(lambda: service.load_sample(org_id, uid, project_id))


@app.post("/api/organizations/{org_id}/projects/{project_id}/activities",
          response_model=Project, tags=["activities"])
def add_activity(org_id: str, project_id: str, activity: Activity,
                 uid: str = Depends(current_user)):
    return _guard(lambda: service.add_activity(org_id, uid, project_id, activity))


@app.put("/api/organizations/{org_id}/projects/{project_id}/activities/{activity_id}",
         response_model=Project, tags=["activities"])
def update_activity(org_id: str, project_id: str, activity_id: str, activity: Activity,
                    uid: str = Depends(current_user)):
    return _guard(lambda: service.update_activity(org_id, uid, project_id, activity))


@app.delete("/api/organizations/{org_id}/projects/{project_id}/activities/{activity_id}",
            response_model=Project, tags=["activities"])
def delete_activity(org_id: str, project_id: str, activity_id: str,
                    uid: str = Depends(current_user)):
    return _guard(lambda: service.delete_activity(org_id, uid, project_id, activity_id))


@app.post("/api/organizations/{org_id}/projects/{project_id}/schedule", tags=["scheduling"])
def schedule(org_id: str, project_id: str, uid: str = Depends(current_user)):
    return _guard(lambda: service.schedule(org_id, uid, project_id))


@app.get("/api/organizations/{org_id}/projects/{project_id}/evm",
         response_model=EVMResult, tags=["scheduling"])
def evm(org_id: str, project_id: str, as_of_day: int,
        uid: str = Depends(current_user)):
    return _guard(lambda: service.evm(org_id, uid, project_id, as_of_day))


# ---- serve the UI ----
_static = Path(__file__).resolve().parents[2] / "static"
if _static.exists():
    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(_static / "index.html")
    @app.get("/login", include_in_schema=False)
    def login_page():
        return FileResponse(_static / "login.html")
    app.mount("/static", StaticFiles(directory=_static), name="static")
