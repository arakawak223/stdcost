"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reconciliationApi } from "@/lib/api-client";

export function useReconciliationResults(params?: { period_id?: string; status?: string }) {
  return useQuery({
    queryKey: ["reconciliation-results", params],
    queryFn: () => reconciliationApi.listResults(params),
    enabled: !!params?.period_id,
  });
}

export function useReconciliationSummary(period_id?: string) {
  return useQuery({
    queryKey: ["reconciliation-summary", period_id],
    queryFn: () => reconciliationApi.summary(period_id!),
    enabled: !!period_id,
  });
}

export function useRunReconciliation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { period_id: string; threshold?: number }) =>
      reconciliationApi.run(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reconciliation-results"] });
      queryClient.invalidateQueries({ queryKey: ["reconciliation-summary"] });
    },
  });
}
