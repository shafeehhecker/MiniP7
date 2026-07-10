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
  predecessors?: string[];
  resource?: string | null;
  description?: string | null;
  status?: ActivityStatus;
  percent_complete?: number;
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

/** A named container of activities, owned by exactly one organization. */
export interface Project {
  id: string;
  organization_id: string;
  name?: string;
  activities?: Activity[];
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
