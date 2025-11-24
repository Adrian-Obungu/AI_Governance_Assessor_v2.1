from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from backend.db.models import User
from backend.auth.dependencies import get_current_user
from backend.assessments.schemas import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    CategoryAnswers,
    AssessmentResultResponse,
    AssessmentSummary,
    QuestionnaireResponse
)
from backend.assessments.crud import (
    create_assessment,
    get_assessment,
    get_user_assessments,
    update_assessment,
    delete_assessment,
    submit_category_answers,
    get_assessment_summary
)
from backend.assessments.questionnaire import QUESTIONNAIRES, AssessmentCategory
from backend.assessments.reports import generate_csv_report, generate_pdf_report

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("/questionnaires", response_model=List[QuestionnaireResponse])
async def get_questionnaires():
    """Get all questionnaire templates"""
    return [
        {
            "category": category,
            "title": data["title"],
            "description": data["description"],
            "questions": data["questions"]
        }
        for category, data in QUESTIONNAIRES.items()
    ]


@router.get("/questionnaires/{category}", response_model=QuestionnaireResponse)
async def get_questionnaire(category: AssessmentCategory):
    """Get questionnaire template for a specific category"""
    data = QUESTIONNAIRES[category]
    return {
        "category": category,
        "title": data["title"],
        "description": data["description"],
        "questions": data["questions"]
    }


@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_assessment(
    assessment: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new assessment"""
    db_assessment = create_assessment(db, current_user.id, assessment.title, assessment.description)
    return db_assessment


@router.get("", response_model=List[AssessmentResponse])
async def list_assessments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all assessments for the current user"""
    assessments = get_user_assessments(db, current_user.id, skip, limit)
    return assessments


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment_detail(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assessment details"""
    assessment = get_assessment(db, assessment_id, current_user.id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


@router.put("/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment_detail(
    assessment_id: int,
    assessment_update: AssessmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update assessment details"""
    updated = update_assessment(
        db,
        assessment_id,
        current_user.id,
        **assessment_update.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return updated


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment_detail(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an assessment"""
    success = delete_assessment(db, assessment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{assessment_id}/answers", response_model=AssessmentResultResponse)
async def submit_answers(
    assessment_id: int,
    category_answers: CategoryAnswers,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answers for a category"""
    result = submit_category_answers(
        db,
        assessment_id,
        current_user.id,
        category_answers.category,
        category_answers.answers
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return result


@router.get("/{assessment_id}/summary", response_model=AssessmentSummary)
async def get_summary(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assessment summary with overall score"""
    summary = get_assessment_summary(db, assessment_id, current_user.id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return summary


@router.get("/{assessment_id}/export/csv")
async def export_csv(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export assessment as CSV"""
    assessment = get_assessment(db, assessment_id, current_user.id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    
    csv_content = generate_csv_report(assessment, assessment.results)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=assessment_{assessment_id}.csv"}
    )


@router.get("/{assessment_id}/export/pdf")
async def export_pdf(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export assessment as PDF"""
    assessment = get_assessment(db, assessment_id, current_user.id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    
    pdf_content = generate_pdf_report(assessment, assessment.results)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=assessment_{assessment_id}.pdf"}
    )
