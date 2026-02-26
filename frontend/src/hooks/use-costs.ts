"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  allocationRulesApi,
  costBudgetsApi,
  standardCostsApi,
  type AllocationRuleCreate,
  type CostBudgetCreate,
} from "@/lib/api-client";

// Allocation Rules
export function useAllocationRules(params?: { is_active?: boolean }) {
  return useQuery({
    queryKey: ["allocation-rules", params],
    queryFn: () => allocationRulesApi.list(params),
  });
}

export function useCreateAllocationRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AllocationRuleCreate) => allocationRulesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allocation-rules"] });
    },
  });
}

export function useDeleteAllocationRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => allocationRulesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allocation-rules"] });
    },
  });
}

// Cost Budgets
export function useCostBudgets(params?: { cost_center_id?: string; period_id?: string }) {
  return useQuery({
    queryKey: ["cost-budgets", params],
    queryFn: () => costBudgetsApi.list(params),
  });
}

export function useCreateCostBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CostBudgetCreate) => costBudgetsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cost-budgets"] });
    },
  });
}

export function useUpdateCostBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CostBudgetCreate> }) =>
      costBudgetsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cost-budgets"] });
    },
  });
}

export function useDeleteCostBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => costBudgetsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cost-budgets"] });
    },
  });
}

// Standard Costs
export function useStandardCosts(params?: { period_id?: string; product_id?: string }) {
  return useQuery({
    queryKey: ["standard-costs", params],
    queryFn: () => standardCostsApi.list(params),
    enabled: !!params?.period_id,
  });
}

export function useCrudeProductStandardCosts(params?: { period_id?: string }) {
  return useQuery({
    queryKey: ["crude-product-standard-costs", params],
    queryFn: () => standardCostsApi.listCrudeProducts(params),
    enabled: !!params?.period_id,
  });
}

export function useCalculateStandardCosts() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { period_id: string; product_ids?: string[]; simulate?: boolean }) =>
      standardCostsApi.calculate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standard-costs"] });
      queryClient.invalidateQueries({ queryKey: ["crude-product-standard-costs"] });
    },
  });
}

export function useSimulateStandardCosts() {
  return useMutation({
    mutationFn: (data: { period_id: string; overrides?: Record<string, unknown> }) =>
      standardCostsApi.simulate(data),
  });
}
