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

export function useMaterials(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  material_type?: string;
  category?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ["materials", params],
    queryFn: () => materialsApi.list(params),
  });
}

export function useCrudeProducts(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  crude_type?: string;
  vintage_year?: number;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ["crude-products", params],
    queryFn: () => crudeProductsApi.list(params),
  });
}

export function useContractors(params?: { search?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: ["contractors", params],
    queryFn: () => contractorsApi.list(params),
  });
}

export function useFiscalPeriods(params?: { year?: number; status?: string }) {
  return useQuery({
    queryKey: ["fiscal-periods", params],
    queryFn: () => fiscalPeriodsApi.list(params),
  });
}
