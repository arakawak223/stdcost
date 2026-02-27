"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { varianceApi } from "@/lib/api-client";

export function useVarianceRecords(params?: {
  period_id?: string;
  product_id?: string;
  cost_element?: string;
  is_flagged?: boolean;
}) {
  return useQuery({
    queryKey: ["variance-records", params],
    queryFn: () => varianceApi.list(params),
    enabled: !!params?.period_id,
  });
}

export function useVarianceSummary(period_id?: string) {
  return useQuery({
    queryKey: ["variance-summary", period_id],
    queryFn: () => varianceApi.summary(period_id!),
    enabled: !!period_id,
  });
}

export function useRunVarianceAnalysis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { period_id: string; product_ids?: string[]; threshold_percent?: number }) =>
      varianceApi.analyze(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["variance-records"] });
      queryClient.invalidateQueries({ queryKey: ["variance-summary"] });
    },
  });
}

export function useUpdateVarianceRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { is_flagged?: boolean; flag_reason?: string; notes?: string };
    }) => varianceApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["variance-records"] });
      queryClient.invalidateQueries({ queryKey: ["variance-summary"] });
    },
  });
}
