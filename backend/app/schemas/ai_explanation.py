"""Pydantic v2 schemas for AI explanation (Phase 5)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.audit import ReviewStatus


class AIExplanationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    context_type: str
    context_id: str | None = None
    prompt: str
    response: str
    model: str
    input_tokens: int
    output_tokens: int
    review_status: ReviewStatus
    reviewer_notes: str | None = None
    created_at: datetime
    updated_at: datetime


class AIExplanationUpdate(BaseModel):
    review_status: ReviewStatus | None = None
    reviewer_notes: str | None = None


class ExplainVarianceRequest(BaseModel):
    variance_record_id: uuid.UUID


class ExplainPeriodRequest(BaseModel):
    period_id: uuid.UUID


class AskQuestionRequest(BaseModel):
    question: str
    context_type: str | None = None
    context_id: uuid.UUID | None = None


class AIExplanationResponse(BaseModel):
    explanation: AIExplanationRead
    message: str
