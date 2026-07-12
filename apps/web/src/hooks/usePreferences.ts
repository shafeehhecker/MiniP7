import useSWR from "swr";
import type { UserPreferences } from "@minip7/client";
import * as api from "../lib/api";
import { useAuth } from "../context/AuthContext";

export function usePreferences() {
  const { isAuthenticated } = useAuth();
  const { data, error, isLoading, mutate } = useSWR(
    isAuthenticated ? "preferences" : null,
    () => api.getPreferences()
  );

  async function save(prefs: UserPreferences) {
    const updated = await api.updatePreferences(prefs);
    await mutate(updated, false);
    return updated;
  }

  return {
    preferences: data,
    loading: isLoading,
    error: error as Error | undefined,
    save,
  };
}
