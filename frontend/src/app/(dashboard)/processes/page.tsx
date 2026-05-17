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
import { useProcesses } from "@/hooks/use-masters";

export default function ProcessesPage() {
  const { data: processes, isLoading } = useProcesses();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">工程マスタ</h2>
        <p className="text-muted-foreground">
          {processes ? `${processes.length} 件` : "読込中..."} —
          原液発酵プロセス上の各工程(仕込・添加混合・調合・ろ過・圧搾・I/C・工程ロス)
        </p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">コード</TableHead>
              <TableHead>工程名</TableHead>
              <TableHead className="w-20">順序</TableHead>
              <TableHead className="w-20">状態</TableHead>
              <TableHead>備考</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : processes && processes.length > 0 ? (
              processes.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-mono text-sm">{p.code}</TableCell>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell className="text-right tabular-nums">{p.sort_order}</TableCell>
                  <TableCell>
                    <Badge variant={p.is_active ? "success" : "secondary"}>
                      {p.is_active ? "有効" : "無効"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{p.notes || "-"}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
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
