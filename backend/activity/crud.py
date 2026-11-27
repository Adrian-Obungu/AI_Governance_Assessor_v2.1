from datetime import date, datetime, time

from sqlalchemy.orm import Session

from backend.db.models import (
    AISystem,
    Assessment,
    EvidenceRecord,
    Finding,
    OperationalSignal,
    ReviewRecord,
)


def as_datetime(value: datetime | date | None) -> datetime:
    if value is None:
        return datetime.min
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def get_user_activity(
    db: Session,
    user_id: int,
    ai_system_id: int | None = None,
    source_type: str | None = None,
) -> list[dict]:
    systems_query = db.query(AISystem).filter(AISystem.user_id == user_id)
    if ai_system_id is not None:
        systems_query = systems_query.filter(AISystem.id == ai_system_id)
    systems = systems_query.all()
    system_ids = {system.id for system in systems}
    events: list[dict] = []

    def include(kind: str) -> bool:
        return source_type is None or source_type == kind

    if include("inventory"):
        events.extend(
            {
                "source_type": "inventory",
                "source_id": system.id,
                "ai_system_id": system.id,
                "occurred_at": as_datetime(system.updated_at or system.created_at),
                "title": f"AI system recorded: {system.name}",
                "summary": system.purpose,
                "status": system.lifecycle_stage,
            }
            for system in systems
        )

    if not system_ids:
        return sorted(events, key=lambda event: event["occurred_at"], reverse=True)

    if include("assessment"):
        assessments = (
            db.query(Assessment)
            .filter(
                Assessment.user_id == user_id, Assessment.ai_system_id.in_(system_ids)
            )
            .all()
        )
        events.extend(
            {
                "source_type": "assessment",
                "source_id": item.id,
                "ai_system_id": item.ai_system_id,
                "occurred_at": as_datetime(item.updated_at or item.created_at),
                "title": f"Assessment: {item.title}",
                "summary": item.description or "Assessment work was recorded.",
                "status": item.status,
            }
            for item in assessments
        )

    if include("evidence"):
        records = (
            db.query(EvidenceRecord)
            .filter(
                EvidenceRecord.user_id == user_id,
                EvidenceRecord.ai_system_id.in_(system_ids),
            )
            .all()
        )
        events.extend(
            {
                "source_type": "evidence",
                "source_id": item.id,
                "ai_system_id": item.ai_system_id,
                "occurred_at": as_datetime(item.updated_at or item.created_at),
                "title": f"Evidence record: {item.title}",
                "summary": item.description,
                "status": item.status,
            }
            for item in records
        )

    if include("finding"):
        findings = (
            db.query(Finding)
            .filter(Finding.user_id == user_id, Finding.ai_system_id.in_(system_ids))
            .all()
        )
        events.extend(
            {
                "source_type": "finding",
                "source_id": item.id,
                "ai_system_id": item.ai_system_id,
                "occurred_at": as_datetime(item.updated_at or item.created_at),
                "title": f"Finding: {item.title}",
                "summary": item.conclusion,
                "status": item.status,
                "priority": item.priority,
            }
            for item in findings
        )

    if include("review"):
        reviews = (
            db.query(ReviewRecord)
            .filter(
                ReviewRecord.user_id == user_id,
                ReviewRecord.ai_system_id.in_(system_ids),
            )
            .all()
        )
        events.extend(
            {
                "source_type": "review",
                "source_id": item.id,
                "ai_system_id": item.ai_system_id,
                "occurred_at": as_datetime(item.review_date),
                "title": f"Human review: {item.decision}",
                "summary": item.change_summary
                or "A human review decision was recorded.",
                "status": item.decision,
            }
            for item in reviews
        )

    if include("signal"):
        signals = (
            db.query(OperationalSignal)
            .filter(
                OperationalSignal.user_id == user_id,
                OperationalSignal.ai_system_id.in_(system_ids),
            )
            .all()
        )
        events.extend(
            {
                "source_type": "signal",
                "source_id": item.id,
                "ai_system_id": item.ai_system_id,
                "occurred_at": as_datetime(item.reported_on),
                "title": f"Operational signal: {item.title}",
                "summary": item.description,
                "status": item.status,
                "severity": item.severity,
            }
            for item in signals
        )

    return sorted(
        events,
        key=lambda event: (event["occurred_at"], event["source_id"]),
        reverse=True,
    )
