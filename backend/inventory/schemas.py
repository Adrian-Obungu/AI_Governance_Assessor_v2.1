from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

LifecycleStage = Literal["discovery", "pilot", "in_production", "retired"]


class AISystemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    purpose: str = Field(..., min_length=1, max_length=4000)
    department: str | None = Field(None, max_length=120)
    business_owner: str | None = Field(None, max_length=255)
    provider: str | None = Field(None, max_length=255)
    lifecycle_stage: LifecycleStage = "discovery"
    geographies: list[str] = Field(default_factory=list, max_length=20)
    data_categories: list[str] = Field(default_factory=list, max_length=20)
    affected_groups: list[str] = Field(default_factory=list, max_length=20)
    review_date: date | None = None


class AISystemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    purpose: str | None = Field(None, min_length=1, max_length=4000)
    department: str | None = Field(None, max_length=120)
    business_owner: str | None = Field(None, max_length=255)
    provider: str | None = Field(None, max_length=255)
    lifecycle_stage: LifecycleStage | None = None
    geographies: list[str] | None = Field(None, max_length=20)
    data_categories: list[str] | None = Field(None, max_length=20)
    affected_groups: list[str] | None = Field(None, max_length=20)
    review_date: date | None = None


class AISystemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    purpose: str
    department: str | None
    business_owner: str | None
    provider: str | None
    lifecycle_stage: LifecycleStage
    geographies: list[str]
    data_categories: list[str]
    affected_groups: list[str]
    review_date: date | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
