"use client";

import { useState } from "react";
import { Bot, MessageSquare, History, AlertTriangle, CheckCircle, XCircle, Loader2 } from "lucide-react";
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
import { useFiscalPeriods } from "@/hooks/use-masters";
import { useVarianceRecords } from "@/hooks/use-variance";
import {
  useAIExplanations,
  useExplainVariance,
  useAskQuestion,
  useUpdateAIExplanation,
} from "@/hooks/use-ai";
import { formatDateTime, formatCurrency, formatPercent, formatFiscalPeriod, costElementLabels, reviewStatusLabels } from "@/lib/format";
import type { AIExplanationResponse } from "@/lib/api-client";

const reviewStatusVariant: Record<string, "default" | "secondary" | "success" | "warning" | "outline"> = {
  pending: "secondary",
  approved: "success",
  rejected: "warning",
};

export default function AIAssistantPage() {
  const [activeTab, setActiveTab] = useState<"variance" | "qa" | "history">("variance");
  const [periodId, setPeriodId] = useState("");
  const [selectedVarianceId, setSelectedVarianceId] = useState("");
  const [varianceResult, setVarianceResult] = useState<AIExplanationResponse | null>(null);
  const [question, setQuestion] = useState("");
  const [qaResult, setQaResult] = useState<AIExplanationResponse | null>(null);

  const { data: periods } = useFiscalPeriods();
  const { data: flaggedRecords } = useVarianceRecords(
    periodId ? { period_id: periodId, is_flagged: true } : undefined
  );
  const { data: explanations } = useAIExplanations();
  const explainVariance = useExplainVariance();
  const askQuestion = useAskQuestion();
  const updateExplanation = useUpdateAIExplanation();

  const handleExplainVariance = async () => {
    if (!selectedVarianceId) return;
    const result = await explainVariance.mutateAsync(selectedVarianceId);
    setVarianceResult(result);
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    const result = await askQuestion.mutateAsync({ question });
    setQaResult(result);
    setQuestion("");
  };

  const handleReview = async (id: string, status: "approved" | "rejected") => {
    await updateExplanation.mutateAsync({ id, data: { review_status: status } });
  };

  const tabs = [
    { key: "variance" as const, label: "差異分析AI", icon: AlertTriangle },
    { key: "qa" as const, label: "質問応答", icon: MessageSquare },
    { key: "history" as const, label: "履歴", icon: History },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Bot className="h-6 w-6" />
        AIアシスタント
      </h1>

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

      {/* Tab 1: 差異分析AI */}
      {activeTab === "variance" && (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium">会計期間:</label>
            <select
              className="rounded-md border px-3 py-2 text-sm"
              value={periodId}
              onChange={(e) => {
                setPeriodId(e.target.value);
                setSelectedVarianceId("");
                setVarianceResult(null);
              }}
            >
              <option value="">選択...</option>
              {periods?.map((p) => (
                <option key={p.id} value={p.id}>
                  {formatFiscalPeriod(p.year, p.month)}
                </option>
              ))}
            </select>
          </div>

          {periodId && flaggedRecords && flaggedRecords.length === 0 && (
            <p className="text-muted-foreground">フラグ付き差異レコードがありません。差異分析を実行してください。</p>
          )}

          {flaggedRecords && flaggedRecords.length > 0 && (
            <div className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>選択</TableHead>
                    <TableHead>原価要素</TableHead>
                    <TableHead className="text-right">差異額</TableHead>
                    <TableHead className="text-right">差異率</TableHead>
                    <TableHead>フラグ理由</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {flaggedRecords.map((r) => (
                    <TableRow
                      key={r.id}
                      className={selectedVarianceId === r.id ? "bg-primary/5" : ""}
                    >
                      <TableCell>
                        <input
                          type="radio"
                          name="variance"
                          checked={selectedVarianceId === r.id}
                          onChange={() => setSelectedVarianceId(r.id)}
                        />
                      </TableCell>
                      <TableCell>{costElementLabels[r.cost_element] || r.cost_element}</TableCell>
                      <TableCell className={`text-right font-medium ${r.is_favorable ? "text-green-600" : "text-red-600"}`}>
                        {formatCurrency(r.variance_amount)}
                      </TableCell>
                      <TableCell className="text-right">{formatPercent(r.variance_percent)}</TableCell>
                      <TableCell className="text-sm">{r.flag_reason || "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <Button
                onClick={handleExplainVariance}
                disabled={!selectedVarianceId || explainVariance.isPending}
              >
                {explainVariance.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    分析中...
                  </>
                ) : (
                  <>
                    <Bot className="mr-2 h-4 w-4" />
                    AIに分析依頼
                  </>
                )}
              </Button>

              {explainVariance.error && (
                <p className="text-sm text-destructive">{(explainVariance.error as Error).message}</p>
              )}
            </div>
          )}

          {varianceResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  AI分析結果
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="whitespace-pre-wrap rounded-md bg-muted p-4 text-sm">
                  {varianceResult.explanation.response}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleReview(varianceResult.explanation.id, "approved")}
                  >
                    <CheckCircle className="mr-1 h-4 w-4 text-green-600" />
                    承認
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleReview(varianceResult.explanation.id, "rejected")}
                  >
                    <XCircle className="mr-1 h-4 w-4 text-red-600" />
                    却下
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  モデル: {varianceResult.explanation.model} / トークン: {varianceResult.explanation.input_tokens} + {varianceResult.explanation.output_tokens}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Tab 2: 質問応答 */}
      {activeTab === "qa" && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>質問を入力</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <textarea
                className="w-full rounded-md border px-3 py-2 text-sm"
                rows={4}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="例: 今期の原材料費が上昇した主な要因は何ですか？"
              />
              <Button
                onClick={handleAsk}
                disabled={!question.trim() || askQuestion.isPending}
              >
                {askQuestion.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    回答生成中...
                  </>
                ) : (
                  "送信"
                )}
              </Button>
              {askQuestion.error && (
                <p className="text-sm text-destructive">{(askQuestion.error as Error).message}</p>
              )}
            </CardContent>
          </Card>

          {qaResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  AI回答
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-md border bg-muted/50 p-3 text-sm">
                  <p className="mb-1 font-medium text-muted-foreground">質問:</p>
                  <p>{qaResult.explanation.prompt}</p>
                </div>
                <div className="whitespace-pre-wrap rounded-md bg-muted p-4 text-sm">
                  {qaResult.explanation.response}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleReview(qaResult.explanation.id, "approved")}
                  >
                    <CheckCircle className="mr-1 h-4 w-4 text-green-600" />
                    承認
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleReview(qaResult.explanation.id, "rejected")}
                  >
                    <XCircle className="mr-1 h-4 w-4 text-red-600" />
                    却下
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Tab 3: 履歴 */}
      {activeTab === "history" && (
        <div>
          {explanations && explanations.length === 0 && (
            <p className="text-muted-foreground">AI説明の履歴がありません。</p>
          )}
          {explanations && explanations.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>タイプ</TableHead>
                  <TableHead>プロンプト（抜粋）</TableHead>
                  <TableHead>モデル</TableHead>
                  <TableHead>トークン</TableHead>
                  <TableHead>ステータス</TableHead>
                  <TableHead>日時</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {explanations.map((ex) => (
                  <TableRow key={ex.id}>
                    <TableCell>
                      <Badge variant="outline">{ex.context_type}</Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate text-sm">
                      {ex.prompt.slice(0, 80)}...
                    </TableCell>
                    <TableCell className="text-sm">{ex.model}</TableCell>
                    <TableCell className="text-sm">{ex.input_tokens + ex.output_tokens}</TableCell>
                    <TableCell>
                      <Badge variant={reviewStatusVariant[ex.review_status] || "secondary"}>
                        {reviewStatusLabels[ex.review_status] || ex.review_status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDateTime(ex.created_at)}
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
