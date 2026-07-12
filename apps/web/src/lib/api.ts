/**
 * Typed fetch client for the Mini-P7 API.
 *
 * Deliberately thin: one `request()` core that attaches the bearer token,
 * parses JSON, and turns non-2xx responses into `ApiError`. No retry/caching
 * logic lives here — that's what the SWR-based hooks (src/hooks) are for.
 * Every function's return type comes from `@minip7/client`, the same
 * generated types the Python schema produces (ADR-0003), so drift between
 * frontend and backend shapes is a compile error, not a runtime surprise.
 */
import type {
  Activity,
  AuthResponse,
  Currency,
  EVMResult,
  LoginRequest,
  Organization,
  Project,
  SignupRequest,
  UserPreferences,
} from "@minip7/client";

const TOKEN_KEY = "minip7_token";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
  else sessionStorage.removeItem(TOKEN_KEY);
}

async function request<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`/api${path}`, { ...init, headers });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON; keep statusText
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ---- auth ----
export const signup = (body: SignupRequest) =>
  request<AuthResponse>("/auth/signup", { method: "POST", body: JSON.stringify(body) });

export const login = (body: LoginRequest) =>
  request<AuthResponse>("/auth/login", { method: "POST", body: JSON.stringify(body) });

// ---- organizations ----
export const listOrganizations = () => request<Organization[]>("/organizations");

export const setOrganizationCurrency = (orgId: string, currency: Currency) =>
  request<Organization>(`/organizations/${orgId}/currency`, {
    method: "PUT",
    body: JSON.stringify(currency),
  });

// ---- reference data ----
export const listCurrencies = () => request<Currency[]>("/currencies");

// ---- preferences ----
export const getPreferences = () => request<UserPreferences>("/me/preferences");

export const updatePreferences = (body: UserPreferences) =>
  request<UserPreferences>("/me/preferences", { method: "PUT", body: JSON.stringify(body) });

// ---- projects ----
export const listProjects = (orgId: string) =>
  request<Project[]>(`/organizations/${orgId}/projects`);

export const createProject = (orgId: string, id: string, name: string) =>
  request<Project>(
    `/organizations/${orgId}/projects?${new URLSearchParams({ id, name })}`,
    { method: "POST" }
  );

export const getProject = (orgId: string, projectId: string) =>
  request<Project>(`/organizations/${orgId}/projects/${projectId}`);

export const loadSample = (orgId: string, projectId: string) =>
  request<Project>(`/organizations/${orgId}/projects/${projectId}/sample`, {
    method: "POST",
  });

// ---- activities ----
export const addActivity = (orgId: string, projectId: string, activity: Activity) =>
  request<Project>(`/organizations/${orgId}/projects/${projectId}/activities`, {
    method: "POST",
    body: JSON.stringify(activity),
  });

export const updateActivity = (orgId: string, projectId: string, activity: Activity) =>
  request<Project>(
    `/organizations/${orgId}/projects/${projectId}/activities/${activity.id}`,
    { method: "PUT", body: JSON.stringify(activity) }
  );

export const deleteActivity = (orgId: string, projectId: string, activityId: string) =>
  request<Project>(
    `/organizations/${orgId}/projects/${projectId}/activities/${activityId}`,
    { method: "DELETE" }
  );

// ---- scheduling ----
export interface ScheduleResult {
  project_id: string;
  organization_id: string;
  duration: number;
  critical_path: string[];
  activities: Activity[];
}

export const scheduleProject = (orgId: string, projectId: string) =>
  request<ScheduleResult>(`/organizations/${orgId}/projects/${projectId}/schedule`, {
    method: "POST",
  });

export const getEvm = (orgId: string, projectId: string, asOfDay: number) =>
  request<EVMResult>(
    `/organizations/${orgId}/projects/${projectId}/evm?${new URLSearchParams({
      as_of_day: String(asOfDay),
    })}`
  );
