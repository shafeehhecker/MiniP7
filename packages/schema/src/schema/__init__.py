"""Canonical domain model — the single source of truth (Phase 1).

Defined once in Pydantic v2; JSON Schema exported for TypeScript generation
(see ADR-0003). Every other package imports its types from here.
"""
from .models import (  # noqa: F401
    Activity,
    Relationship,
    RelationshipType,
    Project,
    ActivityStatus,
    Organization,
    User,
    Role,
    Membership,
)

__all__ = [
    "Activity",
    "Relationship",
    "RelationshipType",
    "Project",
    "ActivityStatus",
    "Organization",
    "User",
    "Role",
    "Membership",
]
