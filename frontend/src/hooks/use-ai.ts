"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { aiApi, type ReviewStatus } from "@/lib/api-client";

export function useAIExplanations(params?: { context_type?: string; review_status?: string }) {
  return useQuery({
    queryKey: ["ai-explanations", params],
    queryFn: () => aiApi.listExplanations(params),
  });
}

export function useExplainVariance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variance_record_id: string) => aiApi.explainVariance(variance_record_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-explanations"] });
    },
  });
}

export function useExplainPeriod() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (period_id: string) => aiApi.explainPeriod(period_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-explanations"] });
    },
  });
}

export function useAskQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { question: string; context_type?: string; context_id?: string }) =>
      aiApi.ask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-explanations"] });
    },
  });
}

export function useUpdateAIExplanation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { review_status?: ReviewStatus; reviewer_notes?: string };
    }) => aiApi.updateExplanation(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-explanations"] });
    },
  });
}
