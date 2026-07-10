/* AUTO-GENERATED — DO NOT EDIT.
 *
 * Generated from packages/schema (the single source of truth, ADR-0003) by
 * tooling/codegen/generate_ts.py. Regenerate with:
 *
 *     python tooling/codegen/generate_ts.py
 *
 * CI regenerates and diffs this file; any drift fails the build.
 */


/** How an activity behaves in the schedule (see ADR-0008 and the glossary). */
export enum ActivityType {
  TASK = "task",
  MILESTONE = "milestone",
  LEVEL_OF_EFFORT = "level_of_effort",
  SUMMARY = "summary",
}

export enum ActivityStatus {
  NOT_STARTED = "not_started",
  IN_PROGRESS = "in_progress",
  COMPLETE = "complete",
}

/** The four dependency types between activities (see glossary). */
export enum RelationshipType {
  FS = "FS",
  SS = "SS",
  FF = "FF",
  SF = "SF",
}

/** The unit a user sees durations in. The engine always computes in days; */
export enum UnitSystem {
  DAYS = "days",
  HOURS = "hours",
}

/** How calendar dates are rendered for a user. Takes full effect once the */
export enum DateFormat {
  ISO = "iso",
  US = "us",
  EU = "eu",
}

/** The user's preferred colour theme. ``SYSTEM`` follows the OS setting. */
export enum Theme {
  LIGHT = "light",
  DARK = "dark",
  SYSTEM = "system",
}

/** A member's role within an organization. Drives authorization. */
export enum Role {
  OWNER = "owner",
  ADMIN = "admin",
  MEMBER = "member",
  VIEWER = "viewer",
}

/** A unit of work with a duration and dependencies — the atom of a schedule. */
export interface Activity {
  id: string;
  name: string;
  /** Working days; 0 == milestone. */
  duration: number;
  type?: ActivityType;
  /** Convenience form: predecessor ids, implying FS with 0 lag. */
  predecessors?: string[];
  /** Typed dependencies (FS/SS/FF/SF with lag). Canonical form; kept in sync with `predecessors` (ADR-0011). */
  relationships?: Relationship[];
  resource?: string | null;
  description?: string | null;
  status?: ActivityStatus;
  percent_complete?: number;
  /** Budget at completion for this activity, in the organization's currency. */
  budget?: number;
  /** Actual cost incurred to date (ACWP contribution). */
  actual_cost?: number;
  ES?: number;
  EF?: number;
  LS?: number;
  LF?: number;
  total_float?: number;
  free_float?: number;
  is_critical?: boolean;
}

/** A typed dependency from one activity to another, with optional lag. */
export interface Relationship {
  predecessor_id: string;
  type?: RelationshipType;
  lag?: number;
}

/** Working-time definition: which weekdays work, which dates don't. */
export interface Calendar {
  /** Weekdays that count as working days (0=Mon .. 6=Sun). */
  working_days?: number[];
  /** Specific dates that are non-working regardless of weekday. */
  holidays?: string[];
}

/** Earned-value snapshot of a scheduled project as of a status day. */
export interface EVMResult {
  /** Status day, in working days from day 0. */
  as_of_day: number;
  /** Budget at completion: total budget. */
  bac: number;
  /** Planned value (BCWS): budgeted cost of work scheduled. */
  pv: number;
  /** Earned value (BCWP): budgeted cost of work performed. */
  ev: number;
  /** Actual cost (ACWP): money spent to date. */
  ac: number;
  /** Schedule variance: EV - PV (negative = behind). */
  sv: number;
  /** Cost variance: EV - AC (negative = over budget). */
  cv: number;
  /** Schedule performance index: EV / PV. */
  spi: number | null;
  /** Cost performance index: EV / AC. */
  cpi: number | null;
  /** Estimate at completion: BAC / CPI. */
  eac: number | null;
  /** Estimate to complete: EAC - AC. */
  etc: number | null;
  /** Variance at completion: BAC - EAC. */
  vac: number | null;
}

/** A named container of activities, owned by exactly one organization. */
export interface Project {
  id: string;
  organization_id: string;
  name?: string;
  activities?: Activity[];
  /** The real date of working day 0. None = undated project. */
  start_date?: string | null;
  calendar?: Calendar;
}

/** A tenant: a company or team that owns projects and has members. */
export interface Organization {
  id: string;
  name: string;
  memberships?: Membership[];
  currency?: Currency;
}

/** A person. Identity, a hashed password, and display preferences. */
export interface User {
  id: string;
  email: string;
  name?: string | null;
  password_hash?: string | null;
  preferences?: UserPreferences;
}

/** One user's display settings. Defaults are safe for a brand-new user. */
export interface UserPreferences {
  units?: UnitSystem;
  date_format?: DateFormat;
  theme?: Theme;
}

/** Links a User to an Organization with a Role. The join is where roles live — */
export interface Membership {
  user_id: string;
  organization_id: string;
  role?: Role;
}

/** An ISO 4217 currency: a 3-letter code, a display symbol, and a name. */
export interface Currency {
  /** ISO 4217 code, e.g. 'USD'. */
  code: string;
  /** Display symbol, e.g. '$'. */
  symbol: string;
  /** Human name, e.g. 'US Dollar'. */
  name: string;
}

/** Payload to register a new user (and their first organization). */
export interface SignupRequest {
  email: string;
  /** At least 8 characters. */
  password: string;
  name?: string | null;
  organization_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

/** Returned on successful signup or login. */
export interface AuthResponse {
  access_token: string;
  token_type?: string;
  user_id: string;
  email: string;
  organization_id?: string | null;
}
