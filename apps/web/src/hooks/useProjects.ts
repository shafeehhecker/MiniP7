import useSWR from "swr";
import * as api from "../lib/api";

export function useProjects(orgId: string | null) {
  const { data, error, isLoading, mutate } = useSWR(
    orgId ? ["projects", orgId] : null,
    () => api.listProjects(orgId as string)
  );

  async function createProject(id: string, name: string) {
    if (!orgId) throw new Error("No organization selected.");
    const project = await api.createProject(orgId, id, name);
    await mutate();
    return project;
  }

  return {
    projects: data ?? [],
    loading: isLoading,
    error: error as Error | undefined,
    createProject,
    refetch: mutate,
  };
}
