from sqlalchemy.orm import Session

from backend.db.models import ReviewRecord


def create_review(db: Session, user_id: int, **values) -> ReviewRecord:
    review = ReviewRecord(user_id=user_id, **values)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_user_reviews(
    db: Session,
    user_id: int,
    ai_system_id: int | None = None,
    decision: str | None = None,
    material_change: bool | None = None,
) -> list[ReviewRecord]:
    query = db.query(ReviewRecord).filter(ReviewRecord.user_id == user_id)
    if ai_system_id is not None:
        query = query.filter(ReviewRecord.ai_system_id == ai_system_id)
    if decision is not None:
        query = query.filter(ReviewRecord.decision == decision)
    if material_change is not None:
        query = query.filter(ReviewRecord.material_change == material_change)
    return query.order_by(ReviewRecord.review_date.desc(), ReviewRecord.id.desc()).all()


def get_user_review(db: Session, review_id: int, user_id: int) -> ReviewRecord | None:
    return (
        db.query(ReviewRecord)
        .filter(ReviewRecord.id == review_id, ReviewRecord.user_id == user_id)
        .first()
    )


def update_review(db: Session, review: ReviewRecord, **values) -> ReviewRecord:
    for key, value in values.items():
        setattr(review, key, value)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
