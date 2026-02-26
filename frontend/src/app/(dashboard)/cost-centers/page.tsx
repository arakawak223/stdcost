"use client";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCostCenters } from "@/hooks/use-masters";
import { centerTypeLabels } from "@/lib/format";

export default function CostCentersPage() {
  const { data: costCenters, isLoading } = useCostCenters();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">部門マスタ</h2>
        <p className="text-muted-foreground">
          {costCenters ? `${costCenters.length} 件` : "読込中..."}
        </p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">コード</TableHead>
              <TableHead>部門名</TableHead>
              <TableHead className="w-24">略称</TableHead>
              <TableHead className="w-24">分類</TableHead>
              <TableHead className="w-20">状態</TableHead>
              <TableHead className="w-20">順序</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : costCenters && costCenters.length > 0 ? (
              costCenters.map((cc) => (
                <TableRow key={cc.id}>
                  <TableCell className="font-mono text-sm">{cc.code}</TableCell>
                  <TableCell className="font-medium">
                    {cc.parent_id && <span className="mr-2 text-muted-foreground">└</span>}
                    {cc.name}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{cc.name_short || "-"}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {centerTypeLabels[cc.center_type] || cc.center_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={cc.is_active ? "success" : "secondary"}>
                      {cc.is_active ? "有効" : "無効"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center">{cc.sort_order}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
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
