"""Add findings and remediation metadata.

Revision ID: 0006
Revises: 0005
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ai_system_id", sa.Integer(), nullable=False),
        sa.Column("evidence_id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("conclusion", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("remediation_action", sa.Text(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="ck_findings_priority",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'accepted_risk')",
            name="ck_findings_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence_records.id"]),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_findings_id"), "findings", ["id"], unique=False)
    op.create_index(
        "ix_findings_user_status", "findings", ["user_id", "status"], unique=False
    )
    op.create_index(
        "ix_findings_user_priority", "findings", ["user_id", "priority"], unique=False
    )
    op.create_index(
        "ix_findings_system_due_date",
        "findings",
        ["ai_system_id", "due_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_findings_system_due_date", table_name="findings")
    op.drop_index("ix_findings_user_priority", table_name="findings")
    op.drop_index("ix_findings_user_status", table_name="findings")
    op.drop_index(op.f("ix_findings_id"), table_name="findings")
    op.drop_table("findings")
