"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useFiscalPeriods } from "@/hooks/use-masters";
import { formatJpDate, periodStatusLabels } from "@/lib/format";

export default function FiscalPeriodsPage() {
  const [selectedYear, setSelectedYear] = useState<number | undefined>();
  const { data: periods, isLoading } = useFiscalPeriods({
    year: selectedYear,
  });

  const years = periods
    ? [...new Set(periods.map((p) => p.year))].sort((a, b) => b - a)
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">会計期間</h2>
        <p className="text-muted-foreground">
          {periods ? `${periods.length} 件` : "読込中..."}
        </p>
      </div>

      <div className="flex items-center gap-4">
        <select
          value={selectedYear || ""}
          onChange={(e) =>
            setSelectedYear(e.target.value ? Number(e.target.value) : undefined)
          }
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="">全期</option>
          {years.map((y) => (
            <option key={y} value={y}>
              第{y}期
            </option>
          ))}
        </select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">期</TableHead>
              <TableHead className="w-16">月</TableHead>
              <TableHead>開始日</TableHead>
              <TableHead>終了日</TableHead>
              <TableHead className="w-28">ステータス</TableHead>
              <TableHead>備考</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : periods && periods.length > 0 ? (
              periods.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-mono">第{p.year}期</TableCell>
                  <TableCell className="font-mono">第{p.month}月</TableCell>
                  <TableCell>{formatJpDate(p.start_date)}</TableCell>
                  <TableCell>{formatJpDate(p.end_date)}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        p.status === "open"
                          ? "success"
                          : p.status === "closing"
                            ? "warning"
                            : "secondary"
                      }
                    >
                      {periodStatusLabels[p.status] || p.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {p.notes || "-"}
                  </TableCell>
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
