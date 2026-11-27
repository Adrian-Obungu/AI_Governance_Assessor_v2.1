from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

SignalType = Literal["incident", "feedback", "material_change"]
SignalSeverity = Literal["low", "medium", "high", "critical"]
SignalStatus = Literal["new", "triaged", "investigating", "closed"]


class SignalCreate(BaseModel):
    ai_system_id: int = Field(..., ge=1)
    finding_id: int | None = Field(None, ge=1)
    review_id: int | None = Field(None, ge=1)
    signal_type: SignalType
    severity: SignalSeverity = "medium"
    status: SignalStatus = "new"
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=4000)
    reported_by: str = Field(..., min_length=1, max_length=255)
    reported_on: date
    owner: str | None = Field(None, max_length=255)
    response_action: str | None = Field(None, max_length=4000)
    reviewer_notes: str | None = Field(None, max_length=4000)


class SignalUpdate(BaseModel):
    ai_system_id: int | None = Field(None, ge=1)
    finding_id: int | None = Field(None, ge=1)
    review_id: int | None = Field(None, ge=1)
    signal_type: SignalType | None = None
    severity: SignalSeverity | None = None
    status: SignalStatus | None = None
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=4000)
    reported_by: str | None = Field(None, min_length=1, max_length=255)
    reported_on: date | None = None
    owner: str | None = Field(None, max_length=255)
    response_action: str | None = Field(None, max_length=4000)
    reviewer_notes: str | None = Field(None, max_length=4000)


class SignalResponse(BaseModel):
    id: int
    user_id: int
    ai_system_id: int
    finding_id: int | None
    review_id: int | None
    signal_type: SignalType
    severity: SignalSeverity
    status: SignalStatus
    title: str
    description: str
    reported_by: str
    reported_on: date
    owner: str | None
    response_action: str | None
    reviewer_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
