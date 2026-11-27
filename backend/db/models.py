from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.db.database import Base


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = relationship("Assessment", back_populates="user")
    failed_logins = relationship("FailedLogin", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")
    ai_systems = relationship(
        "AISystem", back_populates="user", cascade="all, delete-orphan"
    )
    evidence_records = relationship(
        "EvidenceRecord", back_populates="user", cascade="all, delete-orphan"
    )
    findings = relationship(
        "Finding", back_populates="user", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "ReviewRecord", back_populates="user", cascade="all, delete-orphan"
    )
    operational_signals = relationship(
        "OperationalSignal", back_populates="user", cascade="all, delete-orphan"
    )


class AISystem(Base):
    """A user-owned AI system or AI-enabled process in the governance inventory."""

    __tablename__ = "ai_systems"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    department = Column(String(120), nullable=True)
    business_owner = Column(String(255), nullable=True)
    provider = Column(String(255), nullable=True)
    lifecycle_stage = Column(String(32), nullable=False, default="discovery")
    geographies = Column(JSON, nullable=False, default=list)
    data_categories = Column(JSON, nullable=False, default=list)
    affected_groups = Column(JSON, nullable=False, default=list)
    review_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="ai_systems")
    evidence_records = relationship(
        "EvidenceRecord", back_populates="ai_system", cascade="all, delete-orphan"
    )
    findings = relationship(
        "Finding", back_populates="ai_system", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "ReviewRecord", back_populates="ai_system", cascade="all, delete-orphan"
    )
    operational_signals = relationship(
        "OperationalSignal", back_populates="ai_system", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint(
            "lifecycle_stage IN ('discovery', 'pilot', 'in_production', 'retired')",
            name="ck_ai_systems_lifecycle_stage",
        ),
        Index("ix_ai_systems_user_created_at", "user_id", "created_at"),
        Index("ix_ai_systems_user_review_date", "user_id", "review_date"),
    )


class FailedLogin(Base):
    """Track failed login attempts for account lockout"""

    __tablename__ = "failed_logins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="failed_logins")


class PasswordReset(Base):
    """Single-use password reset tokens"""

    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="password_resets")


class Assessment(Base):
    """AI Governance Assessment"""

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_system_id = Column(
        Integer, ForeignKey("ai_systems.id"), nullable=True, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    schema_version = Column(String(32), default="1.0", nullable=False)
    status = Column(
        String(20), default="draft", nullable=False
    )  # draft, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="assessments")
    ai_system = relationship("AISystem")
    results = relationship(
        "AssessmentResult", back_populates="assessment", cascade="all, delete-orphan"
    )
    evidence_records = relationship(
        "EvidenceRecord", back_populates="assessment", cascade="all, delete-orphan"
    )
    findings = relationship(
        "Finding", back_populates="assessment", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "ReviewRecord",
        back_populates="assessment",
        foreign_keys="ReviewRecord.assessment_id",
        cascade="all, delete-orphan",
    )
    reassessments = relationship(
        "ReviewRecord",
        back_populates="reassessment",
        foreign_keys="ReviewRecord.reassessment_id",
    )
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'in_progress', 'completed')",
            name="ck_assessments_status",
        ),
        CheckConstraint(
            "status <> 'completed' OR completed_at IS NOT NULL",
            name="ck_assessments_completed_at",
        ),
        Index("ix_assessments_user_created_at", "user_id", "created_at"),
        Index("ix_assessments_user_status", "user_id", "status"),
    )


class AssessmentResult(Base):
    """Versioned assessment results with scores"""

    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    category = Column(
        String(100), nullable=False
    )  # data_privacy, model_risk, ethics, compliance
    questions = Column(JSON, nullable=False)  # Store questions and answers
    questionnaire_version = Column(String(32), nullable=False, default="1.0")
    questionnaire_snapshot = Column(JSON, nullable=False, default=dict)
    scoring_version = Column(String(32), nullable=False, default="1.0")
    score = Column(Integer, nullable=False)  # 0-100
    maturity_level = Column(
        String(50), nullable=False
    )  # initial, developing, defined, managed, optimized
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("Assessment", back_populates="results")
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "category",
            name="uq_assessment_results_assessment_category",
        ),
        Index("ix_assessment_results_assessment_category", "assessment_id", "category"),
        CheckConstraint(
            "category IN ('data_privacy', 'model_risk', 'ethics', 'compliance')",
            name="ck_assessment_results_category",
        ),
    )


