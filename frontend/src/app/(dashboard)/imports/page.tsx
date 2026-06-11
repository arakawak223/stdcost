"use client";

import { useState } from "react";
import {
  Upload,
  FileText,
  AlertCircle,
  Layers,
  Beaker,
  Package,
  ArrowLeftRight,
  Workflow,
  History,
} from "lucide-react";
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
import {
  useImportBatches,
  useUploadImport,
  useUploadWipSc,
  useUploadProductMovements,
  useUploadCrudeInventory,
  useUploadRawMaterialInventory,
  useUploadCrudeProcessRoutes,
  useUploadPriorYearActuals,
  useUploadPriorYearMaterials,
  useUploadPriorYearWip,
  useUploadPriorYearOutsource,
  useUploadPriorYearRMaterial,
  useUploadPriorYearRLabor,
} from "@/hooks/use-imports";
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

  const [wipPeriodId, setWipPeriodId] = useState("");
  const [wipFile, setWipFile] = useState<File | null>(null);

  const [crudePeriodId, setCrudePeriodId] = useState("");
  const [crudeFile, setCrudeFile] = useState<File | null>(null);
  const [crudeDeleteExisting, setCrudeDeleteExisting] = useState(true);
  const [crudeSkipZero, setCrudeSkipZero] = useState(false);

  const [rawPeriodId, setRawPeriodId] = useState("");
  const [rawFile, setRawFile] = useState<File | null>(null);
  const [rawDeleteExisting, setRawDeleteExisting] = useState(true);
  const [rawSkipZero, setRawSkipZero] = useState(false);
  const [rawUpdateMaster, setRawUpdateMaster] = useState(true);

  const [movePeriodId, setMovePeriodId] = useState("");
  const [moveFile, setMoveFile] = useState<File | null>(null);
  const [moveDeleteExisting, setMoveDeleteExisting] = useState(true);

  const [routePeriodId, setRoutePeriodId] = useState("");
  const [routeFile, setRouteFile] = useState<File | null>(null);

  const [priorYear, setPriorYear] = useState<number>(38);
  const [priorFile, setPriorFile] = useState<File | null>(null);
  const [priorDeleteExisting, setPriorDeleteExisting] = useState(true);
  const [priorMatYear, setPriorMatYear] = useState<number>(38);
  const [priorMatFile, setPriorMatFile] = useState<File | null>(null);
  const [priorMatDeleteExisting, setPriorMatDeleteExisting] = useState(true);
  const [priorWipYear, setPriorWipYear] = useState<number>(38);
  const [priorWipFile, setPriorWipFile] = useState<File | null>(null);
  const [priorWipDeleteExisting, setPriorWipDeleteExisting] = useState(true);
  const [priorOutYear, setPriorOutYear] = useState<number>(38);
  const [priorOutFile, setPriorOutFile] = useState<File | null>(null);
  const [priorOutDeleteExisting, setPriorOutDeleteExisting] = useState(true);
  const [priorRMatYear, setPriorRMatYear] = useState<number>(38);
  const [priorRMatFile, setPriorRMatFile] = useState<File | null>(null);
  const [priorRMatDeleteExisting, setPriorRMatDeleteExisting] = useState(true);
  const [priorRLabYear, setPriorRLabYear] = useState<number>(38);
  const [priorRLabFile, setPriorRLabFile] = useState<File | null>(null);
  const [priorRLabDeleteExisting, setPriorRLabDeleteExisting] = useState(true);

  const { data: periods } = useFiscalPeriods();
  const { data: batches } = useImportBatches();
  const upload = useUploadImport();
  const uploadWipSc = useUploadWipSc();
  const uploadCrude = useUploadCrudeInventory();
  const uploadRaw = useUploadRawMaterialInventory();
  const uploadMove = useUploadProductMovements();
  const uploadRoutes = useUploadCrudeProcessRoutes();
  const uploadPrior = useUploadPriorYearActuals();
  const uploadPriorMat = useUploadPriorYearMaterials();
  const uploadPriorWip = useUploadPriorYearWip();
  const uploadPriorOut = useUploadPriorYearOutsource();
  const uploadPriorRMat = useUploadPriorYearRMaterial();
  const uploadPriorRLab = useUploadPriorYearRLabor();

  const handleUpload = async () => {
    if (!file || !sourceSystem || !periodId) return;
    await upload.mutateAsync({ file, source_system: sourceSystem, period_id: periodId });
    setFile(null);
  };

  const handleUploadWipSc = async () => {
    if (!wipFile || !wipPeriodId) return;
    await uploadWipSc.mutateAsync({ file: wipFile, period_id: wipPeriodId });
    setWipFile(null);
  };

  const handleUploadCrude = async () => {
    if (!crudeFile || !crudePeriodId) return;
    await uploadCrude.mutateAsync({
      file: crudeFile,
      period_id: crudePeriodId,
      delete_existing: crudeDeleteExisting,
      skip_zero_stock: crudeSkipZero,
    });
    setCrudeFile(null);
  };

  const handleUploadRaw = async () => {
    if (!rawFile || !rawPeriodId) return;
    await uploadRaw.mutateAsync({
      file: rawFile,
      period_id: rawPeriodId,
      delete_existing: rawDeleteExisting,
      skip_zero_stock: rawSkipZero,
      update_master_price: rawUpdateMaster,
    });
    setRawFile(null);
  };

  const handleUploadMove = async () => {
    if (!moveFile || !movePeriodId) return;
    await uploadMove.mutateAsync({
      file: moveFile,
      period_id: movePeriodId,
      delete_existing: moveDeleteExisting,
    });
    setMoveFile(null);
  };

  const handleUploadRoutes = async () => {
    if (!routeFile || !routePeriodId) return;
    await uploadRoutes.mutateAsync({ file: routeFile, period_id: routePeriodId });
    setRouteFile(null);
  };

  const handleUploadPrior = async () => {
    if (!priorFile || !priorYear) return;
    await uploadPrior.mutateAsync({
      file: priorFile,
      fiscal_year: priorYear,
      delete_existing: priorDeleteExisting,
    });
    setPriorFile(null);
  };

  const handleUploadPriorMat = async () => {
    if (!priorMatFile || !priorMatYear) return;
    await uploadPriorMat.mutateAsync({
      file: priorMatFile,
      fiscal_year: priorMatYear,
      delete_existing: priorMatDeleteExisting,
    });
    setPriorMatFile(null);
  };

  const handleUploadPriorWip = async () => {
    if (!priorWipFile || !priorWipYear) return;
    await uploadPriorWip.mutateAsync({
      file: priorWipFile,
      fiscal_year: priorWipYear,
      delete_existing: priorWipDeleteExisting,
    });
    setPriorWipFile(null);
  };

  const handleUploadPriorOut = async () => {
    if (!priorOutFile || !priorOutYear) return;
    await uploadPriorOut.mutateAsync({
      file: priorOutFile,
      fiscal_year: priorOutYear,
      delete_existing: priorOutDeleteExisting,
    });
    setPriorOutFile(null);
  };

  const handleUploadPriorRMat = async () => {
    if (!priorRMatFile || !priorRMatYear) return;
    await uploadPriorRMat.mutateAsync({
      file: priorRMatFile,
      fiscal_year: priorRMatYear,
      delete_existing: priorRMatDeleteExisting,
    });
    setPriorRMatFile(null);
  };

  const handleUploadPriorRLab = async () => {
    if (!priorRLabFile || !priorRLabYear) return;
    await uploadPriorRLab.mutateAsync({
      file: priorRLabFile,
      fiscal_year: priorRLabYear,
      delete_existing: priorRLabDeleteExisting,
    });
    setPriorRLabFile(null);
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
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
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

      {/* 仕掛品SC単価 専用アップロード */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-5 w-5" />
            仕掛品SC単価Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">決算用SC仕掛品.xlsx</span> をアップロードし、
            <strong>仕掛品標準単価一覧表（貼付）</strong> から <code>wip_standard_costs</code> を更新、
            <strong>仕掛品名寄（貼付）</strong> から <code>products.sc_consolidation_key</code> を解決します。
            完了後に半製品の在庫評価金額を自動で再計算します。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計期間</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={wipPeriodId}
                onChange={(e) => setWipPeriodId(e.target.value)}
              >
                <option value="">選択...</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={wipFile?.name || "empty"}
                onChange={(e) => setWipFile(e.target.files?.[0] || null)}
              />
            </div>
            <Button
              onClick={handleUploadWipSc}
              disabled={!wipFile || !wipPeriodId || uploadWipSc.isPending}
            >
              {uploadWipSc.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadWipSc.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadWipSc.error as Error).message}
            </p>
          )}
          {uploadWipSc.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadWipSc.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadWipSc.data.total_rows}行 / 成功: {uploadWipSc.data.success_rows}行 /
                エラー: {uploadWipSc.data.error_rows}行
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 原液×工程ルート xlsb 取込 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Workflow className="h-5 w-5" />
            原液×工程ルート Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">第N期原価計算v8.xlsb</span> をアップロードし、
            <strong>2.1④シート</strong>(原液→原液変換記録)から
            <code>crude_product_process_routes</code> に
            (原液 × 工程 × 期別)の実績数量を upsert します。
            工程単位の配賦エンジンの基準データになります。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計期間</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={routePeriodId}
                onChange={(e) => setRoutePeriodId(e.target.value)}
              >
                <option value="">選択...</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsb)</label>
              <input
                type="file"
                accept=".xlsb"
                className="text-sm"
                key={routeFile?.name || "empty"}
                onChange={(e) => setRouteFile(e.target.files?.[0] || null)}
              />
            </div>
            <Button
              onClick={handleUploadRoutes}
              disabled={!routeFile || !routePeriodId || uploadRoutes.isPending}
            >
              {uploadRoutes.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadRoutes.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadRoutes.error as Error).message}
            </p>
          )}
          {uploadRoutes.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadRoutes.data.message}</p>
              <p className="text-xs text-muted-foreground">
                集計: {uploadRoutes.data.total_rows}件 / 成功: {uploadRoutes.data.success_rows}件 /
                未マッチ警告: {uploadRoutes.data.errors?.length ?? 0}件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 2.9原液在庫 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Beaker className="h-5 w-5" />
            2.9原液在庫 Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <strong>2.9原液在庫</strong> シート (Section 1, コード形式 1-XX-Y) を取込み、
            <code>inventory_valuations</code> に <code>category=crude_product</code> として登録します。
            未登録コードは <code>crude_products</code> に自動INSERT。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計期間</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={crudePeriodId}
                onChange={(e) => setCrudePeriodId(e.target.value)}
              >
                <option value="">選択...</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={crudeFile?.name || "empty"}
                onChange={(e) => setCrudeFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={crudeDeleteExisting}
                onChange={(e) => setCrudeDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={crudeSkipZero}
                onChange={(e) => setCrudeSkipZero(e.target.checked)}
              />
              ゼロ在庫スキップ
            </label>
            <Button
              onClick={handleUploadCrude}
              disabled={!crudeFile || !crudePeriodId || uploadCrude.isPending}
            >
              {uploadCrude.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadCrude.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadCrude.error as Error).message}
            </p>
          )}
          {uploadCrude.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadCrude.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadCrude.data.total_rows}行 / 成功: {uploadCrude.data.success_rows}行 /
                エラー: {uploadCrude.data.error_rows}行
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 1.5原材料在庫 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            1.5原材料在庫 (決算用SC原材料.xlsx) 取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <strong>1.5原材料在庫</strong> シートをロット集約し、
            <strong>原材料SC明細</strong> から SC単価を取得して
            <code>inventory_valuations</code> (<code>category=raw_material</code>) に登録します。
            未登録コードは <code>materials</code> に自動INSERT。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計期間</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={rawPeriodId}
                onChange={(e) => setRawPeriodId(e.target.value)}
              >
                <option value="">選択...</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={rawFile?.name || "empty"}
                onChange={(e) => setRawFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={rawDeleteExisting}
                onChange={(e) => setRawDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={rawSkipZero}
                onChange={(e) => setRawSkipZero(e.target.checked)}
              />
              ゼロ在庫スキップ
            </label>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={rawUpdateMaster}
                onChange={(e) => setRawUpdateMaster(e.target.checked)}
              />
              マスタ単価更新
            </label>
            <Button
              onClick={handleUploadRaw}
              disabled={!rawFile || !rawPeriodId || uploadRaw.isPending}
            >
              {uploadRaw.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadRaw.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadRaw.error as Error).message}
            </p>
          )}
          {uploadRaw.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadRaw.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadRaw.data.total_rows}行 / 成功: {uploadRaw.data.success_rows}行 /
                エラー: {uploadRaw.data.error_rows}行
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 製品増減内訳表 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5" />
            製品増減内訳表 Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <strong>製品増減内訳表</strong> シートから期首/生産/販売/販促/.../期末などの数量変動を
            <code>inventory_movements</code> に登録します。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計期間</label>
              <select
                className="rounded-md border px-3 py-2 text-sm"
                value={movePeriodId}
                onChange={(e) => setMovePeriodId(e.target.value)}
              >
                <option value="">選択...</option>
                {periods?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={moveFile?.name || "empty"}
                onChange={(e) => setMoveFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={moveDeleteExisting}
                onChange={(e) => setMoveDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadMove}
              disabled={!moveFile || !movePeriodId || uploadMove.isPending}
            >
              {uploadMove.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadMove.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadMove.error as Error).message}
            </p>
          )}
          {uploadMove.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadMove.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadMove.data.total_rows}行 / 成功: {uploadMove.data.success_rows}行 /
                エラー: {uploadMove.data.error_rows}行
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 前年実績 (38期) 製品SC原価フロー */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            前年実績 (製品SC原価フロー) Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">30SC製品rev1.xlsx</span> の
            <strong>5.製品</strong> シートから第38期の製品別年間SC原価フロー
            (期首/当期製造仕入/振替/売上原価/外注支給/期末 + 振替系7項目) を
            <code>prior_year_actuals</code> に取込みます。
            差異分析の前期比較ベース。同一商品コードは合算して一本化します。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計年度</label>
              <input
                type="number"
                className="w-24 rounded-md border px-3 py-2 text-sm"
                value={priorYear}
                onChange={(e) => setPriorYear(Number(e.target.value))}
                min={1}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={priorFile?.name || "empty"}
                onChange={(e) => setPriorFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={priorDeleteExisting}
                onChange={(e) => setPriorDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadPrior}
              disabled={!priorFile || !priorYear || uploadPrior.isPending}
            >
              {uploadPrior.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadPrior.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadPrior.error as Error).message}
            </p>
          )}
          {uploadPrior.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadPrior.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadPrior.data.total_rows}件 / 成功: {uploadPrior.data.success_rows}件 /
                エラー: {uploadPrior.data.error_rows}件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 前年実績 (38期) 原材料SC原価フロー */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            前年実績 (原材料SC原価フロー) Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">10 SC原材料.xlsx</span> の
            <strong>原材料SC明細</strong> シートから第38期の原材料別年間SC原価フロー
            (期首棚卸/当期仕入高/当期投入高/期末棚卸 + 調整系7項目) を
            <code>prior_year_material_actuals</code> に取込みます。
            差異分析の前期比較ベース。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計年度</label>
              <input
                type="number"
                className="w-24 rounded-md border px-3 py-2 text-sm"
                value={priorMatYear}
                onChange={(e) => setPriorMatYear(Number(e.target.value))}
                min={1}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={priorMatFile?.name || "empty"}
                onChange={(e) => setPriorMatFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={priorMatDeleteExisting}
                onChange={(e) => setPriorMatDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadPriorMat}
              disabled={!priorMatFile || !priorMatYear || uploadPriorMat.isPending}
            >
              {uploadPriorMat.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadPriorMat.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadPriorMat.error as Error).message}
            </p>
          )}
          {uploadPriorMat.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadPriorMat.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadPriorMat.data.total_rows}件 / 成功: {uploadPriorMat.data.success_rows}件 /
                エラー: {uploadPriorMat.data.error_rows}件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 前年実績 (38期) 仕掛品SC原価フロー */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            前年実績 (仕掛品SC原価フロー) Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">20 SC仕掛品.xlsx</span> の
            <strong>仕掛品SC明細</strong> シートから第38期の仕掛品(製造課)別年間SC原価フロー
            (期首棚卸/原材料/労務費/経費/前工程費/期末棚卸 + その他7項目) を
            <code>prior_year_wip_actuals</code> に取込みます。
            識別キーは種類(例 13R)。原材料費は明細未展開のため0です(原材料SC明細側に集約)。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計年度</label>
              <input
                type="number"
                className="w-24 rounded-md border px-3 py-2 text-sm"
                value={priorWipYear}
                onChange={(e) => setPriorWipYear(Number(e.target.value))}
                min={1}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={priorWipFile?.name || "empty"}
                onChange={(e) => setPriorWipFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={priorWipDeleteExisting}
                onChange={(e) => setPriorWipDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadPriorWip}
              disabled={!priorWipFile || !priorWipYear || uploadPriorWip.isPending}
            >
              {uploadPriorWip.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadPriorWip.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadPriorWip.error as Error).message}
            </p>
          )}
          {uploadPriorWip.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadPriorWip.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadPriorWip.data.total_rows}件 / 成功: {uploadPriorWip.data.success_rows}件 /
                エラー: {uploadPriorWip.data.error_rows}件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 前年実績 (38期) 外注製品SC原価フロー */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            前年実績 (外注製品SC原価フロー) Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">31SC外注製品.xlsx</span> の
            <strong>標準原価_外注製品</strong> シートから第38期の外注製品別
            単価(38期実際/39期標準) + 数量・金額フロー
            (37期末/生産/販売/38期末 + その他10項目) を
            <code>prior_year_outsource_actuals</code> に取込みます。
            区分A〜Fと外注先を保持。商品コードでマスタ名寄せ。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計年度</label>
              <input
                type="number"
                className="w-24 rounded-md border px-3 py-2 text-sm"
                value={priorOutYear}
                onChange={(e) => setPriorOutYear(Number(e.target.value))}
                min={1}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={priorOutFile?.name || "empty"}
                onChange={(e) => setPriorOutFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={priorOutDeleteExisting}
                onChange={(e) => setPriorOutDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadPriorOut}
              disabled={!priorOutFile || !priorOutYear || uploadPriorOut.isPending}
            >
              {uploadPriorOut.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadPriorOut.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadPriorOut.error as Error).message}
            </p>
          )}
          {uploadPriorOut.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadPriorOut.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadPriorOut.data.total_rows}件 / 成功: {uploadPriorOut.data.success_rows}件 /
                エラー: {uploadPriorOut.data.error_rows}件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 前年実績 (38期) R仕掛品 加重平均原材料費 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            前年実績 (R仕掛品 加重平均原材料費) Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">21-1 R仕掛品　原材料.xlsx</span> の
            <strong>R仕掛原材料費</strong> シートから原液系列(R1/R2/R3)の
            <strong>加重平均</strong>原材料費 (数量KG/金額/単価) を
            <code>prior_year_r_wip_components</code> に取込みます。
            34〜38期ロットを縦積み集計した加重平均結果のみを採用。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計年度</label>
              <input
                type="number"
                className="w-24 rounded-md border px-3 py-2 text-sm"
                value={priorRMatYear}
                onChange={(e) => setPriorRMatYear(Number(e.target.value))}
                min={1}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={priorRMatFile?.name || "empty"}
                onChange={(e) => setPriorRMatFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={priorRMatDeleteExisting}
                onChange={(e) => setPriorRMatDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadPriorRMat}
              disabled={!priorRMatFile || !priorRMatYear || uploadPriorRMat.isPending}
            >
              {uploadPriorRMat.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadPriorRMat.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadPriorRMat.error as Error).message}
            </p>
          )}
          {uploadPriorRMat.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadPriorRMat.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadPriorRMat.data.total_rows}件 / 成功: {uploadPriorRMat.data.success_rows}件 /
                エラー: {uploadPriorRMat.data.error_rows}件
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 前年実績 (38期) R仕掛品 加重平均労務費 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            前年実績 (R仕掛品 加重平均労務費) Excel取込
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-mono">21-2 R仕掛品　労務費.xlsx</span> の
            <strong>R仕掛品　労務費</strong> シートから原液系列(R1/R2/R3)の
            <strong>採用加重平均</strong>労務費 (数量KG/金額/単価) を
            <code>prior_year_r_wip_components</code> に取込みます。
            異常値除外後に罫線で囲まれた「□採用値」を自動検出。
          </p>
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">会計年度</label>
              <input
                type="number"
                className="w-24 rounded-md border px-3 py-2 text-sm"
                value={priorRLabYear}
                onChange={(e) => setPriorRLabYear(Number(e.target.value))}
                min={1}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">ファイル (.xlsx)</label>
              <input
                type="file"
                accept=".xlsx"
                className="text-sm"
                key={priorRLabFile?.name || "empty"}
                onChange={(e) => setPriorRLabFile(e.target.files?.[0] || null)}
              />
            </div>
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={priorRLabDeleteExisting}
                onChange={(e) => setPriorRLabDeleteExisting(e.target.checked)}
              />
              既存削除
            </label>
            <Button
              onClick={handleUploadPriorRLab}
              disabled={!priorRLabFile || !priorRLabYear || uploadPriorRLab.isPending}
            >
              {uploadPriorRLab.isPending ? "取込中..." : "取込実行"}
            </Button>
          </div>
          {uploadPriorRLab.error && (
            <p className="mt-2 text-sm text-destructive">
              {(uploadPriorRLab.error as Error).message}
            </p>
          )}
          {uploadPriorRLab.data && (
            <div className="mt-3 rounded-md border p-3">
              <p className="text-sm font-medium">{uploadPriorRLab.data.message}</p>
              <p className="text-xs text-muted-foreground">
                合計: {uploadPriorRLab.data.total_rows}件 / 成功: {uploadPriorRLab.data.success_rows}件 /
                エラー: {uploadPriorRLab.data.error_rows}件
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
