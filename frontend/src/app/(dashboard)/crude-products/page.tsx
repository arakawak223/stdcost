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
import { useCrudeProducts } from "@/hooks/use-masters";
import { crudeProductTypeLabels } from "@/lib/format";
import { Search } from "lucide-react";

export default function CrudeProductsPage() {
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState("");

  const { data: crudeProducts, isLoading } = useCrudeProducts({
    search: search || undefined,
    crude_type: selectedType || undefined,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">原体マスタ</h2>
        <p className="text-muted-foreground">
          {crudeProducts ? `${crudeProducts.length} 件` : "読込中..."}
          <span className="ml-2 text-xs">原体（原液）= 果物・野菜等を発酵・熟成させた中間製品</span>
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
          <option value="">全タイプ</option>
          <option value="R">レギュラー</option>
          <option value="HI">HI</option>
          <option value="G">ゴールド</option>
          <option value="SP">スペシャル</option>
          <option value="GN">ジンジャー</option>
          <option value="other">その他</option>
        </select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">コード</TableHead>
              <TableHead>原体名</TableHead>
              <TableHead className="w-20">タイプ</TableHead>
              <TableHead className="w-20">仕込期</TableHead>
              <TableHead className="w-20">熟成年</TableHead>
              <TableHead className="w-20">ブレンド</TableHead>
              <TableHead className="w-16">単位</TableHead>
              <TableHead className="w-20">状態</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : crudeProducts && crudeProducts.length > 0 ? (
              crudeProducts.map((cp) => (
                <TableRow key={cp.id}>
                  <TableCell className="font-mono text-sm font-medium">{cp.code}</TableCell>
                  <TableCell>{cp.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {crudeProductTypeLabels[cp.crude_type] || cp.crude_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono">
                    {cp.vintage_year ? `第${cp.vintage_year}期` : "-"}
                  </TableCell>
                  <TableCell className="font-mono">
                    {cp.aging_years !== null ? `${cp.aging_years}年` : "-"}
                  </TableCell>
                  <TableCell>
                    {cp.is_blend ? (
                      <Badge variant="warning">ブレンド</Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>{cp.unit}</TableCell>
                  <TableCell>
                    <Badge variant={cp.is_active ? "success" : "secondary"}>
                      {cp.is_active ? "有効" : "無効"}
                    </Badge>
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
    </div>
  );
}
