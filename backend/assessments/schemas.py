from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from backend.assessments.questionnaire import AssessmentCategory, MaturityLevel


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class AssessmentUpdate(BaseModel):
    """Schema for updating an assessment"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class CategoryAnswers(BaseModel):
    """Answers for a specific category"""
    category: AssessmentCategory
    answers: Dict[str, int]  # question_id -> answer_value


class AssessmentResultResponse(BaseModel):
    """Response schema for assessment result"""
    id: int
    assessment_id: int
    category: str
    score: int
    maturity_level: str
    recommendations: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    """Response schema for assessment"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    schema_version: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    results: List[AssessmentResultResponse] = []
    
    class Config:
        from_attributes = True


class AssessmentSummary(BaseModel):
    """Summary of assessment with overall score"""
    assessment: AssessmentResponse
    overall_score: int
    overall_maturity: str
    category_scores: Dict[str, int]


class QuestionnaireResponse(BaseModel):
    """Response schema for questionnaire template"""
    category: AssessmentCategory
    title: str
    description: str
    questions: List[Dict]
