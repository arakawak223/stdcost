"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  useProducts,
  useProductCount,
  useProductGroups,
  useCreateProduct,
  useUpdateProduct,
  useDeleteProduct,
} from "@/hooks/use-products";
import { formatNumber, formatDateTime, productTypeLabels } from "@/lib/format";
import type { Product, ProductCreate } from "@/lib/api-client";
import { Plus, Search, Pencil, Trash2, ChevronLeft, ChevronRight } from "lucide-react";

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [selectedGroup, setSelectedGroup] = useState<string>("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editProduct, setEditProduct] = useState<Product | null>(null);
  const perPage = 20;

  const params = {
    page,
    per_page: perPage,
    search: search || undefined,
    product_group: selectedGroup || undefined,
  };

  const { data: products, isLoading } = useProducts(params);
  const { data: countData } = useProductCount({
    search: search || undefined,
    product_group: selectedGroup || undefined,
  });
  const { data: groups } = useProductGroups();
  const createMutation = useCreateProduct();
  const updateMutation = useUpdateProduct();
  const deleteMutation = useDeleteProduct();

  const totalPages = Math.ceil((countData?.count || 0) / perPage);

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data: ProductCreate = {
      code: formData.get("code") as string,
      name: formData.get("name") as string,
      name_short: (formData.get("name_short") as string) || null,
      product_group: (formData.get("product_group") as string) || null,
      product_type: (formData.get("product_type") as string) as ProductCreate["product_type"] || "in_house_product_dept",
      sc_code: (formData.get("sc_code") as string) || null,
      unit: (formData.get("unit") as string) || "個",
      standard_lot_size: (formData.get("standard_lot_size") as string) || "1",
    };
    await createMutation.mutateAsync(data);
    setIsCreateOpen(false);
  };

  const handleUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!editProduct) return;
    const formData = new FormData(e.currentTarget);
    await updateMutation.mutateAsync({
      id: editProduct.id,
      data: {
        name: formData.get("name") as string,
        name_short: (formData.get("name_short") as string) || null,
        product_group: (formData.get("product_group") as string) || null,
        product_type: (formData.get("product_type") as string) as ProductCreate["product_type"],
        sc_code: (formData.get("sc_code") as string) || null,
        unit: formData.get("unit") as string,
        standard_lot_size: formData.get("standard_lot_size") as string,
      },
    });
    setEditProduct(null);
  };

  const handleDelete = async (product: Product) => {
    if (confirm(`「${product.name}」を削除しますか？`)) {
      await deleteMutation.mutateAsync(product.id);
    }
  };

  const productTypeOptions = [
    { value: "semi_finished", label: "半製品" },
    { value: "in_house_product_dept", label: "内製品(製品課)" },
    { value: "in_house_manufacturing", label: "内製品(製造部)" },
    { value: "outsourced_in_house", label: "外注内製" },
    { value: "outsourced", label: "外注品" },
    { value: "special", label: "特殊" },
    { value: "produce", label: "産品" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">製品マスタ</h2>
          <p className="text-muted-foreground">
            {countData ? `${formatNumber(countData.count)} 件` : "読込中..."}
          </p>
        </div>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              新規登録
            </Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle>製品新規登録</DialogTitle>
                <DialogDescription>新しい製品をマスタに登録します</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="code" className="text-right">コード</Label>
                  <Input id="code" name="code" className="col-span-3" required />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">製品名</Label>
                  <Input id="name" name="name" className="col-span-3" required />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name_short" className="text-right">略称</Label>
                  <Input id="name_short" name="name_short" className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="product_type" className="text-right">製品区分</Label>
                  <select id="product_type" name="product_type" defaultValue="in_house_product_dept" className="col-span-3 h-10 rounded-md border border-input bg-background px-3 text-sm">
                    {productTypeOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="sc_code" className="text-right">SCコード</Label>
                  <Input id="sc_code" name="sc_code" className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="product_group" className="text-right">製品群</Label>
                  <Input id="product_group" name="product_group" className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="unit" className="text-right">単位</Label>
                  <Input id="unit" name="unit" defaultValue="個" className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="standard_lot_size" className="text-right">標準ロット</Label>
                  <Input id="standard_lot_size" name="standard_lot_size" type="number" defaultValue="1" className="col-span-3" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "登録中..." : "登録"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="コード・名前で検索..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-9"
          />
        </div>
        <select
          value={selectedGroup}
          onChange={(e) => {
            setSelectedGroup(e.target.value);
            setPage(1);
          }}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="">全製品群</option>
          {groups?.map((g) => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">コード</TableHead>
              <TableHead>製品名</TableHead>
              <TableHead className="w-28">製品区分</TableHead>
              <TableHead className="w-24">SCコード</TableHead>
              <TableHead className="w-24">製品群</TableHead>
              <TableHead className="w-16">単位</TableHead>
              <TableHead className="w-20">状態</TableHead>
              <TableHead className="w-24">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : products && products.length > 0 ? (
              products.map((product) => (
                <TableRow key={product.id}>
                  <TableCell className="font-mono text-sm">{product.code}</TableCell>
                  <TableCell className="font-medium">{product.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {productTypeLabels[product.product_type] || product.product_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono text-sm text-muted-foreground">
                    {product.sc_code || "-"}
                  </TableCell>
                  <TableCell>
                    {product.product_group && (
                      <Badge variant="secondary">{product.product_group}</Badge>
                    )}
                  </TableCell>
                  <TableCell>{product.unit}</TableCell>
                  <TableCell>
                    <Badge variant={product.is_active ? "success" : "secondary"}>
                      {product.is_active ? "有効" : "無効"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setEditProduct(product)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(product)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  データがありません
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {countData?.count} 件中 {(page - 1) * perPage + 1}-
            {Math.min(page * perPage, countData?.count || 0)} 件を表示
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="flex items-center px-3 text-sm">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editProduct} onOpenChange={(open) => !open && setEditProduct(null)}>
        <DialogContent>
          {editProduct && (
            <form onSubmit={handleUpdate}>
              <DialogHeader>
                <DialogTitle>製品編集</DialogTitle>
                <DialogDescription>コード: {editProduct.code}</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-name" className="text-right">製品名</Label>
                  <Input id="edit-name" name="name" defaultValue={editProduct.name} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-name_short" className="text-right">略称</Label>
                  <Input id="edit-name_short" name="name_short" defaultValue={editProduct.name_short || ""} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-product_type" className="text-right">製品区分</Label>
                  <select id="edit-product_type" name="product_type" defaultValue={editProduct.product_type} className="col-span-3 h-10 rounded-md border border-input bg-background px-3 text-sm">
                    {productTypeOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-sc_code" className="text-right">SCコード</Label>
                  <Input id="edit-sc_code" name="sc_code" defaultValue={editProduct.sc_code || ""} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-product_group" className="text-right">製品群</Label>
                  <Input id="edit-product_group" name="product_group" defaultValue={editProduct.product_group || ""} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-unit" className="text-right">単位</Label>
                  <Input id="edit-unit" name="unit" defaultValue={editProduct.unit} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-standard_lot_size" className="text-right">標準ロット</Label>
                  <Input id="edit-standard_lot_size" name="standard_lot_size" type="number" defaultValue={editProduct.standard_lot_size} className="col-span-3" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={updateMutation.isPending}>
                  {updateMutation.isPending ? "更新中..." : "更新"}
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
