from datetime import date
from typing import Literal

from pydantic import BaseModel

AttentionLevel = Literal["info", "attention"]


class AttentionItem(BaseModel):
    level: AttentionLevel
    title: str
    detail: str
    source_type: str
    source_id: int | None = None


class WorkflowCoverage(BaseModel):
    inventory: bool
    assessments: int
    evidence_records: int
    findings: int
    human_reviews: int
    operational_signals: int


class GovernanceSnapshot(BaseModel):
    ai_system_id: int
    system_name: str
    lifecycle_stage: str
    review_date: date | None
    review_due: bool
    coverage: WorkflowCoverage
    open_findings: int
    overdue_findings: int
    active_signals: int
    attention: list[AttentionItem]
    next_action: str
