"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
  useStandardCosts,
  useCrudeProductStandardCosts,
  useCalculateStandardCosts,
  useSimulateStandardCosts,
} from "@/hooks/use-costs";
import { useFiscalPeriods, useCrudeProducts } from "@/hooks/use-masters";
import { useProducts } from "@/hooks/use-products";
import { formatCurrency, formatNumber, formatFiscalPeriod } from "@/lib/format";
import { Calculator, Beaker, Package, FlaskConical } from "lucide-react";
import type { CalculationResult } from "@/lib/api-client";

type TabId = "crude" | "product" | "calculate" | "simulate";

export default function StandardCostsPage() {
  const [activeTab, setActiveTab] = useState<TabId>("crude");
  const [selectedPeriodId, setSelectedPeriodId] = useState("");

  const { data: periods } = useFiscalPeriods({ year: 38 });
  const { data: crudeProducts } = useCrudeProducts();
  const { data: products } = useProducts();

  const cpMap = Object.fromEntries((crudeProducts || []).map((cp) => [cp.id, cp]));
  const prodMap = Object.fromEntries((products || []).map((p) => [p.id, p]));

  const tabs = [
    { id: "crude" as TabId, label: "原体標準原価", icon: Beaker },
    { id: "product" as TabId, label: "製品標準原価", icon: Package },
    { id: "calculate" as TabId, label: "計算実行", icon: Calculator },
    { id: "simulate" as TabId, label: "シミュレーション", icon: FlaskConical },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">標準原価計算</h2>
        <p className="text-muted-foreground">BOMベースの2段階標準原価積上計算</p>
      </div>

      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">会計期間:</label>
        <select
          className="rounded border bg-background px-3 py-2 text-sm"
          value={selectedPeriodId}
          onChange={(e) => setSelectedPeriodId(e.target.value)}
        >
          <option value="">選択してください</option>
          {periods?.map((p) => (
            <option key={p.id} value={p.id}>
              {formatFiscalPeriod(p.year, p.month)}
            </option>
          ))}
        </select>
      </div>

      <div className="flex gap-1 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "crude" && (
        <CrudeProductCostTab periodId={selectedPeriodId} cpMap={cpMap} />
      )}
      {activeTab === "product" && (
        <ProductCostTab periodId={selectedPeriodId} prodMap={prodMap} />
      )}
      {activeTab === "calculate" && (
        <CalculateTab periodId={selectedPeriodId} cpMap={cpMap} prodMap={prodMap} />
      )}
      {activeTab === "simulate" && (
        <SimulateTab periodId={selectedPeriodId} cpMap={cpMap} prodMap={prodMap} />
      )}
    </div>
  );
}

