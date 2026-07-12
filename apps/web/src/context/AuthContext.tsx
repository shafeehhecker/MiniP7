import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import type { LoginRequest, SignupRequest } from "@minip7/client";
import * as api from "../lib/api";
import { getToken, setToken } from "../lib/api";

interface CurrentUser {
  userId: string;
  email: string;
  organizationId: string | null;
}

interface AuthContextValue {
  user: CurrentUser | null;
  isAuthenticated: boolean;
  login: (body: LoginRequest) => Promise<void>;
  signup: (body: SignupRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const USER_KEY = "minip7_user";

function loadStoredUser(): CurrentUser | null {
  const raw = sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(loadStoredUser);

  const applyAuth = useCallback(
    (res: { access_token: string; user_id: string; email: string; organization_id?: string | null }) => {
      setToken(res.access_token);
      const current: CurrentUser = {
        userId: res.user_id,
        email: res.email,
        organizationId: res.organization_id ?? null,
      };
      sessionStorage.setItem(USER_KEY, JSON.stringify(current));
      setUser(current);
    },
    []
  );

  const login = useCallback(
    async (body: LoginRequest) => {
      applyAuth(await api.login(body));
    },
    [applyAuth]
  );

  const signup = useCallback(
    async (body: SignupRequest) => {
      applyAuth(await api.signup(body));
    },
    [applyAuth]
  );

  const logout = useCallback(() => {
    setToken(null);
    sessionStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: !!getToken() && !!user, login, signup, logout }),
    [user, login, signup, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
