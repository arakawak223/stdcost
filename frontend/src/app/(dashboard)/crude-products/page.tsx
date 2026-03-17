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
          <optgroup label="仕込み工程">
            <option value="R1">R1 一次仕込み</option>
            <option value="R2">R2 二次仕込み</option>
            <option value="R3">R3 三次仕込み</option>
            <option value="R">R レギュラー</option>
          </optgroup>
          <optgroup label="R派生工程">
            <option value="Rri">Rリ（リンゴ添加）</option>
            <option value="RB">RB ブレンド</option>
            <option value="Rma">Rマルベリー</option>
            <option value="Rshi">Rシ（生姜系）</option>
            <option value="RG">Rジンジャー</option>
            <option value="RGI">RGI</option>
            <option value="FEB">FEB</option>
          </optgroup>
          <optgroup label="HI系">
            <option value="HI">HI</option>
            <option value="HIA">HI-A</option>
            <option value="HIB">HI-B</option>
            <option value="HIR">HIR</option>
            <option value="HIBkai">HIB海</option>
          </optgroup>
          <optgroup label="その他原液">
            <option value="B">B</option>
            <option value="G">ゴールド</option>
            <option value="GA">GA</option>
            <option value="GB">GB</option>
            <option value="O">O</option>
            <option value="X">X</option>
            <option value="XC">XC</option>
            <option value="BM">BM</option>
            <option value="FB">FB</option>
          </optgroup>
          <optgroup label="製品用仕掛品">
            <option value="P">P（定番）</option>
            <option value="PX">PX</option>
            <option value="PXA">PXA</option>
            <option value="MP">MP マルベリー</option>
            <option value="GP">GP ジンジャープラス</option>
            <option value="LPA">LPA</option>
            <option value="PE">PE（生姜系）</option>
            <option value="T">T（畜産用）</option>
            <option value="RX">RX（植物用）</option>
            <option value="plant">植物用ブレンド</option>
          </optgroup>
          <option value="other">その他</option>
        </select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">コード</TableHead>
              <TableHead>原体名</TableHead>
              <TableHead className="w-28">タイプ</TableHead>
              <TableHead className="w-16">工程</TableHead>
              <TableHead className="w-20">仕込期</TableHead>
              <TableHead className="w-16">単位</TableHead>
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
                  <TableCell className="font-mono text-center">
                    {cp.process_stage ?? "-"}
                  </TableCell>
                  <TableCell className="font-mono">
                    {cp.vintage_year ? `第${cp.vintage_year}期` : "-"}
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
