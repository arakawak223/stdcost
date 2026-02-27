"use client";

import { useQuery } from "@tanstack/react-query";
import { actualCostsApi } from "@/lib/api-client";

export function useActualCosts(params?: {
  period_id?: string;
  product_id?: string;
  cost_center_id?: string;
}) {
  return useQuery({
    queryKey: ["actual-costs", params],
    queryFn: () => actualCostsApi.list(params),
    enabled: !!params?.period_id,
  });
}

export function useCrudeProductActualCosts(params?: {
  period_id?: string;
  crude_product_id?: string;
}) {
  return useQuery({
    queryKey: ["crude-product-actual-costs", params],
    queryFn: () => actualCostsApi.listCrudeProducts(params),
    enabled: !!params?.period_id,
  });
}
