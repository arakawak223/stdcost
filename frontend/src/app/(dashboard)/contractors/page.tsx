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
import { useContractors } from "@/hooks/use-masters";

export default function ContractorsPage() {
  const { data: contractors, isLoading } = useContractors();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">外注先マスタ</h2>
        <p className="text-muted-foreground">
          {contractors ? `${contractors.length} 件` : "読込中..."}
        </p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">コード</TableHead>
              <TableHead>外注先名</TableHead>
              <TableHead className="w-24">略称</TableHead>
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
            ) : contractors && contractors.length > 0 ? (
              contractors.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono text-sm">{c.code}</TableCell>
                  <TableCell className="font-medium">{c.name}</TableCell>
                  <TableCell className="text-muted-foreground">{c.name_short || "-"}</TableCell>
                  <TableCell>
                    <Badge variant={c.is_active ? "success" : "secondary"}>
                      {c.is_active ? "有効" : "無効"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{c.notes || "-"}</TableCell>
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