class EvidenceRecord(Base):
    """Metadata describing user-recorded supporting context for governance work."""

    __tablename__ = "evidence_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_type = Column(String(40), nullable=False)
    source_location = Column(String(1000), nullable=True)
    owner = Column(String(255), nullable=True)
    collected_on = Column(Date, nullable=True)
    review_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default="draft")
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="evidence_records")
    ai_system = relationship("AISystem", back_populates="evidence_records")
    assessment = relationship("Assessment", back_populates="evidence_records")
    findings = relationship(
        "Finding", back_populates="evidence", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint(
            "evidence_type IN ('policy', 'procedure', 'contract', 'technical_document', 'training_record', 'audit_record', 'review_note', 'other')",
            name="ck_evidence_records_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'reviewed', 'needs_update')",
            name="ck_evidence_records_status",
        ),
        Index("ix_evidence_records_user_review_date", "user_id", "review_date"),
        Index("ix_evidence_records_user_status", "user_id", "status"),
        Index("ix_evidence_records_system_status", "ai_system_id", "status"),
    )


class Finding(Base):
    """An owned governance finding with one accountable remediation action."""

    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=False)
    evidence_id = Column(Integer, ForeignKey("evidence_records.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    title = Column(String(255), nullable=False)
    conclusion = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    owner = Column(String(255), nullable=False)
    remediation_action = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(24), nullable=False, default="open")
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="findings")
    ai_system = relationship("AISystem", back_populates="findings")
    evidence = relationship("EvidenceRecord", back_populates="findings")
    assessment = relationship("Assessment", back_populates="findings")
    operational_signals = relationship(
        "OperationalSignal", back_populates="finding", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="ck_findings_priority",
        ),
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'accepted_risk')",
            name="ck_findings_status",
        ),
        Index("ix_findings_user_status", "user_id", "status"),
        Index("ix_findings_user_priority", "user_id", "priority"),
        Index("ix_findings_system_due_date", "ai_system_id", "due_date"),
    )


class ReviewRecord(Base):
    """A human review decision and optional reassessment link for an AI system."""

    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    reassessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    reviewer = Column(String(255), nullable=False)
    review_date = Column(Date, nullable=False)
    decision = Column(String(24), nullable=False)
    material_change = Column(Boolean, nullable=False, default=False)
    change_summary = Column(Text, nullable=True)
    next_review_date = Column(Date, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    ai_system = relationship("AISystem", back_populates="reviews")
    assessment = relationship(
        "Assessment", back_populates="reviews", foreign_keys=[assessment_id]
    )
    reassessment = relationship(
        "Assessment", back_populates="reassessments", foreign_keys=[reassessment_id]
    )
    operational_signals = relationship(
        "OperationalSignal", back_populates="review", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint(
            "decision IN ('continue', 'reassess', 'pause', 'retire')",
            name="ck_review_records_decision",
        ),
        Index("ix_review_records_system_date", "ai_system_id", "review_date"),
        Index("ix_review_records_user_decision", "user_id", "decision"),
        Index("ix_review_records_user_material_change", "user_id", "material_change"),
    )


class OperationalSignal(Base):
    """A user-recorded incident, feedback item, or material system change."""

    __tablename__ = "operational_signals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_system_id = Column(Integer, ForeignKey("ai_systems.id"), nullable=False)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=True)
    review_id = Column(Integer, ForeignKey("review_records.id"), nullable=True)
    signal_type = Column(String(24), nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    status = Column(String(24), nullable=False, default="new")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reported_by = Column(String(255), nullable=False)
    reported_on = Column(Date, nullable=False)
    owner = Column(String(255), nullable=True)
    response_action = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="operational_signals")
    ai_system = relationship("AISystem", back_populates="operational_signals")
    finding = relationship("Finding")
    review = relationship("ReviewRecord", back_populates="operational_signals")
    __table_args__ = (
        CheckConstraint(
            "signal_type IN ('incident', 'feedback', 'material_change')",
            name="ck_operational_signals_type",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_operational_signals_severity",
        ),
        CheckConstraint(
            "status IN ('new', 'triaged', 'investigating', 'closed')",
            name="ck_operational_signals_status",
        ),
        Index("ix_operational_signals_system_date", "ai_system_id", "reported_on"),
        Index("ix_operational_signals_user_status", "user_id", "status"),
        Index("ix_operational_signals_user_severity", "user_id", "severity"),
    )
