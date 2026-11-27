from datetime import date

from sqlalchemy.orm import Session

from backend.db.models import (
    AISystem,
    Assessment,
    EvidenceRecord,
    Finding,
    OperationalSignal,
    ReviewRecord,
)


def get_user_snapshots(
    db: Session, user_id: int, ai_system_id: int | None = None
) -> list[dict]:
    query = db.query(AISystem).filter(AISystem.user_id == user_id)
    if ai_system_id is not None:
        query = query.filter(AISystem.id == ai_system_id)
    systems = query.order_by(AISystem.name.asc(), AISystem.id.asc()).all()
    today = date.today()
    snapshots = []

    for system in systems:
        assessments = (
            db.query(Assessment)
            .filter(Assessment.user_id == user_id, Assessment.ai_system_id == system.id)
            .all()
        )
        evidence = (
            db.query(EvidenceRecord)
            .filter(
                EvidenceRecord.user_id == user_id,
                EvidenceRecord.ai_system_id == system.id,
            )
            .all()
        )
        findings = (
            db.query(Finding)
            .filter(Finding.user_id == user_id, Finding.ai_system_id == system.id)
            .all()
        )
        reviews = (
            db.query(ReviewRecord)
            .filter(
                ReviewRecord.user_id == user_id,
                ReviewRecord.ai_system_id == system.id,
            )
            .all()
        )
        signals = (
            db.query(OperationalSignal)
            .filter(
                OperationalSignal.user_id == user_id,
                OperationalSignal.ai_system_id == system.id,
            )
            .all()
        )

        open_findings = [
            item for item in findings if item.status in {"open", "in_progress"}
        ]
        overdue_findings = [
            item
            for item in open_findings
            if item.due_date is not None and item.due_date < today
        ]
        active_signals = [item for item in signals if item.status != "closed"]
        review_due = system.review_date is not None and system.review_date <= today
        attention: list[dict] = []

        if not assessments:
            attention.append(
                {
                    "level": "attention",
                    "title": "No linked assessment yet",
                    "detail": "Start or link an assessment for this AI system.",
                    "source_type": "assessment",
                }
            )
        if not evidence:
            attention.append(
                {
                    "level": "attention",
                    "title": "No evidence records yet",
                    "detail": "Record the supporting policies, procedures, or review notes.",
                    "source_type": "evidence",
                }
            )
        if overdue_findings:
            attention.append(
                {
                    "level": "attention",
                    "title": f"{len(overdue_findings)} overdue remediation action(s)",
                    "detail": "Review the owner, due date, and current status of overdue findings.",
                    "source_type": "finding",
                    "source_id": overdue_findings[0].id,
                }
            )
        elif open_findings:
            attention.append(
                {
                    "level": "attention",
                    "title": f"{len(open_findings)} open finding(s)",
                    "detail": "Review the assigned remediation actions and their due dates.",
                    "source_type": "finding",
                    "source_id": open_findings[0].id,
                }
            )
        if active_signals:
            attention.append(
                {
                    "level": "attention",
                    "title": f"{len(active_signals)} active operational signal(s)",
                    "detail": "Triage the recorded incident, feedback, or material change with a human reviewer.",
                    "source_type": "signal",
                    "source_id": active_signals[0].id,
                }
            )
        if review_due:
            attention.append(
                {
                    "level": "attention",
                    "title": "Review date reached",
                    "detail": "Record a human review and decide whether reassessment is needed.",
                    "source_type": "inventory",
                    "source_id": system.id,
                }
            )
        if not attention:
            attention.append(
                {
                    "level": "info",
                    "title": "No immediate workflow prompts",
                    "detail": "Continue monitoring the system and keep its governance records current.",
                    "source_type": "inventory",
                    "source_id": system.id,
                }
            )

        next_action = attention[0]["detail"]
        snapshots.append(
            {
                "ai_system_id": system.id,
                "system_name": system.name,
                "lifecycle_stage": system.lifecycle_stage,
                "review_date": system.review_date,
                "review_due": review_due,
                "coverage": {
                    "inventory": True,
                    "assessments": len(assessments),
                    "evidence_records": len(evidence),
                    "findings": len(findings),
                    "human_reviews": len(reviews),
                    "operational_signals": len(signals),
                },
                "open_findings": len(open_findings),
                "overdue_findings": len(overdue_findings),
                "active_signals": len(active_signals),
                "attention": attention,
                "next_action": next_action,
            }
        )
    return snapshots
