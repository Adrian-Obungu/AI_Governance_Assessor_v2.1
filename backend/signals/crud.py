from sqlalchemy.orm import Session

from backend.db.models import OperationalSignal


def create_signal(db: Session, user_id: int, **values) -> OperationalSignal:
    signal = OperationalSignal(user_id=user_id, **values)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def get_user_signals(
    db: Session,
    user_id: int,
    ai_system_id: int | None = None,
    signal_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
) -> list[OperationalSignal]:
    query = db.query(OperationalSignal).filter(OperationalSignal.user_id == user_id)
    if ai_system_id is not None:
        query = query.filter(OperationalSignal.ai_system_id == ai_system_id)
    if signal_type is not None:
        query = query.filter(OperationalSignal.signal_type == signal_type)
    if severity is not None:
        query = query.filter(OperationalSignal.severity == severity)
    if status is not None:
        query = query.filter(OperationalSignal.status == status)
    return query.order_by(
        OperationalSignal.reported_on.desc(), OperationalSignal.id.desc()
    ).all()


def get_user_signal(
    db: Session, signal_id: int, user_id: int
) -> OperationalSignal | None:
    return (
        db.query(OperationalSignal)
        .filter(OperationalSignal.id == signal_id, OperationalSignal.user_id == user_id)
        .first()
    )


def update_signal(
    db: Session, signal: OperationalSignal, **values
) -> OperationalSignal:
    for key, value in values.items():
        setattr(signal, key, value)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal
