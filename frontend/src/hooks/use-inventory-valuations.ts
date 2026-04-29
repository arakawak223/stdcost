"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { inventoryValuationsApi, type InventoryCategory } from "@/lib/api-client";

export function useInventoryValuations(params?: {
  period_id?: string;
  category?: InventoryCategory;
  warehouse_name?: string;
  item_code?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["inventory-valuations", params],
    queryFn: () => inventoryValuationsApi.list(params),
    enabled: !!params?.period_id,
  });
}

export function useValuationSummary(period_id?: string) {
  return useQuery({
    queryKey: ["inventory-valuations-summary", period_id],
    queryFn: () => inventoryValuationsApi.summary(period_id!),
    enabled: !!period_id,
  });
}

export function useProductInventoryFlow(period_id?: string, prior_period_id?: string) {
  return useQuery({
    queryKey: ["inventory-product-flow", period_id, prior_period_id],
    queryFn: () => inventoryValuationsApi.productFlow(period_id!, prior_period_id),
    enabled: !!period_id,
  });
}

export function useRecalculateValuation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (period_id: string) => inventoryValuationsApi.recalculate(period_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations-summary"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-product-flow"] });
    },
  });
}

export function useUploadInventory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      file: File;
      period_id: string;
      sheet_name?: string;
      source_system?: string;
    }) => inventoryValuationsApi.uploadInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations-summary"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-product-flow"] });
      queryClient.invalidateQueries({ queryKey: ["import-batches"] });
    },
  });
}
