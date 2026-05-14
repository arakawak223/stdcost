"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { importsApi } from "@/lib/api-client";

export function useImportBatches(params?: { source_system?: string; period_id?: string }) {
  return useQuery({
    queryKey: ["import-batches", params],
    queryFn: () => importsApi.list(params),
  });
}

export function useImportBatch(id?: string) {
  return useQuery({
    queryKey: ["import-batch", id],
    queryFn: () => importsApi.get(id!),
    enabled: !!id,
  });
}

export function useUploadImport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { file: File; source_system: string; period_id: string }) =>
      importsApi.upload(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["import-batches"] });
    },
  });
}

/** 仕掛品 SC 単価 Excel アップロード。成功後は wip-standard-costs と
 *  在庫評価のキャッシュも invalidate する。
 */
export function useUploadWipSc() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { file: File; period_id: string }) =>
      importsApi.uploadWipSc(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["import-batches"] });
      queryClient.invalidateQueries({ queryKey: ["wip-standard-costs"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations"] });
    },
  });
}
