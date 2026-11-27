from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.assessments.crud import get_assessment
from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User
from backend.inventory.crud import get_user_ai_system
from backend.reviews.crud import (
    create_review,
    get_user_review,
    get_user_reviews,
    update_review,
)
from backend.reviews.schemas import (
    ReviewCreate,
    ReviewDecision,
    ReviewResponse,
    ReviewUpdate,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


def validate_links(
    db: Session,
    user_id: int,
    ai_system_id: int,
    assessment_id: int | None,
    reassessment_id: int | None,
):
    if not get_user_ai_system(db, ai_system_id, user_id):
        raise HTTPException(status_code=404, detail="AI system not found")
    for linked_id, label in (
        (assessment_id, "Assessment"),
        (reassessment_id, "Reassessment"),
    ):
        if linked_id is not None:
            assessment = get_assessment(db, linked_id, user_id)
            if not assessment:
                raise HTTPException(status_code=404, detail=f"{label} not found")
            if assessment.ai_system_id != ai_system_id:
                raise HTTPException(status_code=404, detail=f"{label} context mismatch")


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review_route(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_links(
        db,
        current_user.id,
        payload.ai_system_id,
        payload.assessment_id,
        payload.reassessment_id,
    )
    return create_review(db, current_user.id, **payload.model_dump())


@router.get("", response_model=list[ReviewResponse])
async def list_reviews(
    ai_system_id: int | None = Query(None, ge=1),
    decision_filter: ReviewDecision | None = Query(None, alias="decision"),
    material_change: bool | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_reviews(
        db, current_user.id, ai_system_id, decision_filter, material_change
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review_route(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = get_user_review(db, review_id, current_user.id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review_route(
    review_id: int,
    payload: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = get_user_review(db, review_id, current_user.id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    values = payload.model_dump(exclude_unset=True)
    validate_links(
        db,
        current_user.id,
        values.get("ai_system_id", review.ai_system_id),
        values.get("assessment_id", review.assessment_id),
        values.get("reassessment_id", review.reassessment_id),
    )
    return update_review(db, review, **values)
