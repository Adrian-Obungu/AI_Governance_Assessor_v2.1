from sqlalchemy.orm import Session

from backend.db.models import EvidenceRecord


def create_evidence_record(db: Session, user_id: int, **values) -> EvidenceRecord:
    record = EvidenceRecord(user_id=user_id, **values)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_user_evidence_records(
    db: Session,
    user_id: int,
    ai_system_id: int | None = None,
    status: str | None = None,
) -> list[EvidenceRecord]:
    query = db.query(EvidenceRecord).filter(EvidenceRecord.user_id == user_id)
    if ai_system_id is not None:
        query = query.filter(EvidenceRecord.ai_system_id == ai_system_id)
    if status is not None:
        query = query.filter(EvidenceRecord.status == status)
    return query.order_by(
        EvidenceRecord.updated_at.desc(), EvidenceRecord.id.desc()
    ).all()


def get_user_evidence_record(
    db: Session, record_id: int, user_id: int
) -> EvidenceRecord | None:
    return (
        db.query(EvidenceRecord)
        .filter(EvidenceRecord.id == record_id, EvidenceRecord.user_id == user_id)
        .first()
    )


def update_evidence_record(
    db: Session, record: EvidenceRecord, **values
) -> EvidenceRecord:
    for key, value in values.items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
