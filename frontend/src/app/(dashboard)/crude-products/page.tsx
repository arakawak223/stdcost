"use client";

import { useMemo, useState } from "react";
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
  useCrudeProducts,
  useCrudeProductConsolidation,
  useFiscalPeriods,
} from "@/hooks/use-masters";
import {
  crudeProductTypeLabels,
  formatFiscalPeriod,
  formatNumber,
} from "@/lib/format";
import { Layers, List, Search } from "lucide-react";

type TabKey = "list" | "consolidation";

const tabs: { key: TabKey; label: string; icon: typeof List }[] = [
  { key: "list", label: "個別一覧", icon: List },
  { key: "consolidation", label: "名寄せサマリ", icon: Layers },
];

export default function CrudeProductsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("list");
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [consolidationKey, setConsolidationKey] = useState("");
  const [periodId, setPeriodId] = useState("");

  const { data: periods } = useFiscalPeriods();
  const { data: crudeProducts, isLoading } = useCrudeProducts({
    search: search || undefined,
    crude_type: selectedType || undefined,
    sc_consolidation_key: consolidationKey || undefined,
  });
  const {
    data: consolidationGroups,
    isLoading: isConsolidationLoading,
  } = useCrudeProductConsolidation(periodId || undefined);

  const sortedPeriods = useMemo(
    () =>
      periods
        ? [...periods].sort((a, b) => (a.start_date < b.start_date ? 1 : -1))
        : [],
    [periods]
  );

  const handleConsolidationClick = (key: string | null) => {
    if (!key) return;
    setConsolidationKey(key);
    setActiveTab("list");
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">原体マスタ</h2>
        <p className="text-muted-foreground">
          {activeTab === "list"
            ? crudeProducts
              ? `${crudeProducts.length} 件`
              : "読込中..."
            : consolidationGroups
              ? `${consolidationGroups.length} 名寄せグループ`
              : "読込中..."}
          <span className="ml-2 text-xs">
            原体（原液）= 果物・野菜等を発酵・熟成させた中間製品
          </span>
        </p>
      </div>

      {/* タブ */}
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

      {/* Tab 1: 個別一覧 */}
      {activeTab === "list" && (
        <>
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative max-w-sm flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="コード・名前で検索..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Input
              placeholder="名寄せキーで絞込（例: B, HI, P）"
              value={consolidationKey}
              onChange={(e) => setConsolidationKey(e.target.value)}
              className="max-w-xs"
            />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">全タイプ</option>
              <optgroup label="仕込み工程">
                <option value="R1">R1 一次仕込み</option>
                <option value="R2">R2 二次仕込み</option>
                <option value="R3">R3 三次仕込み</option>
                <option value="R">R レギュラー</option>
              </optgroup>
              <optgroup label="R派生工程">
                <option value="Rri">Rリ（リンゴ添加）</option>
                <option value="RB">RB ブレンド</option>
                <option value="Rma">Rマルベリー</option>
                <option value="Rshi">Rシ（生姜系）</option>
                <option value="RG">Rジンジャー</option>
                <option value="RGI">RGI</option>
                <option value="FEB">FEB</option>
              </optgroup>
              <optgroup label="HI系">
                <option value="HI">HI</option>
                <option value="HIA">HI-A</option>
                <option value="HIB">HI-B</option>
                <option value="HIR">HIR</option>
                <option value="HIBkai">HIB海</option>
              </optgroup>
              <optgroup label="その他原液">
                <option value="B">B</option>
                <option value="G">ゴールド</option>
                <option value="GA">GA</option>
                <option value="GB">GB</option>
                <option value="O">O</option>
                <option value="X">X</option>
                <option value="XC">XC</option>
                <option value="BM">BM</option>
                <option value="FB">FB</option>
              </optgroup>
              <optgroup label="製品用仕掛品">
                <option value="P">P（定番）</option>
                <option value="PX">PX</option>
                <option value="PXA">PXA</option>
                <option value="MP">MP マルベリー</option>
                <option value="GP">GP ジンジャープラス</option>
                <option value="LPA">LPA</option>
                <option value="PE">PE（生姜系）</option>
                <option value="T">T（畜産用）</option>
                <option value="RX">RX（植物用）</option>
                <option value="plant">植物用ブレンド</option>
              </optgroup>
              <option value="other">その他</option>
            </select>
            {(search || consolidationKey || selectedType) && (
              <button
                onClick={() => {
                  setSearch("");
                  setConsolidationKey("");
                  setSelectedType("");
                }}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                クリア
              </button>
            )}
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">コード</TableHead>
                  <TableHead>原体名</TableHead>
                  <TableHead className="w-28">タイプ</TableHead>
                  <TableHead className="w-24">名寄せ</TableHead>
                  <TableHead className="w-16">工程</TableHead>
                  <TableHead className="w-20">仕込期</TableHead>
                  <TableHead className="w-16">単位</TableHead>
                  <TableHead className="w-20">状態</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell
                      colSpan={8}
                      className="py-8 text-center text-muted-foreground"
                    >
                      読込中...
                    </TableCell>
                  </TableRow>
                ) : crudeProducts && crudeProducts.length > 0 ? (
                  crudeProducts.map((cp) => (
                    <TableRow key={cp.id}>
                      <TableCell className="font-mono text-sm font-medium">
                        {cp.code}
                      </TableCell>
                      <TableCell>{cp.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {crudeProductTypeLabels[cp.crude_type] || cp.crude_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {cp.sc_consolidation_key ? (
                          <button
                            onClick={() =>
                              setConsolidationKey(cp.sc_consolidation_key!)
                            }
                            className="text-primary hover:underline"
                            title="このキーで絞込"
                          >
                            {cp.sc_consolidation_key}
                          </button>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center font-mono">
                        {cp.process_stage ?? "-"}
                      </TableCell>
                      <TableCell className="font-mono">
                        {cp.vintage_year ? `第${cp.vintage_year}期` : "-"}
                      </TableCell>
                      <TableCell>{cp.unit}</TableCell>
                      <TableCell>
                        <Badge variant={cp.is_active ? "success" : "secondary"}>
                          {cp.is_active ? "有効" : "無効"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={8}
                      className="py-8 text-center text-muted-foreground"
                    >
                      データがありません
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </>
      )}

      {/* Tab 2: 名寄せサマリ */}
      {activeTab === "consolidation" && (
        <>
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium">
                参照期間（SC単価）
              </label>
              <select
                value={periodId}
                onChange={(e) => setPeriodId(e.target.value)}
                className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              >
                <option value="">全期間（単価表示なし）</option>
                {sortedPeriods.map((p) => (
                  <option key={p.id} value={p.id}>
                    {formatFiscalPeriod(p.year, p.month, p.start_date)}
                  </option>
                ))}
              </select>
            </div>
            <p className="text-xs text-muted-foreground">
              ※ 期間を指定すると material_standard_costs から SC 単価の min/max/avg
              を集計します。
            </p>
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-28">名寄せキー</TableHead>
                  <TableHead className="w-20 text-right">件数</TableHead>
                  <TableHead className="w-32 text-right">単価 min</TableHead>
                  <TableHead className="w-32 text-right">単価 max</TableHead>
                  <TableHead className="w-32 text-right">単価 avg</TableHead>
                  <TableHead>含まれる個別コード（先頭10件）</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isConsolidationLoading ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="py-8 text-center text-muted-foreground"
                    >
                      読込中...
                    </TableCell>
                  </TableRow>
                ) : consolidationGroups && consolidationGroups.length > 0 ? (
                  consolidationGroups.map((g, idx) => (
                    <TableRow
                      key={g.sc_consolidation_key ?? `_null_${idx}`}
                      onClick={() =>
                        handleConsolidationClick(g.sc_consolidation_key)
                      }
                      className={
                        g.sc_consolidation_key
                          ? "cursor-pointer hover:bg-muted/50"
                          : ""
                      }
                    >
                      <TableCell className="font-mono font-medium">
                        {g.sc_consolidation_key ? (
                          <span className="text-primary">
                            {g.sc_consolidation_key}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">(未設定)</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {g.item_count}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {g.unit_cost_min !== null
                          ? formatNumber(g.unit_cost_min, 2)
                          : "-"}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {g.unit_cost_max !== null
                          ? formatNumber(g.unit_cost_max, 2)
                          : "-"}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {g.unit_cost_avg !== null
                          ? formatNumber(g.unit_cost_avg, 2)
                          : "-"}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {g.sample_codes.join(", ")}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="py-8 text-center text-muted-foreground"
                    >
                      データがありません
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </>
      )}
    </div>
  );
}
