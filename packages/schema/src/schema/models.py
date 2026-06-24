"""
Canonical domain model.
========================
Defined once, in Pydantic v2. This module is the single source of truth for the
domain (ADR-0003): the JSON Schema it exports generates the TypeScript types in
`packages/client`, so Python and TypeScript can never disagree.

The model carries both *input* fields (id, name, duration, predecessors) and the
*computed* CPM fields (ES/EF/LS/LF, floats, criticality). The engine fills the
computed fields in place; they default to 0 / False until a schedule is run.
"""
from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator


class RelationshipType(str, Enum):
    """The four dependency types between activities (see glossary)."""
    FS = "FS"  # finish-to-start (default, most common)
    SS = "SS"  # start-to-start
    FF = "FF"  # finish-to-finish
    SF = "SF"  # start-to-finish


class ActivityStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class Relationship(BaseModel):
    """A typed dependency from one activity to another, with optional lag."""
    predecessor_id: str
    type: RelationshipType = RelationshipType.FS
    lag: int = 0


class Activity(BaseModel):
    """A unit of work with a duration and dependencies — the atom of a schedule.

    Invariant: validates on construction; an invalid activity cannot exist.
    The engine reads ``id``, ``name``, ``duration``, ``predecessors`` and writes
    the computed CPM fields in place.
    """
    id: str
    name: str
    duration: int = Field(ge=0, description="Working days; 0 == milestone.")
    predecessors: List[str] = Field(default_factory=list)
    resource: str | None = None
    description: str | None = None
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    percent_complete: int = Field(default=0, ge=0, le=100)

    # Computed CPM fields (populated by the engine; 0 / False until scheduled).
    ES: int = 0
    EF: int = 0
    LS: int = 0
    LF: int = 0
    total_float: int = 0
    free_float: int = 0
    is_critical: bool = False

    @field_validator("id")
    @classmethod
    def _id_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Activity id must not be blank.")
        return v.strip()

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Activity name must not be blank.")
        return v.strip()

    @field_validator("predecessors")
    @classmethod
    def _no_self_dependency(cls, v: List[str], info) -> List[str]:
        # id may not be available yet during validation ordering; guard defensively.
        own = info.data.get("id")
        if own and own in v:
            raise ValueError(f"Activity '{own}' cannot depend on itself.")
        return v

    def summary(self) -> str:
        tag = "CRITICAL" if self.is_critical else f"float={self.total_float:>3}"
        pred = ",".join(self.predecessors) or "—"
        return (f"[{tag}] {self.id} | {self.name} | dur={self.duration} | "
                f"pred=[{pred}] | ES={self.ES} EF={self.EF} "
                f"LS={self.LS} LF={self.LF} | TF={self.total_float} FF={self.free_float}")


class Project(BaseModel):
    """A named container of activities."""
    id: str
    name: str = "My Project"
    activities: List[Activity] = Field(default_factory=list)
