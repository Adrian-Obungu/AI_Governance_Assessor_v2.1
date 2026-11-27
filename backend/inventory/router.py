from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.db.models import User
from backend.inventory.crud import (
    create_ai_system,
    get_user_ai_system,
    get_user_ai_systems,
    update_ai_system,
)
from backend.inventory.schemas import AISystemCreate, AISystemResponse, AISystemUpdate

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", response_model=AISystemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_system(
    payload: AISystemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_ai_system(db, current_user.id, **payload.model_dump())


@router.get("", response_model=list[AISystemResponse])
async def list_inventory_systems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_ai_systems(db, current_user.id)


@router.get("/{system_id}", response_model=AISystemResponse)
async def get_inventory_system(
    system_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    system = get_user_ai_system(db, system_id, current_user.id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI system not found"
        )
    return system


@router.put("/{system_id}", response_model=AISystemResponse)
async def update_inventory_system(
    system_id: int,
    payload: AISystemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    system = get_user_ai_system(db, system_id, current_user.id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI system not found"
        )
    return update_ai_system(db, system, **payload.model_dump(exclude_unset=True))
