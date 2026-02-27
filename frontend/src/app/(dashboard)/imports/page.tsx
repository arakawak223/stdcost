"use client";

import { useState } from "react";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
} from "@/components/ui/dialog";
import { useFiscalPeriods } from "@/hooks/use-masters";
import { useImportBatches, useUploadImport } from "@/hooks/use-imports";
import { formatDateTime, formatFiscalPeriod, sourceSystemLabels, importStatusLabels } from "@/lib/format";
import type { ImportBatch } from "@/lib/api-client";

const importStatusVariant: Record<string, "default" | "secondary" | "success" | "warning" | "outline"> = {
  pending: "secondary",
  processing: "default",
  completed: "success",
  failed: "warning",
};

const sourceOptions = [
  { value: "sc_system", label: "SC（基幹システム）", fileType: "CSV" },
  { value: "geneki_db", label: "原液DB", fileType: "Excel" },
  { value: "kanjyo_bugyo", label: "勘定奉行", fileType: "CSV" },
  { value: "manual", label: "手動入力", fileType: "CSV" },
];

export default function ImportsPage() {
  const [sourceSystem, setSourceSystem] = useState("");
  const [periodId, setPeriodId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [detailBatch, setDetailBatch] = useState<ImportBatch | null>(null);

  const { data: periods } = useFiscalPeriods();
  const { data: batches } = useImportBatches();
  const upload = useUploadImport();

  const handleUpload = async () => {
    if (!file || !sourceSystem || !periodId) return;
    await upload.mutateAsync({ file, source_system: sourceSystem, period_id: periodId });
    setFile(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">データ取込</h1>

      {/* Upload Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            ファイルアップロード
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">ソースシステム</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={sourceSystem}
                onChange={(e) => setSourceSystem(e.target.value)}
              >
                <option value="">選択...</option>
                {sourceOptions.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label} ({s.fileType})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">会計期間</label>
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
              <label className="mb-1 block text-sm font-medium">ファイル</label>
              <input
                type="file"
                accept=".csv,.xlsx"
                className="text-sm"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
            <Button
              onClick={handleUpload}
              disabled={!file || !sourceSystem || !periodId || upload.isPending}
            >
              {upload.isPending ? "アップロード中..." : "アップロード"}
            </Button>
          </div>
          {upload.error && (
            <p className="mt-2 text-sm text-destructive">{(upload.error as Error).message}</p>
          )}
          {upload.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{upload.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {upload.data.total_rows}行 / 成功: {upload.data.success_rows}行 / エラー: {upload.data.error_rows}行
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Import History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            インポート履歴
          </CardTitle>
        </CardHeader>
        <CardContent>
          {batches && batches.length === 0 && (
            <p className="text-muted-foreground">インポート履歴がありません。</p>
          )}
          {batches && batches.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ファイル名</TableHead>
                  <TableHead>ソース</TableHead>
                  <TableHead>ステータス</TableHead>
                  <TableHead className="text-right">合計行</TableHead>
                  <TableHead className="text-right">成功</TableHead>
                  <TableHead className="text-right">エラー</TableHead>
                  <TableHead>日時</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {batches.map((b) => (
                  <TableRow key={b.id}>
                    <TableCell className="font-medium">{b.file_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{sourceSystemLabels[b.source_system] || b.source_system}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={importStatusVariant[b.status] || "default"}>
                        {importStatusLabels[b.status] || b.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">{b.total_rows}</TableCell>
                    <TableCell className="text-right">{b.success_rows}</TableCell>
                    <TableCell className="text-right">{b.error_rows > 0 ? <span className="text-destructive">{b.error_rows}</span> : 0}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{formatDateTime(b.created_at)}</TableCell>
                    <TableCell>
                      {b.error_rows > 0 && (
                        <Button variant="ghost" size="sm" onClick={() => setDetailBatch(b)}>
                          詳細
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Batch Detail Dialog */}
      <Dialog open={!!detailBatch} onOpenChange={() => setDetailBatch(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              エラー詳細 — {detailBatch?.file_name}
            </DialogTitle>
          </DialogHeader>
          {detailBatch?.errors && detailBatch.errors.length > 0 && (
            <div className="max-h-96 overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>行番号</TableHead>
                    <TableHead>列名</TableHead>
                    <TableHead>エラー内容</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {detailBatch.errors.map((err) => (
                    <TableRow key={err.id}>
                      <TableCell>{err.row_number}</TableCell>
                      <TableCell>{err.column_name || "-"}</TableCell>
                      <TableCell className="text-sm text-destructive">{err.error_message}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
