from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.db.models import Assessment, AssessmentResult
from backend.assessments.questionnaire import (
    calculate_category_score,
    get_maturity_level,
    get_recommendations,
    AssessmentCategory
)


def create_assessment(db: Session, user_id: int, title: str, description: Optional[str] = None) -> Assessment:
    """Create a new assessment"""
    assessment = Assessment(
        user_id=user_id,
        title=title,
        description=description,
        status="draft"
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db: Session, assessment_id: int, user_id: int) -> Optional[Assessment]:
    """Get an assessment by ID for a specific user"""
    return db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == user_id
    ).first()


def get_user_assessments(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Assessment]:
    """Get all assessments for a user"""
    return db.query(Assessment).filter(
        Assessment.user_id == user_id
    ).offset(skip).limit(limit).all()


def update_assessment(db: Session, assessment_id: int, user_id: int, **kwargs) -> Optional[Assessment]:
    """Update an assessment"""
    assessment = get_assessment(db, assessment_id, user_id)
    if not assessment:
        return None
    
    for key, value in kwargs.items():
        if value is not None and hasattr(assessment, key):
            setattr(assessment, key, value)
    
    db.commit()
    db.refresh(assessment)
    return assessment


def delete_assessment(db: Session, assessment_id: int, user_id: int) -> bool:
    """Delete an assessment"""
    assessment = get_assessment(db, assessment_id, user_id)
    if not assessment:
        return False
    
    db.delete(assessment)
    db.commit()
    return True


def submit_category_answers(
    db: Session,
    assessment_id: int,
    user_id: int,
    category: AssessmentCategory,
    answers: dict
) -> Optional[AssessmentResult]:
    """Submit answers for a category and calculate results"""
    assessment = get_assessment(db, assessment_id, user_id)
    if not assessment:
        return None
    
    # Calculate score and maturity
    score = calculate_category_score(answers, category)
    maturity = get_maturity_level(score)
    recommendations = get_recommendations(category, score, maturity)
    
    # Check if result already exists for this category
    existing_result = db.query(AssessmentResult).filter(
        AssessmentResult.assessment_id == assessment_id,
        AssessmentResult.category == category.value
    ).first()
    
    if existing_result:
        # Update existing result
        existing_result.questions = answers
        existing_result.score = score
        existing_result.maturity_level = maturity.value
        existing_result.recommendations = recommendations
        existing_result.created_at = datetime.utcnow()
        result = existing_result
    else:
        # Create new result
        result = AssessmentResult(
            assessment_id=assessment_id,
            category=category.value,
            questions=answers,
            score=score,
            maturity_level=maturity.value,
            recommendations=recommendations
        )
        db.add(result)
    
    # Update assessment status
    if assessment.status == "draft":
        assessment.status = "in_progress"
    
    # Check if all categories are completed
    results_count = db.query(AssessmentResult).filter(
        AssessmentResult.assessment_id == assessment_id
    ).count()
    
    if results_count >= 4:  # All 4 categories
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(result)
    return result


def get_assessment_summary(db: Session, assessment_id: int, user_id: int) -> Optional[dict]:
    """Get assessment summary with overall score"""
    assessment = get_assessment(db, assessment_id, user_id)
    if not assessment:
        return None
    
    results = db.query(AssessmentResult).filter(
        AssessmentResult.assessment_id == assessment_id
    ).all()
    
    if not results:
        return {
            "assessment": assessment,
            "overall_score": 0,
            "overall_maturity": "initial",
            "category_scores": {}
        }
    
    # Calculate overall score
    total_score = sum(r.score for r in results)
    overall_score = total_score // len(results)
    overall_maturity = get_maturity_level(overall_score)
    
    category_scores = {r.category: r.score for r in results}
    
    return {
        "assessment": assessment,
        "overall_score": overall_score,
        "overall_maturity": overall_maturity.value,
        "category_scores": category_scores
    }
