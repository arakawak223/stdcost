"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
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
import { useAllocationRules, useCreateAllocationRule, useDeleteAllocationRule } from "@/hooks/use-costs";
import { useCostCenters } from "@/hooks/use-masters";
import { Plus, Trash2 } from "lucide-react";
import type { AllocationBasis } from "@/lib/api-client";

const basisLabels: Record<string, string> = {
  production_hours: "直接生産時間",
  raw_material_quantity: "原料使用数量",
  crude_quantity: "原体数量",
  weight_based: "重量基準",
  manual: "手動設定",
};

export default function AllocationRulesPage() {
  const { data: rules, isLoading } = useAllocationRules();
  const { data: costCenters } = useCostCenters();
  const createRule = useCreateAllocationRule();
  const deleteRule = useDeleteAllocationRule();

  const [showDialog, setShowDialog] = useState(false);
  const [name, setName] = useState("");
  const [sourceCcId, setSourceCcId] = useState("");
  const [basis, setBasis] = useState<AllocationBasis>("raw_material_quantity");
  const [targets, setTargets] = useState<{ target_cost_center_id: string; ratio: string }[]>([]);

  const ccMap = Object.fromEntries((costCenters || []).map((cc) => [cc.id, cc]));

  const handleCreate = async () => {
    await createRule.mutateAsync({
      name,
      source_cost_center_id: sourceCcId,
      basis,
      targets,
    });
    setShowDialog(false);
    setName("");
    setSourceCcId("");
    setTargets([]);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">配賦ルール</h2>
          <p className="text-muted-foreground">間接費の配賦基準と按分率の管理</p>
        </div>
        <Button onClick={() => setShowDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          新規ルール
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>配賦ルール一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-muted-foreground">読み込み中...</p>
          ) : !rules?.length ? (
            <p className="text-muted-foreground">配賦ルールがありません</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ルール名</TableHead>
                  <TableHead>配賦元部門</TableHead>
                  <TableHead>配賦基準</TableHead>
                  <TableHead>ターゲット数</TableHead>
                  <TableHead>状態</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rules.map((rule) => (
                  <TableRow key={rule.id}>
                    <TableCell className="font-medium">{rule.name}</TableCell>
                    <TableCell>
                      {rule.source_cost_center?.name || ccMap[rule.source_cost_center_id]?.name || "-"}
                    </TableCell>
                    <TableCell>{basisLabels[rule.basis] || rule.basis}</TableCell>
                    <TableCell>{rule.targets.length}件</TableCell>
                    <TableCell>
                      <Badge variant={rule.is_active ? "success" : "secondary"}>
                        {rule.is_active ? "有効" : "無効"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          if (confirm("この配賦ルールを削除しますか？")) {
                            deleteRule.mutate(rule.id);
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

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新規配賦ルール</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>ルール名</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="例: 製造部労務費配賦" />
            </div>
            <div className="space-y-2">
              <Label>配賦元部門</Label>
              <select
                className="w-full rounded border bg-background px-3 py-2 text-sm"
                value={sourceCcId}
                onChange={(e) => setSourceCcId(e.target.value)}
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
              <Label>配賦基準</Label>
              <select
                className="w-full rounded border bg-background px-3 py-2 text-sm"
                value={basis}
                onChange={(e) => setBasis(e.target.value as AllocationBasis)}
              >
                {Object.entries(basisLabels).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>ターゲット部門</Label>
              {targets.map((t, i) => (
                <div key={i} className="flex gap-2">
                  <select
                    className="flex-1 rounded border bg-background px-2 py-1 text-sm"
                    value={t.target_cost_center_id}
                    onChange={(e) => {
                      const updated = [...targets];
                      updated[i] = { ...updated[i], target_cost_center_id: e.target.value };
                      setTargets(updated);
                    }}
                  >
                    <option value="">部門選択</option>
                    {costCenters?.map((cc) => (
                      <option key={cc.id} value={cc.id}>{cc.name}</option>
                    ))}
                  </select>
                  <Input
                    type="number"
                    step="0.0001"
                    value={t.ratio}
                    onChange={(e) => {
                      const updated = [...targets];
                      updated[i] = { ...updated[i], ratio: e.target.value };
                      setTargets(updated);
                    }}
                    placeholder="按分率"
                    className="w-24"
                  />
                  <Button variant="ghost" size="sm" onClick={() => setTargets(targets.filter((_, j) => j !== i))}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setTargets([...targets, { target_cost_center_id: "", ratio: "1.0" }])}
              >
                <Plus className="mr-1 h-4 w-4" />
                ターゲット追加
              </Button>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>キャンセル</Button>
            <Button onClick={handleCreate} disabled={!name || !sourceCcId || createRule.isPending}>
              作成
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
