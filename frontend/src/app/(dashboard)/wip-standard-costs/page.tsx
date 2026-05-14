"use client";

import { useEffect, useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
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
  useWipStandardCostMutations,
  useWipStandardCosts,
} from "@/hooks/use-masters";
import type { WipStandardCost } from "@/lib/api-client";
import { formatFiscalPeriod, formatNumber } from "@/lib/format";
import { Plus, Search } from "lucide-react";

export default function WipStandardCostsPage() {
  const [periodId, setPeriodId] = useState("");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<WipStandardCost | "new" | null>(null);

  const { data: periods } = useFiscalPeriods();
  const sortedPeriods = useMemo(
    () =>
      periods
        ? [...periods].sort((a, b) => (a.start_date < b.start_date ? 1 : -1))
        : [],
    [periods]
  );

  // 初期表示: 最新期 (=39期8か月目 2026/1) を選択
  useEffect(() => {
    if (!periodId && sortedPeriods.length > 0) {
      setPeriodId(sortedPeriods[0].id);
    }
  }, [sortedPeriods, periodId]);

  const { data: costs, isLoading } = useWipStandardCosts({
    period_id: periodId || undefined,
  });

  const filtered = useMemo(() => {
    if (!costs) return [];
    const q = search.trim();
    return q
      ? costs.filter((c) => c.consolidation_key.includes(q))
      : costs;
  }, [costs, search]);

  const total = useMemo(() => {
    if (!costs) return null;
    return costs.reduce((sum, c) => sum + Number(c.unit_cost), 0);
  }, [costs]);

  const selectedPeriod = sortedPeriods.find((p) => p.id === periodId);
  const periodLabel = selectedPeriod
    ? formatFiscalPeriod(
        selectedPeriod.year,
        selectedPeriod.month,
        selectedPeriod.start_date
      )
    : "";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">仕掛品 SC 単価</h2>
        <p className="text-muted-foreground">
          名寄せキー × 期間 で管理する仕掛品(半製品)の標準単価。
          <br />
          データソース:{" "}
          <span className="font-mono">docs/reference/決算用SC仕掛品.xlsx</span>{" "}
          → 取込は <code>scripts/import_wip_sc.py</code> または「データ取込」ページから。
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="キーで検索 (B / BM / FB ...)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
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
          <Button
            type="button"
            size="sm"
            onClick={() => setEditing("new")}
            disabled={!periodId}
          >
            <Plus className="mr-1 h-4 w-4" />
            新規キー
          </Button>
        </div>
      </div>

      {periodId && costs && (
        <div className="rounded-md bg-muted/40 p-3 text-sm">
          <div className="flex items-center justify-between">
            <span>
              {periodLabel} —{" "}
              <strong>{costs.length}</strong> 件のキー登録 (合計単価:{" "}
              <span className="font-mono">{formatNumber(total ?? 0, 2)}</span> ¥/kg)
            </span>
            <span className="text-xs text-muted-foreground">
              行をクリックして編集 / 削除
            </span>
          </div>
        </div>
      )}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">名寄せキー</TableHead>
              <TableHead className="w-28 text-right">前工程費</TableHead>
              <TableHead className="w-28 text-right">原材料費</TableHead>
              <TableHead className="w-28 text-right">労務費</TableHead>
              <TableHead className="w-28 text-right">経費</TableHead>
              <TableHead className="w-28 text-right">SC単価</TableHead>
              <TableHead>備考</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {!periodId ? (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                  上部から参照期間を選択してください。
                </TableCell>
              </TableRow>
            ) : isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                  読込中...
                </TableCell>
              </TableRow>
            ) : filtered.length > 0 ? (
              filtered.map((c) => (
                <TableRow
                  key={c.id}
                  onClick={() => setEditing(c)}
                  className="cursor-pointer hover:bg-muted/50"
                >
                  <TableCell className="font-mono font-medium">{c.consolidation_key}</TableCell>
                  <TableCell className="text-right font-mono text-muted-foreground">
                    {formatNumber(c.pre_process_cost, 2)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-muted-foreground">
                    {formatNumber(c.material_cost, 2)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-muted-foreground">
                    {formatNumber(c.labor_cost, 2)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-muted-foreground">
                    {formatNumber(c.expense_cost, 2)}
                  </TableCell>
                  <TableCell className="text-right font-mono font-semibold">
                    {formatNumber(c.unit_cost, 2)}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {c.notes ?? "-"}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                  該当データがありません
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {editing && periodId && (
        <WipStandardCostDialog
          periodId={periodId}
          periodLabel={periodLabel}
          existing={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}

/** 仕掛品 SC 単価 編集ダイアログ。
 *  内訳 4列 (前工程費/原材料費/労務費/経費) と合計 (unit_cost) を編集。
 *  unit_cost が手入力されない限り、内訳合計を自動算出。
 */
function WipStandardCostDialog({
  periodId,
  periodLabel,
  existing,
  onClose,
}: {
  periodId: string;
  periodLabel: string;
  existing: WipStandardCost | null;
  onClose: () => void;
}) {
  const { create, update, remove } = useWipStandardCostMutations();
  const [key, setKey] = useState(existing?.consolidation_key ?? "");
  const [pre, setPre] = useState(existing ? String(existing.pre_process_cost) : "0");
  const [mat, setMat] = useState(existing ? String(existing.material_cost) : "0");
  const [labor, setLabor] = useState(existing ? String(existing.labor_cost) : "0");
  const [exp, setExp] = useState(existing ? String(existing.expense_cost) : "0");
  const [totalManual, setTotalManual] = useState(
    existing ? String(existing.unit_cost) : ""
  );
  const [notes, setNotes] = useState(existing?.notes ?? "");
  const [error, setError] = useState<string | null>(null);

  const pending = create.isPending || update.isPending || remove.isPending;

  // 内訳合計 (手動入力 totalManual が空のときに自動セット)
  const breakdownSum = useMemo(() => {
    const sum = [pre, mat, labor, exp].reduce(
      (acc, v) => acc + (Number(v) || 0),
      0
    );
    return sum;
  }, [pre, mat, labor, exp]);

  const effectiveTotal = totalManual.trim() === "" ? breakdownSum : Number(totalManual);

  const handleSave = async () => {
    setError(null);
    const trimmedKey = key.trim();
    if (!trimmedKey) {
      setError("名寄せキーを入力してください。");
      return;
    }
    if (!Number.isFinite(effectiveTotal) || effectiveTotal < 0) {
      setError("単価合計は0以上の数値である必要があります。");
      return;
    }
    const payload = {
      unit_cost: String(effectiveTotal),
      pre_process_cost: String(Number(pre) || 0),
      material_cost: String(Number(mat) || 0),
      labor_cost: String(Number(labor) || 0),
      expense_cost: String(Number(exp) || 0),
      notes: notes || null,
    };
    try {
      if (existing) {
        await update.mutateAsync({ id: existing.id, data: payload });
      } else {
        await create.mutateAsync({
          consolidation_key: trimmedKey,
          period_id: periodId,
          ...payload,
        });
      }
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存に失敗しました");
    }
  };

  const handleDelete = async () => {
    if (!existing) return;
    if (
      !confirm(
        `名寄せキー「${existing.consolidation_key}」の単価レコードを削除します。よろしいですか？`
      )
    )
      return;
    setError(null);
    try {
      await remove.mutateAsync(existing.id);
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "削除に失敗しました");
    }
  };

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{existing ? "仕掛品 SC 単価の編集" : "仕掛品 SC 単価の新規登録"}</DialogTitle>
          <DialogDescription>
            参照期間: <strong>{periodLabel || "未選択"}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium">名寄せキー</label>
            <Input
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="例: B / BM / FB / その他"
              disabled={!!existing}
              className="font-mono"
            />
            {existing && (
              <p className="mt-1 text-xs text-muted-foreground">
                既存レコードのキー変更は不可です(削除→新規登録で対応してください)
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <NumField label="前工程費" value={pre} onChange={setPre} />
            <NumField label="原材料費" value={mat} onChange={setMat} />
            <NumField label="労務費" value={labor} onChange={setLabor} />
            <NumField label="経費" value={exp} onChange={setExp} />
          </div>

          <div className="rounded-md bg-muted/40 p-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">内訳合計</span>
              <span className="font-mono">{formatNumber(breakdownSum, 2)}</span>
            </div>
            <div className="mt-2">
              <label className="mb-1 block text-xs text-muted-foreground">
                SC単価合計 (空欄なら内訳合計を自動採用)
              </label>
              <Input
                type="number"
                step="0.0001"
                value={totalManual}
                onChange={(e) => setTotalManual(e.target.value)}
                placeholder={`${breakdownSum.toFixed(4)}（自動）`}
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">備考</label>
            <Input
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="（任意）取込元・根拠など"
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <DialogFooter>
          {existing && (
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
            {existing ? "更新" : "新規登録"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function NumField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs text-muted-foreground">{label}</label>
      <Input
        type="number"
        step="0.0001"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
