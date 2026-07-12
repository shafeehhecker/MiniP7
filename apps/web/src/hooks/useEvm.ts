import useSWR from "swr";
import * as api from "../lib/api";

export function useEvm(orgId: string | null, projectId: string | null, asOfDay: number) {
  const key = orgId && projectId ? ["evm", orgId, projectId, asOfDay] : null;
  const { data, error, isLoading } = useSWR(key, () =>
    api.getEvm(orgId as string, projectId as string, asOfDay)
  );
  return { evm: data, loading: isLoading, error: error as Error | undefined };
}
