from sqlalchemy.orm import Session

from backend.db.models import Finding


def create_finding(db: Session, user_id: int, **values) -> Finding:
    finding = Finding(user_id=user_id, **values)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


def get_user_findings(
    db: Session,
    user_id: int,
    ai_system_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> list[Finding]:
    query = db.query(Finding).filter(Finding.user_id == user_id)
    if ai_system_id is not None:
        query = query.filter(Finding.ai_system_id == ai_system_id)
    if status is not None:
        query = query.filter(Finding.status == status)
    if priority is not None:
        query = query.filter(Finding.priority == priority)
    return query.order_by(Finding.updated_at.desc(), Finding.id.desc()).all()


def get_user_finding(db: Session, finding_id: int, user_id: int) -> Finding | None:
    return (
        db.query(Finding)
        .filter(Finding.id == finding_id, Finding.user_id == user_id)
        .first()
    )


def update_finding(db: Session, finding: Finding, **values) -> Finding:
    for key, value in values.items():
        setattr(finding, key, value)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding
