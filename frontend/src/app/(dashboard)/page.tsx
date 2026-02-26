"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useProducts, useProductCount, useProductGroups } from "@/hooks/use-products";
import { useCostCenters, useMaterials, useCrudeProducts, useFiscalPeriods } from "@/hooks/use-masters";
import { Package, Beaker, Building2, FlaskConical, Calendar } from "lucide-react";
import { periodStatusLabels } from "@/lib/format";

export default function DashboardPage() {
  const { data: productCount } = useProductCount();
  const { data: costCenters } = useCostCenters();
  const { data: materials } = useMaterials();
  const { data: crudeProducts } = useCrudeProducts();
  const { data: periods } = useFiscalPeriods();
  const { data: productGroups } = useProductGroups();

  const openPeriods = periods?.filter((p) => p.status === "open") || [];
  const closingPeriods = periods?.filter((p) => p.status === "closing") || [];

  const stats = [
    {
      title: "製品数",
      value: productCount?.count ?? "...",
      description: `${productGroups?.length ?? 0} 製品群`,
      icon: Package,
    },
    {
      title: "原体数",
      value: crudeProducts?.length ?? "...",
      description: "発酵原液マスタ",
      icon: Beaker,
    },
    {
      title: "原材料数",
      value: materials?.length ?? "...",
      description: "果物・野菜・穀物・資材",
      icon: FlaskConical,
    },
    {
      title: "会計期間",
      value: `${openPeriods.length} オープン`,
      description: `${closingPeriods.length} 締め処理中`,
      icon: Calendar,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">ダッシュボード</h2>
        <p className="text-muted-foreground">標準原価計算システムの概況</p>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Phase status */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">実装フェーズ</CardTitle>
            <CardDescription>現在のシステム開発状況</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Phase 1: 基盤構築</span>
              <Badge variant="success">完了</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Phase 2: BOM・標準原価エンジン</span>
              <Badge variant="success">完了</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Phase 3: データ取込・実際原価</span>
              <Badge variant="outline">未着手</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Phase 4: 差異分析</span>
              <Badge variant="outline">未着手</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Phase 5: AI連携</span>
              <Badge variant="outline">未着手</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Phase 6: 仕上げ・本番準備</span>
              <Badge variant="outline">未着手</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">会計期間ステータス</CardTitle>
            <CardDescription>直近の会計期間（第38期）</CardDescription>
          </CardHeader>
          <CardContent>
            {periods && periods.length > 0 ? (
              <div className="space-y-2">
                {periods.slice(-6).reverse().map((p) => (
                  <div key={p.id} className="flex items-center justify-between text-sm">
                    <span>
                      第{p.year}期 第{p.month}月
                    </span>
                    <Badge
                      variant={
                        p.status === "open"
                          ? "success"
                          : p.status === "closing"
                            ? "warning"
                            : "secondary"
                      }
                    >
                      {periodStatusLabels[p.status] || p.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                会計期間データがありません。シードデータを投入してください。
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
