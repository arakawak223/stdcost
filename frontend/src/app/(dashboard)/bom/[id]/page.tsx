"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BomLineEditor } from "@/components/bom-line-editor";
import { useBomHeader, useCreateBom, useUpdateBom } from "@/hooks/use-bom";
import { useMaterials, useCrudeProducts } from "@/hooks/use-masters";
import type { BomLineCreate, BomType } from "@/lib/api-client";
import { ArrowLeft, Save } from "lucide-react";
import Link from "next/link";

export default function BomEditPage() {
  const params = useParams();
  const router = useRouter();
  const isNew = params.id === "new";
  const bomId = isNew ? "" : (params.id as string);

  const { data: bom } = useBomHeader(bomId);
  const { data: materials } = useMaterials({ per_page: 200 });
  const { data: crudeProducts } = useCrudeProducts({ per_page: 200 });
  const createBom = useCreateBom();
  const updateBom = useUpdateBom();

  const [bomType, setBomType] = useState<BomType>("raw_material_process");
  const [productId, setProductId] = useState("");
  const [crudeProductId, setCrudeProductId] = useState("");
  const [effectiveDate, setEffectiveDate] = useState("2024-10-01");
  const [yieldRate, setYieldRate] = useState("1.0000");
  const [notes, setNotes] = useState("");
  const [lines, setLines] = useState<BomLineCreate[]>([]);

  useEffect(() => {
    if (bom) {
      setBomType(bom.bom_type);
      setProductId(bom.product_id || "");
      setCrudeProductId(bom.crude_product_id || "");
      setEffectiveDate(bom.effective_date);
      setYieldRate(bom.yield_rate);
      setNotes(bom.notes || "");
      setLines(
        bom.lines.map((l) => ({
          material_id: l.material_id,
          crude_product_id: l.crude_product_id,
          quantity: l.quantity,
          unit: l.unit,
          loss_rate: l.loss_rate,
          sort_order: l.sort_order,
        }))
      );
    }
  }, [bom]);

  const handleSave = async () => {
    const data = {
      bom_type: bomType,
      product_id: productId || null,
      crude_product_id: crudeProductId || null,
      effective_date: effectiveDate,
      yield_rate: yieldRate,
      notes: notes || null,
      lines,
    };

    if (isNew) {
      await createBom.mutateAsync(data);
    } else {
      await updateBom.mutateAsync({ id: bomId, data });
    }
    router.push("/bom");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/bom">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-1 h-4 w-4" />
            戻る
          </Button>
        </Link>
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            {isNew ? "新規BOM作成" : "BOM編集"}
          </h2>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>BOMヘッダー</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>工程タイプ</Label>
              <select
                className="w-full rounded border bg-background px-3 py-2 text-sm"
                value={bomType}
                onChange={(e) => setBomType(e.target.value as BomType)}
              >
                <option value="raw_material_process">原体工程（原料→原体）</option>
                <option value="product_process">製品工程（原体→製品）</option>
              </select>
            </div>

            {bomType === "raw_material_process" ? (
              <div className="space-y-2">
                <Label>出力原体</Label>
                <select
                  className="w-full rounded border bg-background px-3 py-2 text-sm"
                  value={crudeProductId}
                  onChange={(e) => setCrudeProductId(e.target.value)}
                >
                  <option value="">選択してください</option>
                  {crudeProducts?.map((cp) => (
                    <option key={cp.id} value={cp.id}>
                      {cp.code} - {cp.name}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="space-y-2">
                <Label>出力製品</Label>
                <select
                  className="w-full rounded border bg-background px-3 py-2 text-sm"
                  value={productId}
                  onChange={(e) => setProductId(e.target.value)}
                >
                  <option value="">選択してください</option>
                  {/* Products would be loaded from useProducts */}
                </select>
              </div>
            )}

            <div className="space-y-2">
              <Label>有効日</Label>
              <Input
                type="date"
                value={effectiveDate}
                onChange={(e) => setEffectiveDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>歩留率</Label>
              <Input
                type="number"
                step="0.0001"
                value={yieldRate}
                onChange={(e) => setYieldRate(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>メモ</Label>
            <Input
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="メモ（任意）"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>BOM明細行</CardTitle>
        </CardHeader>
        <CardContent>
          <BomLineEditor
            lines={lines}
            onChange={setLines}
            materials={materials || []}
            crudeProducts={crudeProducts || []}
            bomType={bomType}
          />
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={createBom.isPending || updateBom.isPending}>
          <Save className="mr-2 h-4 w-4" />
          {isNew ? "作成" : "更新"}
        </Button>
      </div>
    </div>
  );
}
