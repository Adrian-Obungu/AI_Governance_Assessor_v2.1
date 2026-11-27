from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.assessments.questionnaire import AssessmentCategory


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment"""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class AssessmentUpdate(BaseModel):
    """Schema for updating an assessment"""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: Literal["draft", "in_progress", "completed"] | None = None


class CategoryAnswers(BaseModel):
    """Answers for a specific category"""

    category: AssessmentCategory
    answers: dict[str, int] = Field(default_factory=dict)  # question_id -> answer_value


class AssessmentResultResponse(BaseModel):
    """Response schema for assessment result"""

    id: int
    assessment_id: int
    category: str
    score: int
    maturity_level: str
    recommendations: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    """Response schema for assessment"""

    id: int
    user_id: int
    title: str
    description: str | None
    schema_version: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    results: list[AssessmentResultResponse] = []

    class Config:
        from_attributes = True


class AssessmentSummary(BaseModel):
    """Summary of assessment with overall score"""

    assessment: AssessmentResponse
    overall_score: int
    overall_maturity: str
    category_scores: dict[str, int]


class QuestionnaireResponse(BaseModel):
    """Response schema for questionnaire template"""

    category: AssessmentCategory
    title: str
    description: str
    questions: list[dict]
