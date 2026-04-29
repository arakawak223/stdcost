"use client";

import { useState } from "react";
import { Upload, Boxes, RefreshCw, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useFiscalPeriods } from "@/hooks/use-masters";
import {
  useInventoryValuations,
  useProductInventoryFlow,
  useRecalculateValuation,
  useUploadInventory,
  useValuationSummary,
} from "@/hooks/use-inventory-valuations";
import {
  formatCurrency,
  formatFiscalPeriod,
  formatNumber,
  inventoryCategoryLabels,
} from "@/lib/format";
import type { InventoryCategory } from "@/lib/api-client";

const categoryFilters: { value: InventoryCategory | ""; label: string }[] = [
  { value: "", label: "全区分" },
  { value: "product", label: "製品" },
  { value: "semi_finished", label: "半製品" },
  { value: "crude_product", label: "原体" },
  { value: "raw_material", label: "原材料" },
  { value: "sub_material", label: "副資材" },
  { value: "merchandise", label: "商品" },
  { value: "other", label: "その他" },
];

type TabKey = "list" | "flow";

export default function InventoryValuationsPage() {
  const [periodId, setPeriodId] = useState("");
  const [priorPeriodId, setPriorPeriodId] = useState("");
  const [category, setCategory] = useState<InventoryCategory | "">("");
  const [warehouse, setWarehouse] = useState("");
  const [itemCode, setItemCode] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [tab, setTab] = useState<TabKey>("list");

  const { data: periods } = useFiscalPeriods();
  const { data: summary } = useValuationSummary(periodId || undefined);
  const { data: valuations } = useInventoryValuations({
    period_id: periodId || undefined,
    category: category || undefined,
    warehouse_name: warehouse || undefined,
    item_code: itemCode || undefined,
    limit: 200,
  });
  const { data: flows } = useProductInventoryFlow(
    periodId || undefined,
    priorPeriodId || undefined
  );
  const recalc = useRecalculateValuation();
  const upload = useUploadInventory();

  const handleUpload = async () => {
    if (!file || !periodId) return;
    await upload.mutateAsync({ file, period_id: periodId });
    setFile(null);
  };

  const handleRecalc = async () => {
    if (!periodId) return;
    await recalc.mutateAsync(periodId);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">在庫評価</h1>
        <p className="text-sm text-muted-foreground">
          標準単価 × 実際数量で在庫金額・払出金額を算出
        </p>
      </div>

      {/* 期間選択 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">対象期間</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={periodId}
                onChange={(e) => setPeriodId(e.target.value)}
              >
                <option value="">選択...</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">前期(期首用)</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={priorPeriodId}
                onChange={(e) => setPriorPeriodId(e.target.value)}
              >
                <option value="">なし</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month)}
                  </option>
                ))}
              </select>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRecalc}
              disabled={!periodId || recalc.isPending}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              標準単価で再計算
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Excel取込 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Upload className="h-5 w-5" />
            期末全在庫Excel取込（4.3期末全在庫シート）
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end gap-4">
            <input
              type="file"
              accept=".xlsx"
              className="text-sm"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            <Button
              size="sm"
              onClick={handleUpload}
              disabled={!file || !periodId || upload.isPending}
            >
              アップロード
            </Button>
            {upload.data && (
              <span className="text-xs text-muted-foreground">
                {upload.data.message}
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* サマリー */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Boxes className="h-5 w-5" />
                区分別集計
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>区分</TableHead>
                    <TableHead className="text-right">件数</TableHead>
                    <TableHead className="text-right">合計数量</TableHead>
                    <TableHead className="text-right">評価金額</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {summary.by_category.map((c) => (
                    <TableRow key={c.category}>
                      <TableCell>{inventoryCategoryLabels[c.category]}</TableCell>
                      <TableCell className="text-right">{c.item_count}</TableCell>
                      <TableCell className="text-right">{formatNumber(c.total_quantity)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(c.total_amount)}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="font-bold">
                    <TableCell>合計</TableCell>
                    <TableCell className="text-right">{summary.total_items}</TableCell>
                    <TableCell />
                    <TableCell className="text-right">{formatCurrency(summary.total_amount)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Boxes className="h-5 w-5" />
                倉庫別集計
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="max-h-64 overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>倉庫</TableHead>
                      <TableHead className="text-right">件数</TableHead>
                      <TableHead className="text-right">評価金額</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {summary.by_warehouse.map((w) => (
                      <TableRow key={w.warehouse_name}>
                        <TableCell>{w.warehouse_name}</TableCell>
                        <TableCell className="text-right">{w.item_count}</TableCell>
                        <TableCell className="text-right">{formatCurrency(w.total_amount)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 詳細タブ（簡易切り替え） */}
      <div className="flex gap-2 border-b">
        <button
          type="button"
          onClick={() => setTab("list")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "list"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          在庫評価一覧
        </button>
        <button
          type="button"
          onClick={() => setTab("flow")}
          className={`flex items-center px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "flow"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <TrendingUp className="mr-2 h-4 w-4" />
          製品在庫推移
        </button>
      </div>

      {tab === "list" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">在庫評価レコード（最大200件）</CardTitle>
              <div className="flex flex-wrap gap-2 pt-2">
                <select
                  className="rounded-md border px-3 py-2 text-sm"
                  value={category}
                  onChange={(e) => setCategory(e.target.value as InventoryCategory | "")}
                >
                  {categoryFilters.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="倉庫名"
                  value={warehouse}
                  onChange={(e) => setWarehouse(e.target.value)}
                  className="rounded-md border px-3 py-2 text-sm"
                />
                <input
                  type="text"
                  placeholder="商品コード"
                  value={itemCode}
                  onChange={(e) => setItemCode(e.target.value)}
                  className="rounded-md border px-3 py-2 text-sm"
                />
              </div>
            </CardHeader>
            <CardContent>
              {!periodId ? (
                <p className="text-sm text-muted-foreground">対象期間を選択してください</p>
              ) : (
                <div className="max-h-[500px] overflow-y-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>商品コード</TableHead>
                        <TableHead>商品名</TableHead>
                        <TableHead>倉庫</TableHead>
                        <TableHead>区分</TableHead>
                        <TableHead className="text-right">数量</TableHead>
                        <TableHead className="text-right">標準単価</TableHead>
                        <TableHead className="text-right">評価金額</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {valuations?.map((v) => (
                        <TableRow key={v.id}>
                          <TableCell className="font-mono text-xs">{v.item_code}</TableCell>
                          <TableCell className="max-w-xs truncate">{v.item_name}</TableCell>
                          <TableCell>{v.warehouse_name}</TableCell>
                          <TableCell>{inventoryCategoryLabels[v.category]}</TableCell>
                          <TableCell className="text-right">
                            {formatNumber(v.quantity)} {v.unit}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatCurrency(v.standard_unit_price)}
                          </TableCell>
                          <TableCell className="text-right font-semibold">
                            {formatCurrency(v.valuation_amount)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
      )}

      {tab === "flow" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                製品在庫推移（期首+受入-払出=期末、標準単価ベース）
              </CardTitle>
              <p className="text-xs text-muted-foreground pt-1">
                ※ 期首は前期の期末在庫から、受入・払出は当期 InventoryMovement から集計
              </p>
            </CardHeader>
            <CardContent>
              {!periodId ? (
                <p className="text-sm text-muted-foreground">対象期間を選択してください</p>
              ) : !flows || flows.length === 0 ? (
                <p className="text-sm text-muted-foreground">データがありません</p>
              ) : (
                <div className="max-h-[500px] overflow-y-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>商品コード</TableHead>
                        <TableHead>商品名</TableHead>
                        <TableHead className="text-right">標準単価</TableHead>
                        <TableHead className="text-right">期首数量</TableHead>
                        <TableHead className="text-right">受入数量</TableHead>
                        <TableHead className="text-right">払出数量</TableHead>
                        <TableHead className="text-right">期末数量</TableHead>
                        <TableHead className="text-right">期末金額</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {flows.map((f) => (
                        <TableRow key={f.product_id}>
                          <TableCell className="font-mono text-xs">{f.product_code}</TableCell>
                          <TableCell className="max-w-xs truncate">{f.product_name}</TableCell>
                          <TableCell className="text-right">
                            {formatCurrency(f.standard_unit_price)}
                          </TableCell>
                          <TableCell className="text-right">{formatNumber(f.beginning_qty)}</TableCell>
                          <TableCell className="text-right">{formatNumber(f.receipt_qty)}</TableCell>
                          <TableCell className="text-right">{formatNumber(f.issue_qty)}</TableCell>
                          <TableCell className="text-right">{formatNumber(f.ending_qty)}</TableCell>
                          <TableCell className="text-right font-semibold">
                            {formatCurrency(f.ending_amount)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
      )}
    </div>
  );
}
