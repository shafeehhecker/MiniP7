import { useState, useCallback } from "react";
import useSWR from "swr";
import type { Activity } from "@minip7/client";
import * as api from "../lib/api";
import type { ScheduleResult } from "../lib/api";

/**
 * Everything one project screen needs: the project itself, the ability to
 * add/edit/delete activities, and the two engine-backed actions (schedule,
 * evm) that Phase 2 built. Scheduling re-fetches the project afterward so
 * the activity table and Gantt always show the CPM fields the server just
 * computed — there is no client-side scheduling logic to keep in sync.
 */
export function useProject(orgId: string | null, projectId: string | null) {
  const key = orgId && projectId ? ["project", orgId, projectId] : null;
  const { data: project, error, isLoading, mutate } = useSWR(
    key,
    () => api.getProject(orgId as string, projectId as string)
  );

  const [scheduleResult, setScheduleResult] = useState<ScheduleResult | null>(null);
  const [scheduling, setScheduling] = useState(false);
  const [scheduleError, setScheduleError] = useState<string | null>(null);

  const schedule = useCallback(async () => {
    if (!orgId || !projectId) return;
    setScheduling(true);
    setScheduleError(null);
    try {
      const result = await api.scheduleProject(orgId, projectId);
      setScheduleResult(result);
      await mutate();
    } catch (e) {
      setScheduleError(e instanceof Error ? e.message : "Could not schedule project.");
    } finally {
      setScheduling(false);
    }
  }, [orgId, projectId, mutate]);

  const addActivity = useCallback(
    async (activity: Activity) => {
      if (!orgId || !projectId) throw new Error("No project selected.");
      await api.addActivity(orgId, projectId, activity);
      setScheduleResult(null); // stale until re-scheduled
      await mutate();
    },
    [orgId, projectId, mutate]
  );

  const updateActivity = useCallback(
    async (activity: Activity) => {
      if (!orgId || !projectId) throw new Error("No project selected.");
      await api.updateActivity(orgId, projectId, activity);
      setScheduleResult(null);
      await mutate();
    },
    [orgId, projectId, mutate]
  );

  const removeActivity = useCallback(
    async (activityId: string) => {
      if (!orgId || !projectId) throw new Error("No project selected.");
      await api.deleteActivity(orgId, projectId, activityId);
      setScheduleResult(null);
      await mutate();
    },
    [orgId, projectId, mutate]
  );

  const loadSample = useCallback(async () => {
    if (!orgId || !projectId) return;
    await api.loadSample(orgId, projectId);
    setScheduleResult(null);
    await mutate();
  }, [orgId, projectId, mutate]);

  return {
    project,
    loading: isLoading,
    error: error as Error | undefined,
    refetch: mutate,
    schedule,
    scheduling,
    scheduleError,
    scheduleResult,
    isScheduled: scheduleResult !== null,
    addActivity,
    updateActivity,
    removeActivity,
    loadSample,
  };
}
