"""Add metadata-only evidence records.

Revision ID: 0005
Revises: 0004
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ai_system_id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_type", sa.String(length=40), nullable=False),
        sa.Column("source_location", sa.String(length=1000), nullable=True),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("collected_on", sa.Date(), nullable=True),
        sa.Column("review_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "evidence_type IN ('policy', 'procedure', 'contract', 'technical_document', 'training_record', 'audit_record', 'review_note', 'other')",
            name="ck_evidence_records_type",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'submitted', 'reviewed', 'needs_update')",
            name="ck_evidence_records_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_evidence_records_id"), "evidence_records", ["id"], unique=False
    )
    op.create_index(
        "ix_evidence_records_user_review_date",
        "evidence_records",
        ["user_id", "review_date"],
        unique=False,
    )
    op.create_index(
        "ix_evidence_records_user_status",
        "evidence_records",
        ["user_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_evidence_records_system_status",
        "evidence_records",
        ["ai_system_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_evidence_records_system_status", table_name="evidence_records")
    op.drop_index("ix_evidence_records_user_status", table_name="evidence_records")
    op.drop_index("ix_evidence_records_user_review_date", table_name="evidence_records")
    op.drop_index(op.f("ix_evidence_records_id"), table_name="evidence_records")
    op.drop_table("evidence_records")
