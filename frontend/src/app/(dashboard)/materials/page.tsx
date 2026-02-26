"use client";

import { useState } from "react";
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
import { useMaterials } from "@/hooks/use-masters";
import { formatCurrency, materialTypeLabels, materialCategoryLabels } from "@/lib/format";
import { Search } from "lucide-react";

export default function MaterialsPage() {
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  const { data: materials, isLoading } = useMaterials({
    search: search || undefined,
    material_type: selectedType || undefined,
    category: selectedCategory || undefined,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">原材料マスタ</h2>
        <p className="text-muted-foreground">
          {materials ? `${materials.length} 件` : "読込中..."}
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="コード・名前で検索..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="">全種別</option>
          <option value="raw">原料</option>
          <option value="packaging">資材</option>
          <option value="sub_material">副資材</option>
        </select>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="">全カテゴリ</option>
          <option value="fruit">果物</option>
          <option value="vegetable">野菜</option>
          <option value="grain">穀物</option>
          <option value="seaweed">海藻</option>
          <option value="other">その他</option>
        </select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">コード</TableHead>
              <TableHead>原材料名</TableHead>
              <TableHead className="w-20">種別</TableHead>
              <TableHead className="w-20">カテゴリ</TableHead>
              <TableHead className="w-16">単位</TableHead>
              <TableHead className="w-32 text-right">標準単価</TableHead>
              <TableHead className="w-20">状態</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : materials && materials.length > 0 ? (
              materials.map((m) => (
                <TableRow key={m.id}>
                  <TableCell className="font-mono text-sm">{m.code}</TableCell>
                  <TableCell className="font-medium">{m.name}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {materialTypeLabels[m.material_type] || m.material_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {m.category ? (
                      <Badge variant="outline">
                        {materialCategoryLabels[m.category] || m.category}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>{m.unit}</TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrency(m.standard_unit_price)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={m.is_active ? "success" : "secondary"}>
                      {m.is_active ? "有効" : "無効"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  データがありません
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
