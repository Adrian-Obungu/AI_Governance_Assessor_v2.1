from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.assessments.crud import get_assessment
from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User
from backend.evidence.crud import get_user_evidence_record
from backend.findings.crud import (
    create_finding,
    get_user_finding,
    get_user_findings,
    update_finding,
)
from backend.findings.schemas import (
    FindingCreate,
    FindingPriority,
    FindingResponse,
    FindingStatus,
    FindingUpdate,
)
from backend.inventory.crud import get_user_ai_system

router = APIRouter(prefix="/findings", tags=["findings"])


def validate_links(
    db: Session,
    user_id: int,
    ai_system_id: int,
    evidence_id: int,
    assessment_id: int | None,
):
    system = get_user_ai_system(db, ai_system_id, user_id)
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")
    evidence = get_user_evidence_record(db, evidence_id, user_id)
    if not evidence or evidence.ai_system_id != ai_system_id:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    if assessment_id is not None and not get_assessment(db, assessment_id, user_id):
        raise HTTPException(status_code=404, detail="Assessment not found")


@router.post("", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding_route(
    payload: FindingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_links(
        db,
        current_user.id,
        payload.ai_system_id,
        payload.evidence_id,
        payload.assessment_id,
    )
    return create_finding(db, current_user.id, **payload.model_dump())


@router.get("", response_model=list[FindingResponse])
async def list_findings(
    ai_system_id: int | None = Query(None, ge=1),
    status_filter: FindingStatus | None = Query(None, alias="status"),
    priority_filter: FindingPriority | None = Query(None, alias="priority"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_findings(
        db,
        current_user.id,
        ai_system_id,
        status_filter,
        priority_filter,
    )


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding_route(
    finding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding = get_user_finding(db, finding_id, current_user.id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.put("/{finding_id}", response_model=FindingResponse)
async def update_finding_route(
    finding_id: int,
    payload: FindingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding = get_user_finding(db, finding_id, current_user.id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    values = payload.model_dump(exclude_unset=True)
    validate_links(
        db,
        current_user.id,
        values.get("ai_system_id", finding.ai_system_id),
        values.get("evidence_id", finding.evidence_id),
        values.get("assessment_id", finding.assessment_id),
    )
    return update_finding(db, finding, **values)
