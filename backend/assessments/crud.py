from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.assessments.questionnaire import (
    AssessmentCategory,
    QUESTIONNAIRES,
    calculate_category_score,
    get_maturity_level,
    get_recommendations,
)
from backend.db.models import Assessment, AssessmentResult


def create_assessment(
    db: Session,
    user_id: int,
    title: str,
    description: str | None = None,
    ai_system_id: int | None = None,
) -> Assessment:
    """Create a new assessment"""
    assessment = Assessment(
        user_id=user_id,
        ai_system_id=ai_system_id,
        title=title,
        description=description,
        status="draft",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db: Session, assessment_id: int, user_id: int) -> Assessment | None:
    """Get an assessment by ID for a specific user"""
    return (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id, Assessment.user_id == user_id)
        .first()
    )


def get_user_assessments(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[Assessment]:
    """Get all assessments for a user"""
    return (
        db.query(Assessment)
        .filter(Assessment.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_assessment(
    db: Session, assessment_id: int, user_id: int, **kwargs
) -> Assessment | None:
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
    answers: dict,
) -> AssessmentResult | None:
    """Submit answers for a category and calculate results"""
    assessment = get_assessment(db, assessment_id, user_id)
    if not assessment:
        return None

    questionnaire = QUESTIONNAIRES[category]
    expected_questions = {question["id"]: question for question in questionnaire["questions"]}
    submitted_questions = set(answers)
    missing = sorted(set(expected_questions) - submitted_questions)
    unknown = sorted(submitted_questions - set(expected_questions))
    invalid_options = {
        question_id: value
        for question_id, value in answers.items()
        if question_id in expected_questions
        and value not in {option["value"] for option in expected_questions[question_id]["options"]}
    }
    if missing or unknown or invalid_options:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Answers must include exactly one valid option for every question.",
                "missing_questions": missing,
                "unknown_questions": unknown,
                "invalid_options": invalid_options,
            },
        )

    # Calculate score and maturity
    score = calculate_category_score(answers, category)
    maturity = get_maturity_level(score)
    recommendations = get_recommendations(category, score, maturity)

    # Check if result already exists for this category
    existing_result = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.category == category.value,
        )
        .first()
    )

    if existing_result:
        # Update existing result
        existing_result.questions = answers
        existing_result.questionnaire_version = "1.0"
        existing_result.questionnaire_snapshot = questionnaire
        existing_result.scoring_version = "1.0"
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
            questionnaire_version="1.0",
            questionnaire_snapshot=questionnaire,
            scoring_version="1.0",
            score=score,
            maturity_level=maturity.value,
            recommendations=recommendations,
        )
        db.add(result)

    # Update assessment status
    if assessment.status == "draft":
        assessment.status = "in_progress"

    # Flush the new or updated result before checking completion. The test and
    # production sessions may disable autoflush, so a count query can otherwise
    # miss the category submitted in this request.
    db.flush()

    # Check against the authoritative questionnaire categories rather than a
    # hard-coded count. Distinct categories also prevent duplicate submissions
    # from making an assessment appear complete.
    completed_categories = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.assessment_id == assessment_id)
        .with_entities(AssessmentResult.category)
        .distinct()
        .all()
    )

    if len(completed_categories) == len(QUESTIONNAIRES):
        assessment.status = "completed"
        if assessment.completed_at is None:
            assessment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(result)
    return result


def get_assessment_summary(
    db: Session, assessment_id: int, user_id: int
) -> dict | None:
    """Get assessment summary with overall score"""
    assessment = get_assessment(db, assessment_id, user_id)
    if not assessment:
        return None

    results = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.assessment_id == assessment_id)
        .all()
    )

    if not results:
        return {
            "assessment": assessment,
            "overall_score": 0,
            "overall_maturity": "initial",
            "category_scores": {},
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
        "category_scores": category_scores,
    }
