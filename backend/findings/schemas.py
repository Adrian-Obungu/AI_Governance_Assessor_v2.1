from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

FindingPriority = Literal["low", "medium", "high", "critical"]
FindingStatus = Literal["open", "in_progress", "resolved", "accepted_risk"]


class FindingCreate(BaseModel):
    ai_system_id: int = Field(..., ge=1)
    evidence_id: int = Field(..., ge=1)
    assessment_id: int | None = Field(None, ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    conclusion: str = Field(..., min_length=1, max_length=4000)
    priority: FindingPriority = "medium"
    owner: str = Field(..., min_length=1, max_length=255)
    remediation_action: str = Field(..., min_length=1, max_length=4000)
    due_date: date | None = None
    status: FindingStatus = "open"
    reviewer_notes: str | None = Field(None, max_length=4000)


class FindingUpdate(BaseModel):
    ai_system_id: int | None = Field(None, ge=1)
    evidence_id: int | None = Field(None, ge=1)
    assessment_id: int | None = Field(None, ge=1)
    title: str | None = Field(None, min_length=1, max_length=255)
    conclusion: str | None = Field(None, min_length=1, max_length=4000)
    priority: FindingPriority | None = None
    owner: str | None = Field(None, min_length=1, max_length=255)
    remediation_action: str | None = Field(None, min_length=1, max_length=4000)
    due_date: date | None = None
    status: FindingStatus | None = None
    reviewer_notes: str | None = Field(None, max_length=4000)


class FindingResponse(BaseModel):
    id: int
    user_id: int
    ai_system_id: int
    evidence_id: int
    assessment_id: int | None
    title: str
    conclusion: str
    priority: FindingPriority
    owner: str
    remediation_action: str
    due_date: date | None
    status: FindingStatus
    reviewer_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
