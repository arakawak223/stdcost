"use client";

import { useState } from "react";
import { AlertTriangle, BarChart3, Flag, List, Play } from "lucide-react";
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
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useFiscalPeriods } from "@/hooks/use-masters";
import {
  useVarianceRecords,
  useVarianceSummary,
  useRunVarianceAnalysis,
  useUpdateVarianceRecord,
} from "@/hooks/use-variance";
import { formatCurrency, formatPercent, formatFiscalPeriod, costElementLabels, varianceTypeLabels } from "@/lib/format";
import type { VarianceAnalysisResult, VarianceRecord } from "@/lib/api-client";

export default function VarianceAnalysisPage() {
  const [activeTab, setActiveTab] = useState<"run" | "summary" | "records">("run");
  const [periodId, setPeriodId] = useState("");
  const [threshold, setThreshold] = useState("5.0");
  const [analysisResult, setAnalysisResult] = useState<VarianceAnalysisResult | null>(null);
  const [editRecord, setEditRecord] = useState<VarianceRecord | null>(null);
  const [editNotes, setEditNotes] = useState("");
  const [editFlagReason, setEditFlagReason] = useState("");

  const { data: periods } = useFiscalPeriods();
  const runAnalysis = useRunVarianceAnalysis();
  const { data: summary } = useVarianceSummary(periodId || undefined);
  const { data: records } = useVarianceRecords(periodId ? { period_id: periodId } : undefined);
  const updateRecord = useUpdateVarianceRecord();

  const handleRunAnalysis = async () => {
    if (!periodId) return;
    const result = await runAnalysis.mutateAsync({
      period_id: periodId,
      threshold_percent: parseFloat(threshold),
    });
    setAnalysisResult(result);
  };

  const handleSaveRecord = async () => {
    if (!editRecord) return;
    await updateRecord.mutateAsync({
      id: editRecord.id,
      data: {
        notes: editNotes || undefined,
        flag_reason: editFlagReason || undefined,
      },
    });
    setEditRecord(null);
  };

  const tabs = [
    { key: "run" as const, label: "差異分析実行", icon: Play },
    { key: "summary" as const, label: "サマリーレポート", icon: BarChart3 },
    { key: "records" as const, label: "差異レコード", icon: List },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">差異分析</h1>

      {/* Period Selector */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">会計期間:</label>
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

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: 差異分析実行 */}
      {activeTab === "run" && (
        <div className="space-y-6">
          <div className="flex items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">閾値 (%)</label>
              <Input
                type="number"
                step="0.1"
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
                className="w-32"
              />
            </div>
            <Button
              onClick={handleRunAnalysis}
              disabled={!periodId || runAnalysis.isPending}
            >
              {runAnalysis.isPending ? "分析中..." : "差異分析を実行"}
            </Button>
          </div>

          {runAnalysis.error && (
            <p className="text-sm text-destructive">{(runAnalysis.error as Error).message}</p>
          )}

          {analysisResult && (
            <>
              <div className="grid grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">分析製品数</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{analysisResult.products_analyzed}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">レコード数</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{analysisResult.records_created}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">フラグ数</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-destructive">{analysisResult.flagged_count}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">総差異額</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{formatCurrency(analysisResult.total_variance)}</p>
                  </CardContent>
                </Card>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>製品</TableHead>
                    <TableHead className="text-right">標準原価</TableHead>
                    <TableHead className="text-right">実際原価</TableHead>
                    <TableHead className="text-right">差異額</TableHead>
                    <TableHead className="text-right">差異率</TableHead>
                    <TableHead>原価要素別</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {analysisResult.details.map((d) => (
                    <TableRow key={`${d.product_id}-${d.cost_center_id}`}>
                      <TableCell>
                        <div>
                          <span className="font-medium">{d.product_name}</span>
                          <span className="ml-2 text-xs text-muted-foreground">{d.product_code}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">{formatCurrency(d.total_standard)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(d.total_actual)}</TableCell>
                      <TableCell className={`text-right font-medium ${d.is_favorable ? "text-green-600" : "text-red-600"}`}>
                        {formatCurrency(d.total_variance)}
                      </TableCell>
                      <TableCell className={`text-right ${d.is_favorable ? "text-green-600" : "text-red-600"}`}>
                        {formatPercent(d.total_variance_percent)}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {d.elements.map((el) => (
                            <Badge
                              key={el.cost_element}
                              variant={el.is_favorable ? "success" : "warning"}
                              className="text-xs"
                            >
                              {costElementLabels[el.cost_element] || el.cost_element}{" "}
                              {formatPercent(el.variance_percent)}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          )}
        </div>
      )}

      {/* Tab 2: サマリーレポート */}
      {activeTab === "summary" && (
        <div className="space-y-6">
          {!periodId && <p className="text-muted-foreground">会計期間を選択してください。</p>}
          {summary && (
            <>
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">対象製品数</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{summary.total_products}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">総差異額</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{formatCurrency(summary.overall_variance)}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-muted-foreground">フラグ件数</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-destructive">{summary.total_flagged}</p>
                  </CardContent>
                </Card>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>原価要素</TableHead>
                    <TableHead className="text-right">標準原価合計</TableHead>
                    <TableHead className="text-right">実際原価合計</TableHead>
                    <TableHead className="text-right">差異合計</TableHead>
                    <TableHead className="text-right">平均差異率</TableHead>
                    <TableHead className="text-right">有利</TableHead>
                    <TableHead className="text-right">不利</TableHead>
                    <TableHead className="text-right">フラグ</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {summary.by_element.map((el) => (
                    <TableRow key={el.cost_element}>
                      <TableCell className="font-medium">
                        {costElementLabels[el.cost_element] || el.cost_element}
                      </TableCell>
                      <TableCell className="text-right">{formatCurrency(el.total_standard)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(el.total_actual)}</TableCell>
                      <TableCell className="text-right font-medium">{formatCurrency(el.total_variance)}</TableCell>
                      <TableCell className="text-right">{formatPercent(el.average_variance_percent)}</TableCell>
                      <TableCell className="text-right text-green-600">{el.favorable_count}</TableCell>
                      <TableCell className="text-right text-red-600">{el.unfavorable_count}</TableCell>
                      <TableCell className="text-right">{el.flagged_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          )}
        </div>
      )}

      {/* Tab 3: 差異レコード */}
      {activeTab === "records" && (
        <div className="space-y-4">
          {!periodId && <p className="text-muted-foreground">会計期間を選択してください。</p>}
          {records && records.length === 0 && (
            <p className="text-muted-foreground">差異レコードがありません。分析を実行してください。</p>
          )}
          {records && records.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>タイプ</TableHead>
                  <TableHead>原価要素</TableHead>
                  <TableHead className="text-right">標準額</TableHead>
                  <TableHead className="text-right">実際額</TableHead>
                  <TableHead className="text-right">差異額</TableHead>
                  <TableHead className="text-right">差異率</TableHead>
                  <TableHead>状態</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {records.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell>
                      <Badge variant="outline">{varianceTypeLabels[r.variance_type] || r.variance_type}</Badge>
                    </TableCell>
                    <TableCell>{costElementLabels[r.cost_element] || r.cost_element}</TableCell>
                    <TableCell className="text-right">{formatCurrency(r.standard_amount)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(r.actual_amount)}</TableCell>
                    <TableCell className={`text-right font-medium ${r.is_favorable ? "text-green-600" : "text-red-600"}`}>
                      {formatCurrency(r.variance_amount)}
                    </TableCell>
                    <TableCell className={`text-right ${r.is_favorable ? "text-green-600" : "text-red-600"}`}>
                      {formatPercent(r.variance_percent)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        {r.is_favorable ? (
                          <Badge variant="success">有利</Badge>
                        ) : (
                          <Badge variant="warning">不利</Badge>
                        )}
                        {r.is_flagged && (
                          <AlertTriangle className="h-4 w-4 text-destructive" />
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditRecord(r);
                          setEditNotes(r.notes || "");
                          setEditFlagReason(r.flag_reason || "");
                        }}
                      >
                        編集
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editRecord} onOpenChange={() => setEditRecord(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>差異レコード編集</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">フラグ理由</label>
              <Input
                value={editFlagReason}
                onChange={(e) => setEditFlagReason(e.target.value)}
                placeholder="フラグの理由を入力..."
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">メモ</label>
              <textarea
                className="w-full rounded-md border px-3 py-2 text-sm"
                rows={3}
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="メモを入力..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditRecord(null)}>
              キャンセル
            </Button>
            <Button onClick={handleSaveRecord} disabled={updateRecord.isPending}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
