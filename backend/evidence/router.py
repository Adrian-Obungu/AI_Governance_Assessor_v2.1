from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.assessments.crud import get_assessment
from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User
from backend.evidence.crud import (
    create_evidence_record,
    get_user_evidence_record,
    get_user_evidence_records,
    update_evidence_record,
)
from backend.evidence.schemas import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceStatus,
    EvidenceUpdate,
)
from backend.inventory.crud import get_user_ai_system

router = APIRouter(prefix="/evidence", tags=["evidence"])


def validate_links(
    db: Session, user_id: int, ai_system_id: int, assessment_id: int | None
):
    if not get_user_ai_system(db, ai_system_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI system not found"
        )
    if assessment_id is not None and not get_assessment(db, assessment_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found"
        )


@router.post("", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    payload: EvidenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_links(db, current_user.id, payload.ai_system_id, payload.assessment_id)
    return create_evidence_record(db, current_user.id, **payload.model_dump())


@router.get("", response_model=list[EvidenceResponse])
async def list_evidence(
    ai_system_id: int | None = Query(None, ge=1),
    status_filter: EvidenceStatus | None = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_evidence_records(db, current_user.id, ai_system_id, status_filter)


@router.get("/{record_id}", response_model=EvidenceResponse)
async def get_evidence(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = get_user_evidence_record(db, record_id, current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence record not found"
        )
    return record


@router.put("/{record_id}", response_model=EvidenceResponse)
async def update_evidence(
    record_id: int,
    payload: EvidenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = get_user_evidence_record(db, record_id, current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evidence record not found"
        )
    values = payload.model_dump(exclude_unset=True)
    validate_links(
        db,
        current_user.id,
        values.get("ai_system_id", record.ai_system_id),
        values.get("assessment_id", record.assessment_id),
    )
    return update_evidence_record(db, record, **values)
