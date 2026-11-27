from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User
from backend.snapshot.crud import get_user_snapshots
from backend.snapshot.schemas import GovernanceSnapshot

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/snapshots", response_model=list[GovernanceSnapshot])
async def list_governance_snapshots(
    ai_system_id: int | None = Query(None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_snapshots(db, current_user.id, ai_system_id)
