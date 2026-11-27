from sqlalchemy.orm import Session

from backend.db.models import AISystem


def create_ai_system(db: Session, user_id: int, **values) -> AISystem:
    system = AISystem(user_id=user_id, **values)
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


def get_user_ai_systems(db: Session, user_id: int) -> list[AISystem]:
    return (
        db.query(AISystem)
        .filter(AISystem.user_id == user_id)
        .order_by(AISystem.updated_at.desc(), AISystem.id.desc())
        .all()
    )


def get_user_ai_system(db: Session, system_id: int, user_id: int) -> AISystem | None:
    return (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.user_id == user_id)
        .first()
    )


def update_ai_system(db: Session, system: AISystem, **values) -> AISystem:
    for key, value in values.items():
        setattr(system, key, value)
    db.add(system)
    db.commit()
    db.refresh(system)
    return system
