"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { useCostBudgets, useCreateCostBudget, useDeleteCostBudget } from "@/hooks/use-costs";
import { useCostCenters, useFiscalPeriods } from "@/hooks/use-masters";
import { Plus, Trash2 } from "lucide-react";
import { formatCurrency, formatFiscalPeriod } from "@/lib/format";

export default function CostBudgetsPage() {
  const [selectedCcId, setSelectedCcId] = useState<string | undefined>(undefined);
  const { data: budgets, isLoading } = useCostBudgets(
    selectedCcId ? { cost_center_id: selectedCcId } : undefined
  );
  const { data: costCenters } = useCostCenters();
  const { data: periods } = useFiscalPeriods();
  const createBudget = useCreateCostBudget();
  const deleteBudget = useDeleteCostBudget();

  const [showDialog, setShowDialog] = useState(false);
  const [formCcId, setFormCcId] = useState("");
  const [formPeriodId, setFormPeriodId] = useState("");
  const [laborBudget, setLaborBudget] = useState("0");
  const [overheadBudget, setOverheadBudget] = useState("0");
  const [outsourcingBudget, setOutsourcingBudget] = useState("0");

  const ccMap = Object.fromEntries((costCenters || []).map((cc) => [cc.id, cc]));
  const periodMap = Object.fromEntries((periods || []).map((p) => [p.id, p]));

  const handleCreate = async () => {
    await createBudget.mutateAsync({
      cost_center_id: formCcId,
      period_id: formPeriodId,
      labor_budget: laborBudget,
      overhead_budget: overheadBudget,
      outsourcing_budget: outsourcingBudget,
    });
    setShowDialog(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">予算管理</h2>
          <p className="text-muted-foreground">部門×期間の労務費・経費・外注費予算</p>
        </div>
        <Button onClick={() => setShowDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          新規予算
        </Button>
      </div>

      <div className="flex gap-2">
        <Button
          variant={selectedCcId === undefined ? "default" : "outline"}
          size="sm"
          onClick={() => setSelectedCcId(undefined)}
        >
          全部門
        </Button>
        {costCenters
          ?.filter((cc) => cc.center_type !== "indirect")
          .map((cc) => (
            <Button
              key={cc.id}
              variant={selectedCcId === cc.id ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCcId(cc.id)}
            >
              {cc.name}
            </Button>
          ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>予算一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-muted-foreground">読み込み中...</p>
          ) : !budgets?.length ? (
            <p className="text-muted-foreground">予算データがありません</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>部門</TableHead>
                  <TableHead>会計期間</TableHead>
                  <TableHead className="text-right">労務費予算</TableHead>
                  <TableHead className="text-right">経費予算</TableHead>
                  <TableHead className="text-right">外注費予算</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {budgets.map((b) => {
                  const cc = ccMap[b.cost_center_id];
                  const period = periodMap[b.period_id];
                  return (
                    <TableRow key={b.id}>
                      <TableCell>{cc?.name || "-"}</TableCell>
                      <TableCell>
                        {period
                          ? formatFiscalPeriod(period.year, period.month)
                          : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(b.labor_budget)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(b.overhead_budget)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(b.outsourcing_budget)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            if (confirm("この予算を削除しますか？")) {
                              deleteBudget.mutate(b.id);
                            }
                          }}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新規予算登録</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>部門</Label>
              <select
                className="w-full rounded border bg-background px-3 py-2 text-sm"
                value={formCcId}
                onChange={(e) => setFormCcId(e.target.value)}
              >
                <option value="">選択してください</option>
                {costCenters?.map((cc) => (
                  <option key={cc.id} value={cc.id}>
                    {cc.code} - {cc.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>会計期間</Label>
              <select
                className="w-full rounded border bg-background px-3 py-2 text-sm"
                value={formPeriodId}
                onChange={(e) => setFormPeriodId(e.target.value)}
              >
                <option value="">選択してください</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month)}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>労務費予算</Label>
              <Input type="number" value={laborBudget} onChange={(e) => setLaborBudget(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>経費予算</Label>
              <Input type="number" value={overheadBudget} onChange={(e) => setOverheadBudget(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>外注費予算</Label>
              <Input type="number" value={outsourcingBudget} onChange={(e) => setOutsourcingBudget(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>キャンセル</Button>
            <Button onClick={handleCreate} disabled={!formCcId || !formPeriodId || createBudget.isPending}>
              登録
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
