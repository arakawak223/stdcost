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

/** 製品増減内訳表アップロード。InventoryMovement と在庫評価キャッシュを invalidate。 */
export function useUploadProductMovements() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      file: File;
      period_id: string;
      delete_existing?: boolean;
    }) => importsApi.uploadProductMovements(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["import-batches"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-movements"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-product-flow"] });
    },
  });
}

/** 2.9原液在庫アップロード。crude_products と在庫評価キャッシュを invalidate。 */
export function useUploadCrudeInventory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      file: File;
      period_id: string;
      delete_existing?: boolean;
      skip_zero_stock?: boolean;
    }) => importsApi.uploadCrudeInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["import-batches"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations-summary"] });
      queryClient.invalidateQueries({ queryKey: ["crude-products"] });
      queryClient.invalidateQueries({ queryKey: ["crude-products-consolidation"] });
    },
  });
}

/** 決算用SC原材料アップロード。materials マスタと在庫評価キャッシュを invalidate。 */
export function useUploadRawMaterialInventory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      file: File;
      period_id: string;
      delete_existing?: boolean;
      skip_zero_stock?: boolean;
      update_master_price?: boolean;
    }) => importsApi.uploadRawMaterialInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["import-batches"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-valuations-summary"] });
      queryClient.invalidateQueries({ queryKey: ["materials"] });
      queryClient.invalidateQueries({ queryKey: ["material-standard-costs"] });
    },
  });
}
