from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.activity.crud import get_user_activity
from backend.activity.schemas import ActivityEvent, ActivitySource
from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("", response_model=list[ActivityEvent])
async def list_activity(
    ai_system_id: int | None = Query(None, ge=1),
    source_type: ActivitySource | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_activity(db, current_user.id, ai_system_id, source_type)
