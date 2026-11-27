from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

ReviewDecision = Literal["continue", "reassess", "pause", "retire"]


class ReviewCreate(BaseModel):
    ai_system_id: int = Field(..., ge=1)
    assessment_id: int | None = Field(None, ge=1)
    reassessment_id: int | None = Field(None, ge=1)
    reviewer: str = Field(..., min_length=1, max_length=255)
    review_date: date
    decision: ReviewDecision
    material_change: bool = False
    change_summary: str | None = Field(None, max_length=4000)
    next_review_date: date | None = None
    reviewer_notes: str | None = Field(None, max_length=4000)


class ReviewUpdate(BaseModel):
    ai_system_id: int | None = Field(None, ge=1)
    assessment_id: int | None = Field(None, ge=1)
    reassessment_id: int | None = Field(None, ge=1)
    reviewer: str | None = Field(None, min_length=1, max_length=255)
    review_date: date | None = None
    decision: ReviewDecision | None = None
    material_change: bool | None = None
    change_summary: str | None = Field(None, max_length=4000)
    next_review_date: date | None = None
    reviewer_notes: str | None = Field(None, max_length=4000)


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    ai_system_id: int
    assessment_id: int | None
    reassessment_id: int | None
    reviewer: str
    review_date: date
    decision: ReviewDecision
    material_change: bool
    change_summary: str | None
    next_review_date: date | None
    reviewer_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
