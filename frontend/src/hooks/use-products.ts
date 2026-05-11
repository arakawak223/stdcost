"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  productsApi,
  type Product,
  type ProductCreate,
  type ProductUpdate,
} from "@/lib/api-client";

/** マスタ系一覧のデフォルト件数。
 *  現在の products テーブルは711件あるため、全件取得できるよう per_page を大きめに設定。
 */
const DEFAULT_PRODUCTS_PER_PAGE = 2000;

export function useProducts(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  product_group?: string;
  is_active?: boolean;
}) {
  const merged = { per_page: DEFAULT_PRODUCTS_PER_PAGE, ...params };
  return useQuery({
    queryKey: ["products", merged],
    queryFn: () => productsApi.list(merged),
  });
}

export function useProductCount(params?: {
  search?: string;
  product_group?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ["products-count", params],
    queryFn: () => productsApi.count(params),
  });
}

export function useProductGroups() {
  return useQuery({
    queryKey: ["product-groups"],
    queryFn: () => productsApi.groups(),
  });
}

export function useProduct(id: string) {
  return useQuery({
    queryKey: ["product", id],
    queryFn: () => productsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProductCreate) => productsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["products-count"] });
      queryClient.invalidateQueries({ queryKey: ["product-groups"] });
    },
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProductUpdate }) =>
      productsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => productsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["products-count"] });
    },
  });
}
