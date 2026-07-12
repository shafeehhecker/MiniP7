import useSWR from "swr";
import * as api from "../lib/api";
import { useAuth } from "../context/AuthContext";

export function useOrganizations() {
  const { isAuthenticated } = useAuth();
  const { data, error, isLoading, mutate } = useSWR(
    isAuthenticated ? "organizations" : null,
    () => api.listOrganizations()
  );
  return {
    organizations: data ?? [],
    loading: isLoading,
    error: error as Error | undefined,
    refetch: mutate,
  };
}