function CrudeProductCostTab({
  periodId,
  cpMap,
}: {
  periodId: string;
  cpMap: Record<string, { code: string; name: string }>;
}) {
  const { data: costs, isLoading } = useCrudeProductStandardCosts(
    periodId ? { period_id: periodId } : undefined
  );

  if (!periodId) return <p className="text-muted-foreground">会計期間を選択してください</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>原体標準原価一覧</CardTitle>
        <CardDescription>Stage 1: 製造部での原体原価計算結果</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-muted-foreground">読み込み中...</p>
        ) : !costs?.length ? (
          <p className="text-muted-foreground">データがありません。「計算実行」タブで計算を実行してください。</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>原体</TableHead>
                <TableHead className="text-right">原材料費</TableHead>
                <TableHead className="text-right">労務費</TableHead>
                <TableHead className="text-right">経費</TableHead>
                <TableHead className="text-right">前工程費</TableHead>
                <TableHead className="text-right">合計</TableHead>
                <TableHead className="text-right">kg単価</TableHead>
                <TableHead className="text-right">標準数量</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {costs.map((c) => {
                const cp = cpMap[c.crude_product_id];
                return (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">
                      {cp ? `${cp.code} - ${cp.name}` : c.crude_product_id}
                    </TableCell>
                    <TableCell className="text-right">{formatCurrency(c.material_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.labor_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.overhead_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.prior_process_cost)}</TableCell>
                    <TableCell className="text-right font-bold">{formatCurrency(c.total_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.unit_cost)}</TableCell>
                    <TableCell className="text-right">{formatNumber(c.standard_quantity, 2)}kg</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function ProductCostTab({
  periodId,
  prodMap,
}: {
  periodId: string;
  prodMap: Record<string, { code: string; name: string }>;
}) {
  const { data: costs, isLoading } = useStandardCosts(
    periodId ? { period_id: periodId } : undefined
  );

  if (!periodId) return <p className="text-muted-foreground">会計期間を選択してください</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>製品標準原価一覧</CardTitle>
        <CardDescription>Stage 2: 製品課での製品原価計算結果</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-muted-foreground">読み込み中...</p>
        ) : !costs?.length ? (
          <p className="text-muted-foreground">データがありません。「計算実行」タブで計算を実行してください。</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>製品</TableHead>
                <TableHead className="text-right">原体費</TableHead>
                <TableHead className="text-right">資材費</TableHead>
                <TableHead className="text-right">労務費</TableHead>
                <TableHead className="text-right">経費</TableHead>
                <TableHead className="text-right">外注費</TableHead>
                <TableHead className="text-right">合計</TableHead>
                <TableHead className="text-right">単価</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {costs.map((c) => {
                const prod = prodMap[c.product_id];
                return (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">
                      {prod ? `${prod.code} - ${prod.name}` : c.product_id}
                    </TableCell>
                    <TableCell className="text-right">{formatCurrency(c.crude_product_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.packaging_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.labor_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.overhead_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.outsourcing_cost)}</TableCell>
                    <TableCell className="text-right font-bold">{formatCurrency(c.total_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(c.unit_cost)}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function CalculateTab({
  periodId,
  cpMap,
  prodMap,
}: {
  periodId: string;
  cpMap: Record<string, { code: string; name: string }>;
  prodMap: Record<string, { code: string; name: string }>;
}) {
  const calculate = useCalculateStandardCosts();
  const [result, setResult] = useState<CalculationResult | null>(null);

  const handleCalculate = async () => {
    if (!periodId) return;
    const res = await calculate.mutateAsync({ period_id: periodId });
    setResult(res);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>標準原価計算の実行</CardTitle>
          <CardDescription>
            選択した会計期間のBOM・予算データに基づいて標準原価を計算し、結果をDBに保存します。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!periodId ? (
            <p className="text-muted-foreground">会計期間を選択してください</p>
          ) : (
            <>
              <Button onClick={handleCalculate} disabled={calculate.isPending}>
                <Calculator className="mr-2 h-4 w-4" />
                {calculate.isPending ? "計算中..." : "計算実行"}
              </Button>

              {result && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                    <Card>
                      <CardContent className="pt-4">
                        <p className="text-sm text-muted-foreground">原体計算数</p>
                        <p className="text-2xl font-bold">{result.crude_products_calculated}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-4">
                        <p className="text-sm text-muted-foreground">製品計算数</p>
                        <p className="text-2xl font-bold">{result.products_calculated}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-4">
                        <p className="text-sm text-muted-foreground">原体原価合計</p>
                        <p className="text-2xl font-bold">{formatCurrency(result.total_crude_product_cost)}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-4">
                        <p className="text-sm text-muted-foreground">製品原価合計</p>
                        <p className="text-2xl font-bold">{formatCurrency(result.total_product_cost)}</p>
                      </CardContent>
                    </Card>
                  </div>
                  <Badge variant="success">計算完了 - 結果がDBに保存されました</Badge>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function SimulateTab({
  periodId,
  cpMap,
  prodMap,
}: {
  periodId: string;
  cpMap: Record<string, { code: string; name: string }>;
  prodMap: Record<string, { code: string; name: string }>;
}) {
  const simulate = useSimulateStandardCosts();
  const [result, setResult] = useState<CalculationResult | null>(null);

  const handleSimulate = async () => {
    if (!periodId) return;
    const res = await simulate.mutateAsync({ period_id: periodId });
    setResult(res);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>シミュレーション</CardTitle>
          <CardDescription>
            DBに保存せずに標準原価を試算します。単価変更や予算変更の影響を確認できます。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!periodId ? (
            <p className="text-muted-foreground">会計期間を選択してください</p>
          ) : (
            <>
              <Button onClick={handleSimulate} disabled={simulate.isPending} variant="outline">
                <FlaskConical className="mr-2 h-4 w-4" />
                {simulate.isPending ? "シミュレーション中..." : "シミュレーション実行"}
              </Button>

              {result && (
                <div className="space-y-4">
                  <Badge variant="warning">シミュレーション結果（DB保存なし）</Badge>
                  <div className="grid grid-cols-2 gap-4">
                    <Card>
                      <CardContent className="pt-4">
                        <p className="text-sm text-muted-foreground">原体計算数</p>
                        <p className="text-2xl font-bold">{result.crude_products_calculated}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-4">
                        <p className="text-sm text-muted-foreground">製品計算数</p>
                        <p className="text-2xl font-bold">{result.products_calculated}</p>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
