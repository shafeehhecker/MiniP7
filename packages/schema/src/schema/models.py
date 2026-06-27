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

from pydantic import BaseModel, Field, field_validator, model_validator


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


class ActivityType(str, Enum):
    """How an activity behaves in the schedule (see ADR-0008 and the glossary).

    Two types are fully scheduled today:

    - ``TASK`` — an ordinary unit of work with its own duration. The default.
    - ``MILESTONE`` — a zero-duration marker for a point in time (a deliverable,
      a gate). Its duration is required to be 0.

    Two further types are recognised and stored, but their *special* scheduling
    behaviour is deferred (see ADR-0008); until then the engine schedules them
    like a task:

    - ``LEVEL_OF_EFFORT`` — sustained work whose span is driven by other
      activities (e.g. project management). Faithful scheduling needs typed
      successor relationships, which are not yet implemented.
    - ``SUMMARY`` — a roll-up of the activities beneath a WBS node. Faithful
      scheduling needs the WBS hierarchy, which is not yet implemented.
    """
    TASK = "task"
    MILESTONE = "milestone"
    LEVEL_OF_EFFORT = "level_of_effort"
    SUMMARY = "summary"


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

    The ``type`` (see :class:`ActivityType`) classifies the activity. A
    ``MILESTONE`` must have ``duration == 0``; this is enforced here, so an
    inconsistent milestone cannot be constructed.
    """
    id: str
    name: str
    duration: int = Field(ge=0, description="Working days; 0 == milestone.")
    type: ActivityType = ActivityType.TASK
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

    @model_validator(mode="after")
    def _milestone_has_zero_duration(self) -> "Activity":
        # A milestone marks a point in time; it cannot consume working days.
        if self.type == ActivityType.MILESTONE and self.duration != 0:
            raise ValueError(
                "A milestone activity must have duration 0 "
                f"(got {self.duration})."
            )
        return self

    def summary(self) -> str:
        tag = "CRITICAL" if self.is_critical else f"float={self.total_float:>3}"
        pred = ",".join(self.predecessors) or "—"
        return (f"[{tag}] {self.id} | {self.name} | {self.type.value} | "
                f"dur={self.duration} | pred=[{pred}] | ES={self.ES} EF={self.EF} "
                f"LS={self.LS} LF={self.LF} | TF={self.total_float} FF={self.free_float}")


# ---------------------------------------------------------------------------
# Multi-tenancy (see ADR-0005)
# ---------------------------------------------------------------------------
# The product serves small teams: a company (Organization) owns its projects,
# and people (Users) belong to the company via a Membership that carries a Role.
# Every Project belongs to exactly one Organization, so data is always scoped to
# a tenant. This boundary is the spine of the product and is designed in from the
# start rather than retrofitted.


class Role(str, Enum):
    """A member's role within an organization. Drives authorization."""
    OWNER = "owner"      # full control, incl. billing and deleting the org
    ADMIN = "admin"      # manage members and all projects
    MEMBER = "member"    # create and edit projects
    VIEWER = "viewer"    # read-only


# ---------------------------------------------------------------------------
# User preferences (see ADR-0007)
# ---------------------------------------------------------------------------
# Per-user display settings. They never affect the *computed* schedule (the
# engine always works in abstract working days); they only change how values are
# presented to one user. They are embedded in the User so they travel with
# identity and need no separate store.


class UnitSystem(str, Enum):
    """The unit a user sees durations in. The engine always computes in days;
    this is presentation only. ``HOURS`` assumes an 8-hour working day."""
    DAYS = "days"
    HOURS = "hours"


class DateFormat(str, Enum):
    """How calendar dates are rendered for a user. Takes full effect once the
    calendar feature maps day-offsets to real dates; stored now so the choice
    is preserved."""
    ISO = "iso"  # 2026-06-27
    US = "us"    # 06/27/2026
    EU = "eu"    # 27/06/2026


class Theme(str, Enum):
    """The user's preferred colour theme. ``SYSTEM`` follows the OS setting."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class UserPreferences(BaseModel):
    """One user's display settings. Defaults are safe for a brand-new user."""
    units: UnitSystem = UnitSystem.DAYS
    date_format: DateFormat = DateFormat.ISO
    theme: Theme = Theme.SYSTEM


class User(BaseModel):
    """A person. Identity, a hashed password, and display preferences.

    The password is stored only as a bcrypt hash (never plaintext), produced by
    the auth commons. A user may belong to several organizations via memberships.
    """
    id: str
    email: str
    name: str | None = None
    password_hash: str | None = None  # set at registration; never the plaintext
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    @field_validator("email")
    @classmethod
    def _email_shape(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address.")
        return v


class SignupRequest(BaseModel):
    """Payload to register a new user (and their first organization)."""
    email: str
    password: str = Field(min_length=8, description="At least 8 characters.")
    name: str | None = None
    organization_name: str = "My Organization"


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    """Returned on successful signup or login."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    organization_id: str | None = None


class Membership(BaseModel):
    """Links a User to an Organization with a Role. The join is where roles live —
    the same person can be an admin in one org and a viewer in another."""
    user_id: str
    organization_id: str
    role: Role = Role.MEMBER


# ---------------------------------------------------------------------------
# Currency (see ADR-0009)
# ---------------------------------------------------------------------------
# An organization picks the currency its costs are expressed in. Cost rollups
# and earned-value are not built yet, so currency is a display setting today;
# it is modelled now so the choice is captured and ready when costs land.


class Currency(BaseModel):
    """An ISO 4217 currency: a 3-letter code, a display symbol, and a name."""
    code: str = Field(description="ISO 4217 code, e.g. 'USD'.")
    symbol: str = Field(description="Display symbol, e.g. '$'.")
    name: str = Field(description="Human name, e.g. 'US Dollar'.")

    @field_validator("code")
    @classmethod
    def _code_shape(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency code must be 3 letters (ISO 4217).")
        return v

    @classmethod
    def default(cls) -> "Currency":
        return cls(code="USD", symbol="$", name="US Dollar")


# A small catalogue for pickers. Not exhaustive — a starting set of common
# currencies. The API exposes this so the UI needn't hard-code it.
COMMON_CURRENCIES: List[Currency] = [
    Currency(code="USD", symbol="$", name="US Dollar"),
    Currency(code="EUR", symbol="€", name="Euro"),
    Currency(code="GBP", symbol="£", name="British Pound"),
    Currency(code="QAR", symbol="ر.ق", name="Qatari Riyal"),
    Currency(code="JPY", symbol="¥", name="Japanese Yen"),
    Currency(code="INR", symbol="₹", name="Indian Rupee"),
    Currency(code="AUD", symbol="A$", name="Australian Dollar"),
    Currency(code="CAD", symbol="C$", name="Canadian Dollar"),
]


class Organization(BaseModel):
    """A tenant: a company or team that owns projects and has members."""
    id: str
    name: str
    memberships: List[Membership] = Field(default_factory=list)
    currency: Currency = Field(default_factory=Currency.default)


class Project(BaseModel):
    """A named container of activities, owned by exactly one organization."""
    id: str
    organization_id: str
    name: str = "My Project"
    activities: List[Activity] = Field(default_factory=list)
