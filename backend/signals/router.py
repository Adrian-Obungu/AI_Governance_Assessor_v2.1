from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User
from backend.findings.crud import get_user_finding
from backend.inventory.crud import get_user_ai_system
from backend.reviews.crud import get_user_review
from backend.signals.crud import (
    create_signal,
    get_user_signal,
    get_user_signals,
    update_signal,
)
from backend.signals.schemas import (
    SignalCreate,
    SignalResponse,
    SignalSeverity,
    SignalStatus,
    SignalType,
    SignalUpdate,
)

router = APIRouter(prefix="/signals", tags=["signals"])


def validate_links(
    db: Session,
    user_id: int,
    ai_system_id: int,
    finding_id: int | None,
    review_id: int | None,
):
    if not get_user_ai_system(db, ai_system_id, user_id):
        raise HTTPException(status_code=404, detail="AI system not found")
    if finding_id is not None:
        finding = get_user_finding(db, finding_id, user_id)
        if not finding or finding.ai_system_id != ai_system_id:
            raise HTTPException(status_code=404, detail="Finding not found")
    if review_id is not None:
        review = get_user_review(db, review_id, user_id)
        if not review or review.ai_system_id != ai_system_id:
            raise HTTPException(status_code=404, detail="Review not found")


@router.post("", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def create_signal_route(
    payload: SignalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_links(
        db, current_user.id, payload.ai_system_id, payload.finding_id, payload.review_id
    )
    return create_signal(db, current_user.id, **payload.model_dump())


@router.get("", response_model=list[SignalResponse])
async def list_signals(
    ai_system_id: int | None = Query(None, ge=1),
    signal_type: SignalType | None = Query(None),
    severity: SignalSeverity | None = Query(None),
    status_filter: SignalStatus | None = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_signals(
        db, current_user.id, ai_system_id, signal_type, severity, status_filter
    )


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal_route(
    signal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    signal = get_user_signal(db, signal_id, current_user.id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.put("/{signal_id}", response_model=SignalResponse)
async def update_signal_route(
    signal_id: int,
    payload: SignalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    signal = get_user_signal(db, signal_id, current_user.id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    values = payload.model_dump(exclude_unset=True)
    validate_links(
        db,
        current_user.id,
        values.get("ai_system_id", signal.ai_system_id),
        values.get("finding_id", signal.finding_id),
        values.get("review_id", signal.review_id),
    )
    return update_signal(db, signal, **values)
