"""Claude AI integration service (Phase 5).

万田発酵の標準原価計算における差異分析・期間レポート・汎用Q&AにAI説明を提供する。
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.audit import AIExplanation, ReviewStatus
from app.models.cost import ActualCost, StandardCost
from app.models.master import Product
from app.models.variance import VarianceRecord

SYSTEM_PROMPT = """あなたは万田発酵株式会社の経理部門向け原価分析AIアシスタントです。

【企業概要】
- 万田発酵は53種類以上の植物原材料を使用した発酵食品を製造
- 主力製品: 万田酵素（ペースト・粒・ドリンク等）
- 製造工程: 原材料仕込み → 発酵・熟成（3年3ヶ月以上）→ ブレンド → 製品化
- 原体タイプ: レギュラー(R), HI, ゴールド(G), スペシャル(SP), ジンジャー(GN)

【原価構造】
- 原材料費: 果物・野菜・穀物・海藻等（季節変動あり）
- 労務費: 製造部・製品課の人件費
- 経費(製造間接費): 設備減価償却・光熱費等
- 外注加工費: 外注製品の加工委託費
- 前工程費: ブレンド製品における原液の移転原価

【分析ポイント】
- 原材料の季節変動（果物は夏秋に高騰）
- 熟成期間による在庫評価の複雑さ
- ブレンド比率変更による原体原価への影響
- 外注vs内製の原価比較

回答は日本語で、簡潔かつ具体的に。数値の根拠を示し、改善提案があれば付記してください。"""

MODEL = "claude-sonnet-4-20250514"


def _get_client():
    """AsyncAnthropic clientを取得。APIキー未設定時はNone。"""
    if not settings.anthropic_api_key:
        return None
    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=settings.anthropic_api_key)


async def explain_variance(db: AsyncSession, variance_record_id: uuid.UUID) -> AIExplanation:
    """フラグ付き差異レコードのAI説明を生成する。"""
    client = _get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY が設定されていません")

    # Load variance record
    result = await db.execute(
        select(VarianceRecord).where(VarianceRecord.id == variance_record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise ValueError("差異レコードが見つかりません")

    # Load related data
    product_result = await db.execute(
        select(Product).where(Product.id == record.product_id)
    )
    product = product_result.scalar_one_or_none()

    std_result = await db.execute(
        select(StandardCost).where(
            StandardCost.product_id == record.product_id,
            StandardCost.period_id == record.period_id,
        )
    )
    std_cost = std_result.scalar_one_or_none()

    act_result = await db.execute(
        select(ActualCost).where(
            ActualCost.product_id == record.product_id,
            ActualCost.period_id == record.period_id,
        )
    )
    act_cost = act_result.scalar_one_or_none()

    # Build prompt
    prompt = f"""以下の差異レコードについて分析・説明してください。

【差異レコード】
- 製品: {product.name if product else 'N/A'} ({product.code if product else 'N/A'})
- 原価要素: {record.cost_element}
- 差異タイプ: {record.variance_type.value if record.variance_type else 'N/A'}
- 標準額: {record.standard_amount:,.0f}円
- 実際額: {record.actual_amount:,.0f}円
- 差異額: {record.variance_amount:,.0f}円
- 差異率: {record.variance_percent:.1f}%
- 有利/不利: {'有利差異' if record.is_favorable else '不利差異'}
- フラグ理由: {record.flag_reason or 'なし'}"""

    if std_cost:
        prompt += f"""

【標準原価内訳】
- 原体原価: {std_cost.crude_product_cost:,.0f}円
- 資材費: {std_cost.packaging_cost:,.0f}円
- 労務費: {std_cost.labor_cost:,.0f}円
- 経費: {std_cost.overhead_cost:,.0f}円
- 外注費: {std_cost.outsourcing_cost:,.0f}円
- 合計: {std_cost.total_cost:,.0f}円"""

    if act_cost:
        prompt += f"""

【実際原価内訳】
- 原体原価: {act_cost.crude_product_cost:,.0f}円
- 資材費: {act_cost.packaging_cost:,.0f}円
- 労務費: {act_cost.labor_cost:,.0f}円
- 経費: {act_cost.overhead_cost:,.0f}円
- 外注費: {act_cost.outsourcing_cost:,.0f}円
- 合計: {act_cost.total_cost:,.0f}円"""

    prompt += """

上記データに基づき、以下を回答してください:
1. 差異の主要因の分析
2. 考えられる原因（季節性、数量変動、価格変動等）
3. 改善提案（あれば）"""

    # Call Claude API
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text

    # Save AIExplanation
    explanation = AIExplanation(
        context_type="variance_record",
        context_id=str(variance_record_id),
        prompt=prompt,
        response=response_text,
        model=MODEL,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        review_status=ReviewStatus.pending,
    )
    db.add(explanation)
    await db.flush()
    await db.refresh(explanation)
    return explanation


async def explain_period_summary(db: AsyncSession, period_id: uuid.UUID) -> AIExplanation:
    """期間全体の差異サマリーをAI分析する。"""
    client = _get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY が設定されていません")

    # Load all variance records for the period
    result = await db.execute(
        select(VarianceRecord).where(VarianceRecord.period_id == period_id)
    )
    records = result.scalars().all()

    if not records:
        raise ValueError("差異レコードが見つかりません（先に差異分析を実行してください）")

    # Summarize
    total_std = sum(float(r.standard_amount) for r in records)
    total_act = sum(float(r.actual_amount) for r in records)
    total_var = sum(float(r.variance_amount) for r in records)
    flagged = [r for r in records if r.is_flagged]

    # Group by cost element
    by_element: dict[str, list] = {}
    for r in records:
        by_element.setdefault(r.cost_element, []).append(r)

    element_summary = ""
    for elem, recs in by_element.items():
        elem_var = sum(float(r.variance_amount) for r in recs)
        elem_flagged = sum(1 for r in recs if r.is_flagged)
        element_summary += f"  - {elem}: 差異合計 {elem_var:,.0f}円, フラグ {elem_flagged}件\n"

    prompt = f"""以下の期間差異サマリーについて総合分析してください。

【期間サマリー】
- レコード数: {len(records)}件
- フラグ付き: {len(flagged)}件
- 標準原価合計: {total_std:,.0f}円
- 実際原価合計: {total_act:,.0f}円
- 差異合計: {total_var:,.0f}円

【原価要素別】
{element_summary}

以下を回答してください:
1. 期間全体の差異傾向の分析
2. 特に注目すべき原価要素とその理由
3. 次期に向けた改善提案"""

    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text

    explanation = AIExplanation(
        context_type="period_summary",
        context_id=str(period_id),
        prompt=prompt,
        response=response_text,
        model=MODEL,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        review_status=ReviewStatus.pending,
    )
    db.add(explanation)
    await db.flush()
    await db.refresh(explanation)
    return explanation


async def ask_question(
    db: AsyncSession,
    question: str,
    context_type: str | None = None,
    context_id: uuid.UUID | None = None,
) -> AIExplanation:
    """汎用Q&A — ユーザーの質問にAIが回答する。"""
    client = _get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY が設定されていません")

    prompt = question

    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text

    explanation = AIExplanation(
        context_type=context_type or "question",
        context_id=str(context_id) if context_id else None,
        prompt=prompt,
        response=response_text,
        model=MODEL,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        review_status=ReviewStatus.pending,
    )
    db.add(explanation)
    await db.flush()
    await db.refresh(explanation)
    return explanation
