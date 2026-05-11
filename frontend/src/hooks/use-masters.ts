"use client";

import { useQuery } from "@tanstack/react-query";
import {
  costCentersApi,
  materialsApi,
  crudeProductsApi,
  contractorsApi,
  fiscalPeriodsApi,
} from "@/lib/api-client";

export function useCostCenters(params?: { center_type?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: ["cost-centers", params],
    queryFn: () => costCentersApi.list(params),
  });
}

/** マスタ系一覧のデフォルト件数。
 *  業務上の総件数(製品711/原体256/原材料213)を全件取得できるよう
 *  per_page を大きめに設定。将来的に件数が爆発するならページネーションUIに切替。
 */
const DEFAULT_MASTER_PER_PAGE = 2000;

export function useMaterials(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  material_type?: string;
  category?: string;
  is_active?: boolean;
}) {
  const merged = { per_page: DEFAULT_MASTER_PER_PAGE, ...params };
  return useQuery({
    queryKey: ["materials", merged],
    queryFn: () => materialsApi.list(merged),
  });
}

export function useCrudeProducts(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  crude_type?: string;
  sc_consolidation_key?: string;
  vintage_year?: number;
  is_active?: boolean;
}) {
  const merged = { per_page: DEFAULT_MASTER_PER_PAGE, ...params };
  return useQuery({
    queryKey: ["crude-products", merged],
    queryFn: () => crudeProductsApi.list(merged),
  });
}

export function useCrudeProductConsolidation(periodId?: string) {
  return useQuery({
    queryKey: ["crude-products-consolidation", periodId],
    queryFn: () => crudeProductsApi.consolidationSummary(periodId),
  });
}

export function useContractors(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  is_active?: boolean;
}) {
  const merged = { per_page: DEFAULT_MASTER_PER_PAGE, ...params };
  return useQuery({
    queryKey: ["contractors", merged],
    queryFn: () => contractorsApi.list(merged),
  });
}

export function useFiscalPeriods(params?: { year?: number; status?: string }) {
  return useQuery({
    queryKey: ["fiscal-periods", params],
    queryFn: () => fiscalPeriodsApi.list(params),
  });
}
