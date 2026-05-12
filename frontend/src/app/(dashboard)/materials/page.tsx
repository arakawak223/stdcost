"use client";

import { useEffect, useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useFiscalPeriods,
  useMaterialStandardCostMutations,
  useMaterialStandardCosts,
  useMaterials,
} from "@/hooks/use-masters";
import type { Material, MaterialStandardCost } from "@/lib/api-client";
import {
  formatCurrency,
  formatFiscalPeriod,
  formatNumber,
  materialCategoryLabels,
  materialTypeLabels,
} from "@/lib/format";
import { Search } from "lucide-react";

export default function MaterialsPage() {
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [periodId, setPeriodId] = useState("");
  const [editing, setEditing] = useState<Material | null>(null);

  const { data: materials, isLoading } = useMaterials({
    search: search || undefined,
    material_type: selectedType || undefined,
    category: selectedCategory || undefined,
  });
  const { data: periods } = useFiscalPeriods();

  const sortedPeriods = useMemo(
    () =>
      periods
        ? [...periods].sort((a, b) => (a.start_date < b.start_date ? 1 : -1))
        : [],
    [periods]
  );

  // 初期表示: 最新期(=39期8か月目 2026/1)をデフォルト選択
  useEffect(() => {
    if (!periodId && sortedPeriods.length > 0) {
      setPeriodId(sortedPeriods[0].id);
    }
  }, [sortedPeriods, periodId]);

  const { data: periodCosts } = useMaterialStandardCosts({
    period_id: periodId || undefined,
  });

  /** material_id → MaterialStandardCost のルックアップ。 */
  const costByMaterial = useMemo(() => {
    const m = new Map<string, MaterialStandardCost>();
    periodCosts?.forEach((c) => m.set(c.material_id, c));
    return m;
  }, [periodCosts]);

  const selectedPeriod = sortedPeriods.find((p) => p.id === periodId);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">原材料マスタ</h2>
        <p className="text-muted-foreground">
          {materials ? `${materials.length} 件` : "読込中..."}
          {selectedPeriod && periodCosts && (
            <span className="ml-3 text-xs">
              （{formatFiscalPeriod(selectedPeriod.year, selectedPeriod.month, selectedPeriod.start_date)} の SC 単価: {periodCosts.length} 件登録）
            </span>
          )}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
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
          <option value="">全種別</option>
          <option value="raw">原料</option>
          <option value="packaging">資材</option>
          <option value="sub_material">副資材</option>
        </select>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="">全カテゴリ</option>
          <option value="fruit">果物</option>
          <option value="vegetable">野菜</option>
          <option value="grain">穀物</option>
          <option value="seaweed">海藻</option>
          <option value="other">その他</option>
        </select>
        <div className="ml-auto flex items-center gap-2">
          <label className="text-xs text-muted-foreground">参照期間:</label>
          <select
            value={periodId}
            onChange={(e) => setPeriodId(e.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">指定なし</option>
            {sortedPeriods.map((p) => (
              <option key={p.id} value={p.id}>
                {formatFiscalPeriod(p.year, p.month, p.start_date)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">コード</TableHead>
              <TableHead>原材料名</TableHead>
              <TableHead className="w-20">種別</TableHead>
              <TableHead className="w-20">カテゴリ</TableHead>
              <TableHead className="w-16">単位</TableHead>
              <TableHead className="w-28 text-right">マスタ単価</TableHead>
              <TableHead className="w-32 text-right">当期SC単価</TableHead>
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
            ) : materials && materials.length > 0 ? (
              materials.map((m) => {
                const cost = costByMaterial.get(m.id);
                return (
                  <TableRow
                    key={m.id}
                    onClick={() => setEditing(m)}
                    className="cursor-pointer hover:bg-muted/50"
                  >
                    <TableCell className="font-mono text-sm">{m.code}</TableCell>
                    <TableCell className="font-medium">{m.name}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {materialTypeLabels[m.material_type] || m.material_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {m.category ? (
                        <Badge variant="outline">
                          {materialCategoryLabels[m.category] || m.category}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>{m.unit}</TableCell>
                    <TableCell className="text-right font-mono text-muted-foreground">
                      {formatCurrency(m.standard_unit_price)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {periodId ? (
                        cost ? (
                          <span>{formatNumber(cost.unit_cost, 2)}</span>
                        ) : (
                          <span className="text-muted-foreground">未登録</span>
                        )
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={m.is_active ? "success" : "secondary"}>
                        {m.is_active ? "有効" : "無効"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                );
              })
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

      {editing && (
        <MaterialStandardCostDialog
          material={editing}
          periodId={periodId}
          periodLabel={
            selectedPeriod
              ? formatFiscalPeriod(
                  selectedPeriod.year,
                  selectedPeriod.month,
                  selectedPeriod.start_date
                )
              : ""
          }
          existingCost={costByMaterial.get(editing.id) ?? null}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}

/** 期別単価編集ダイアログ。
 *  既存レコードがあれば PUT、なければ POST。空欄保存で DELETE。
 */
function MaterialStandardCostDialog({
  material,
  periodId,
  periodLabel,
  existingCost,
  onClose,
}: {
  material: Material;
  periodId: string;
  periodLabel: string;
  existingCost: MaterialStandardCost | null;
  onClose: () => void;
}) {
  const { create, update, remove } = useMaterialStandardCostMutations();
  const [unitCost, setUnitCost] = useState(
    existingCost ? String(existingCost.unit_cost) : ""
  );
  const [notes, setNotes] = useState(existingCost?.notes ?? "");
  const [error, setError] = useState<string | null>(null);

  const pending = create.isPending || update.isPending || remove.isPending;

  const handleSave = async () => {
    setError(null);
    if (!periodId) {
      setError("先に上部の参照期間を選択してください。");
      return;
    }
    const trimmed = unitCost.trim();
    if (!trimmed) {
      setError("単価を入力してください（削除する場合は「削除」ボタン）。");
      return;
    }
    const num = Number(trimmed);
    if (!Number.isFinite(num) || num < 0) {
      setError("正の数値を入力してください。");
      return;
    }
    try {
      if (existingCost) {
        await update.mutateAsync({
          id: existingCost.id,
          data: { unit_cost: trimmed, notes: notes || null },
        });
      } else {
        await create.mutateAsync({
          material_id: material.id,
          period_id: periodId,
          unit_cost: trimmed,
          notes: notes || null,
        });
      }
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存に失敗しました");
    }
  };

  const handleDelete = async () => {
    if (!existingCost) return;
    if (!confirm("この期間の単価レコードを削除します。よろしいですか？")) return;
    setError(null);
    try {
      await remove.mutateAsync(existingCost.id);
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "削除に失敗しました");
    }
  };

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>期別 SC 単価の編集</DialogTitle>
          <DialogDescription>
            <span className="font-mono">{material.code}</span> — {material.name}
            <br />
            参照期間: <strong>{periodLabel || "未選択"}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="rounded-md bg-muted/40 p-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">マスタ単価</span>
              <span className="font-mono">
                {formatCurrency(material.standard_unit_price)} / {material.unit}
              </span>
            </div>
            <div className="mt-1 flex justify-between">
              <span className="text-muted-foreground">期別レコード</span>
              <span className="font-mono">
                {existingCost ? `${formatNumber(existingCost.unit_cost, 4)}（更新）` : "未登録（新規作成）"}
              </span>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">単価（{material.unit}あたり）</label>
            <Input
              type="number"
              step="0.0001"
              value={unitCost}
              onChange={(e) => setUnitCost(e.target.value)}
              placeholder="例: 1380.5"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">備考</label>
            <Input
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="（任意）SC取込元、根拠など"
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <DialogFooter>
          {existingCost && (
            <Button
              type="button"
              variant="destructive"
              onClick={handleDelete}
              disabled={pending}
              className="mr-auto"
            >
              削除
            </Button>
          )}
          <Button type="button" variant="outline" onClick={onClose} disabled={pending}>
            キャンセル
          </Button>
          <Button type="button" onClick={handleSave} disabled={pending}>
            {existingCost ? "更新" : "新規登録"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
