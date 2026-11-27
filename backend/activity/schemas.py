from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ActivitySource = Literal[
    "inventory", "assessment", "evidence", "finding", "review", "signal"
]


class ActivityEvent(BaseModel):
    source_type: ActivitySource
    source_id: int
    ai_system_id: int
    occurred_at: datetime
    title: str
    summary: str
    status: str | None = None
    priority: str | None = None
    severity: str | None = None
