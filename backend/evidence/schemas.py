from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

EvidenceType = Literal[
    "policy",
    "procedure",
    "contract",
    "technical_document",
    "training_record",
    "audit_record",
    "review_note",
    "other",
]
EvidenceStatus = Literal["draft", "submitted", "reviewed", "needs_update"]


class EvidenceCreate(BaseModel):
    ai_system_id: int = Field(..., ge=1)
    assessment_id: int | None = Field(None, ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=4000)
    evidence_type: EvidenceType
    source_location: str | None = Field(None, max_length=1000)
    owner: str | None = Field(None, max_length=255)
    collected_on: date | None = None
    review_date: date | None = None
    status: EvidenceStatus = "draft"
    reviewer_notes: str | None = Field(None, max_length=4000)


class EvidenceUpdate(BaseModel):
    ai_system_id: int | None = Field(None, ge=1)
    assessment_id: int | None = Field(None, ge=1)
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=4000)
    evidence_type: EvidenceType | None = None
    source_location: str | None = Field(None, max_length=1000)
    owner: str | None = Field(None, max_length=255)
    collected_on: date | None = None
    review_date: date | None = None
    status: EvidenceStatus | None = None
    reviewer_notes: str | None = Field(None, max_length=4000)


class EvidenceResponse(BaseModel):
    id: int
    user_id: int
    ai_system_id: int
    assessment_id: int | None
    title: str
    description: str
    evidence_type: EvidenceType
    source_location: str | None
    owner: str | None
    collected_on: date | None
    review_date: date | None
    status: EvidenceStatus
    reviewer_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
