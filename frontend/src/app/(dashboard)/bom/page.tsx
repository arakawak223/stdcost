"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useBomHeaders, useDeleteBom } from "@/hooks/use-bom";
import { Plus, Trash2 } from "lucide-react";
import type { BomType } from "@/lib/api-client";

const bomTypeLabels: Record<string, string> = {
  raw_material_process: "原体工程",
  product_process: "製品工程",
};

export default function BomListPage() {
  const [bomType, setBomType] = useState<BomType | undefined>(undefined);
  const { data: boms, isLoading } = useBomHeaders(
    bomType ? { bom_type: bomType } : undefined
  );
  const deleteBom = useDeleteBom();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">BOM管理</h2>
          <p className="text-muted-foreground">部品表（Bill of Materials）の管理</p>
        </div>
        <Link href="/bom/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            新規BOM作成
          </Button>
        </Link>
      </div>

      <div className="flex gap-2">
        <Button
          variant={bomType === undefined ? "default" : "outline"}
          size="sm"
          onClick={() => setBomType(undefined)}
        >
          全て
        </Button>
        <Button
          variant={bomType === "raw_material_process" ? "default" : "outline"}
          size="sm"
          onClick={() => setBomType("raw_material_process")}
        >
          原体工程
        </Button>
        <Button
          variant={bomType === "product_process" ? "default" : "outline"}
          size="sm"
          onClick={() => setBomType("product_process")}
        >
          製品工程
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>BOM一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-muted-foreground">読み込み中...</p>
          ) : !boms?.length ? (
            <p className="text-muted-foreground">BOMデータがありません</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>工程</TableHead>
                  <TableHead>出力品目</TableHead>
                  <TableHead>有効日</TableHead>
                  <TableHead>Ver</TableHead>
                  <TableHead>行数</TableHead>
                  <TableHead>歩留率</TableHead>
                  <TableHead>状態</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {boms.map((bom) => (
                  <TableRow key={bom.id}>
                    <TableCell>
                      <Badge variant="outline">
                        {bomTypeLabels[bom.bom_type] || bom.bom_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/bom/${bom.id}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {bom.product
                          ? `${bom.product.code} - ${bom.product.name}`
                          : bom.crude_product_detail
                            ? `${bom.crude_product_detail.code} - ${bom.crude_product_detail.name}`
                            : "-"}
                      </Link>
                    </TableCell>
                    <TableCell>{bom.effective_date}</TableCell>
                    <TableCell>v{bom.version}</TableCell>
                    <TableCell>{bom.lines.length}行</TableCell>
                    <TableCell>{(parseFloat(bom.yield_rate) * 100).toFixed(1)}%</TableCell>
                    <TableCell>
                      <Badge variant={bom.is_active ? "success" : "secondary"}>
                        {bom.is_active ? "有効" : "無効"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          if (confirm("このBOMを削除しますか？")) {
                            deleteBom.mutate(bom.id);
                          }
                        }}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
