"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  bomApi,
  type BomHeader,
  type BomHeaderCreate,
  type BomHeaderUpdate,
} from "@/lib/api-client";

export function useBomHeaders(params?: {
  product_id?: string;
  crude_product_id?: string;
  bom_type?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ["bom-headers", params],
    queryFn: () => bomApi.list(params),
  });
}

export function useBomHeader(id: string) {
  return useQuery({
    queryKey: ["bom-header", id],
    queryFn: () => bomApi.get(id),
    enabled: !!id,
  });
}

export function useCreateBom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BomHeaderCreate) => bomApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bom-headers"] });
    },
  });
}

export function useUpdateBom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BomHeaderUpdate }) =>
      bomApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bom-headers"] });
      queryClient.invalidateQueries({ queryKey: ["bom-header"] });
    },
  });
}

export function useDeleteBom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bomApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bom-headers"] });
    },
  });
}
