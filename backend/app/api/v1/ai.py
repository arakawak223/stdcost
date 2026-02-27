"""AI Assistant API — Claude AIによる差異分析説明・Q&A (Phase 5)。"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.audit import AIExplanation, ReviewStatus
from app.schemas.ai_explanation import (
    AIExplanationRead,
    AIExplanationResponse,
    AIExplanationUpdate,
    AskQuestionRequest,
    ExplainPeriodRequest,
    ExplainVarianceRequest,
)
from app.services.ai_agent import ask_question, explain_period_summary, explain_variance

router = APIRouter()


@router.post("/explain/variance", response_model=AIExplanationResponse)
async def ai_explain_variance(
    data: ExplainVarianceRequest, db: AsyncSession = Depends(get_db)
):
    """差異レコードのAI分析を実行する。"""
    try:
        explanation = await explain_variance(db, data.variance_record_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析エラー: {e}")
    return AIExplanationResponse(
        explanation=AIExplanationRead.model_validate(explanation),
        message="差異分析の説明を生成しました",
    )


@router.post("/explain/period", response_model=AIExplanationResponse)
async def ai_explain_period(
    data: ExplainPeriodRequest, db: AsyncSession = Depends(get_db)
):
    """期間サマリーのAI分析を実行する。"""
    try:
        explanation = await explain_period_summary(db, data.period_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析エラー: {e}")
    return AIExplanationResponse(
        explanation=AIExplanationRead.model_validate(explanation),
        message="期間サマリー分析を生成しました",
    )


@router.post("/ask", response_model=AIExplanationResponse)
async def ai_ask_question(
    data: AskQuestionRequest, db: AsyncSession = Depends(get_db)
):
    """汎用Q&A — AIに質問する。"""
    try:
        explanation = await ask_question(
            db, data.question, data.context_type, data.context_id
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI応答エラー: {e}")
    return AIExplanationResponse(
        explanation=AIExplanationRead.model_validate(explanation),
        message="回答を生成しました",
    )


@router.get("/explanations", response_model=list[AIExplanationRead])
async def list_ai_explanations(
    context_type: str | None = None,
    review_status: ReviewStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    """AI説明の履歴一覧を取得する。"""
    query = select(AIExplanation)
    if context_type:
        query = query.where(AIExplanation.context_type == context_type)
    if review_status:
        query = query.where(AIExplanation.review_status == review_status)
    query = query.order_by(AIExplanation.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/explanations/{explanation_id}", response_model=AIExplanationRead)
async def get_ai_explanation(
    explanation_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """AI説明を取得する。"""
    result = await db.execute(
        select(AIExplanation).where(AIExplanation.id == explanation_id)
    )
    explanation = result.scalar_one_or_none()
    if not explanation:
        raise HTTPException(status_code=404, detail="AI説明が見つかりません")
    return explanation


@router.put("/explanations/{explanation_id}", response_model=AIExplanationRead)
async def update_ai_explanation(
    explanation_id: uuid.UUID,
    data: AIExplanationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """AI説明のレビューステータスを更新する。"""
    result = await db.execute(
        select(AIExplanation).where(AIExplanation.id == explanation_id)
    )
    explanation = result.scalar_one_or_none()
    if not explanation:
        raise HTTPException(status_code=404, detail="AI説明が見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(explanation, field, value)
    await db.flush()
    await db.refresh(explanation)
    return explanation
