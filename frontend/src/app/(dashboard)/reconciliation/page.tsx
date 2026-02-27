"use client";

import { useState, useMemo } from "react";
import { CheckCircle2, AlertTriangle, HelpCircle, Scale } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { useFiscalPeriods } from "@/hooks/use-masters";
import { useProducts } from "@/hooks/use-products";
import { useRunReconciliation } from "@/hooks/use-reconciliation";
import { formatCurrency, formatFiscalPeriod, sourceSystemLabels, reconciliationStatusLabels } from "@/lib/format";
import type { ReconcileResponse } from "@/lib/api-client";

const statusVariant: Record<string, "default" | "secondary" | "success" | "warning" | "outline"> = {
  matched: "success",
  unmatched: "warning",
  discrepancy: "warning",
};

const statusIcon: Record<string, typeof CheckCircle2> = {
  matched: CheckCircle2,
  unmatched: HelpCircle,
  discrepancy: AlertTriangle,
};

export default function ReconciliationPage() {
  const [periodId, setPeriodId] = useState("");
  const [threshold, setThreshold] = useState("1000");
  const [result, setResult] = useState<ReconcileResponse | null>(null);

  const { data: periods } = useFiscalPeriods();
  const { data: products } = useProducts();
  const runReconciliation = useRunReconciliation();

  const productMap = useMemo(() => {
    const m = new Map<string, string>();
    products?.forEach((p) => m.set(p.id, p.name));
    return m;
  }, [products]);

  const handleRun = async () => {
    if (!periodId) return;
    const res = await runReconciliation.mutateAsync({
      period_id: periodId,
      threshold: parseFloat(threshold),
    });
    setResult(res);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Scale className="h-6 w-6" />
        突合チェック
      </h1>

      {/* Controls */}
      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">会計期間</label>
          <select
            className="rounded-md border px-3 py-2 text-sm"
            value={periodId}
            onChange={(e) => setPeriodId(e.target.value)}
          >
            <option value="">選択してください</option>
            {periods?.map((p) => (
              <option key={p.id} value={p.id}>
                {formatFiscalPeriod(p.year, p.month)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">閾値 (円)</label>
          <Input
            type="number"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            className="w-32"
          />
        </div>
        <Button
          onClick={handleRun}
          disabled={!periodId || runReconciliation.isPending}
        >
          {runReconciliation.isPending ? "突合実行中..." : "突合実行"}
        </Button>
      </div>

      {runReconciliation.error && (
        <p className="text-sm text-destructive">{(runReconciliation.error as Error).message}</p>
      )}

      {/* Summary Cards */}
      {result && (
        <>
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground">合計</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{result.summary.total}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  一致
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-green-600">{result.summary.matched}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
                  <HelpCircle className="h-4 w-4 text-yellow-600" />
                  未照合
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-yellow-600">{result.summary.unmatched}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  不一致
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-red-600">{result.summary.discrepancy}</p>
              </CardContent>
            </Card>
          </div>

          {/* Results Table */}
          {result.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>エンティティ</TableHead>
                  <TableHead>ソースA</TableHead>
                  <TableHead>ソースB</TableHead>
                  <TableHead className="text-right">値A</TableHead>
                  <TableHead className="text-right">値B</TableHead>
                  <TableHead className="text-right">差額</TableHead>
                  <TableHead>ステータス</TableHead>
                  <TableHead>備考</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.results.map((r) => {
                  const StatusIcon = statusIcon[r.status] || HelpCircle;
                  return (
                    <TableRow key={r.id}>
                      <TableCell className="font-medium">
                        {r.entity_type === "product"
                          ? productMap.get(r.entity_id) || r.entity_id.slice(0, 8)
                          : r.entity_id.slice(0, 8)}
                      </TableCell>
                      <TableCell>{sourceSystemLabels[r.source_a] || r.source_a}</TableCell>
                      <TableCell>{sourceSystemLabels[r.source_b] || r.source_b}</TableCell>
                      <TableCell className="text-right">
                        {r.value_a ? formatCurrency(r.value_a) : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {r.value_b ? formatCurrency(r.value_b) : "-"}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {r.difference ? formatCurrency(r.difference) : "-"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusVariant[r.status] || "secondary"} className="flex w-fit items-center gap-1">
                          <StatusIcon className="h-3 w-3" />
                          {reconciliationStatusLabels[r.status] || r.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {r.notes || "-"}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </>
      )}
    </div>
  );
}
