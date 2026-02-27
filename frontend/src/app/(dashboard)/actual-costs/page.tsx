"use client";

import { useState, useMemo } from "react";
import { DollarSign, Beaker } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useFiscalPeriods, useCrudeProducts } from "@/hooks/use-masters";
import { useProducts } from "@/hooks/use-products";
import { useActualCosts, useCrudeProductActualCosts } from "@/hooks/use-actual-costs";
import { formatCurrency, formatNumber, formatFiscalPeriod, sourceSystemLabels, costElementLabels } from "@/lib/format";

export default function ActualCostsPage() {
  const [activeTab, setActiveTab] = useState<"product" | "crude">("product");
  const [periodId, setPeriodId] = useState("");

  const { data: periods } = useFiscalPeriods();
  const { data: products } = useProducts();
  const { data: crudeProducts } = useCrudeProducts();
  const { data: actualCosts } = useActualCosts(periodId ? { period_id: periodId } : undefined);
  const { data: crudeActualCosts } = useCrudeProductActualCosts(periodId ? { period_id: periodId } : undefined);

  const productMap = useMemo(() => {
    const m = new Map<string, string>();
    products?.forEach((p) => m.set(p.id, p.name));
    return m;
  }, [products]);

  const crudeProductMap = useMemo(() => {
    const m = new Map<string, string>();
    crudeProducts?.forEach((p) => m.set(p.id, p.name));
    return m;
  }, [crudeProducts]);

  const tabs = [
    { key: "product" as const, label: "製品実際原価", icon: DollarSign },
    { key: "crude" as const, label: "原体実際原価", icon: Beaker },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">実際原価</h1>

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

      {!periodId && <p className="text-muted-foreground">会計期間を選択してください。</p>}

      {/* Tab 1: Product Actual Costs */}
      {activeTab === "product" && periodId && (
        <div>
          {actualCosts && actualCosts.length === 0 && (
            <p className="text-muted-foreground">実際原価データがありません。</p>
          )}
          {actualCosts && actualCosts.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>製品</TableHead>
                  <TableHead className="text-right">{costElementLabels.crude_product}</TableHead>
                  <TableHead className="text-right">{costElementLabels.packaging}</TableHead>
                  <TableHead className="text-right">{costElementLabels.labor}</TableHead>
                  <TableHead className="text-right">{costElementLabels.overhead}</TableHead>
                  <TableHead className="text-right">{costElementLabels.outsourcing}</TableHead>
                  <TableHead className="text-right">合計</TableHead>
                  <TableHead className="text-right">生産数量</TableHead>
                  <TableHead>ソース</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {actualCosts.map((ac) => (
                  <TableRow key={ac.id}>
                    <TableCell className="font-medium">
                      {productMap.get(ac.product_id) || ac.product_id.slice(0, 8)}
                    </TableCell>
                    <TableCell className="text-right">{formatCurrency(ac.crude_product_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(ac.packaging_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(ac.labor_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(ac.overhead_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(ac.outsourcing_cost)}</TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(ac.total_cost)}</TableCell>
                    <TableCell className="text-right">{formatNumber(ac.quantity_produced, 2)}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{sourceSystemLabels[ac.source_system] || ac.source_system}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      )}

      {/* Tab 2: Crude Product Actual Costs */}
      {activeTab === "crude" && periodId && (
        <div>
          {crudeActualCosts && crudeActualCosts.length === 0 && (
            <p className="text-muted-foreground">原体実際原価データがありません。</p>
          )}
          {crudeActualCosts && crudeActualCosts.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>原体</TableHead>
                  <TableHead className="text-right">{costElementLabels.material}</TableHead>
                  <TableHead className="text-right">{costElementLabels.labor}</TableHead>
                  <TableHead className="text-right">{costElementLabels.overhead}</TableHead>
                  <TableHead className="text-right">{costElementLabels.prior_process}</TableHead>
                  <TableHead className="text-right">合計</TableHead>
                  <TableHead className="text-right">実際数量(kg)</TableHead>
                  <TableHead>ソース</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {crudeActualCosts.map((cc) => (
                  <TableRow key={cc.id}>
                    <TableCell className="font-medium">
                      {crudeProductMap.get(cc.crude_product_id) || cc.crude_product_id.slice(0, 8)}
                    </TableCell>
                    <TableCell className="text-right">{formatCurrency(cc.material_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(cc.labor_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(cc.overhead_cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(cc.prior_process_cost)}</TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(cc.total_cost)}</TableCell>
                    <TableCell className="text-right">{formatNumber(cc.actual_quantity, 2)}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{sourceSystemLabels[cc.source_system] || cc.source_system}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      )}
    </div>
  );
}
