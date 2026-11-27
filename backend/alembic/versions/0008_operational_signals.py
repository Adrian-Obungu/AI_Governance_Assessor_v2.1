"""Add operational signal records.

Revision ID: 0008
Revises: 0007
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operational_signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ai_system_id", sa.Integer(), nullable=False),
        sa.Column("finding_id", sa.Integer(), nullable=True),
        sa.Column("review_id", sa.Integer(), nullable=True),
        sa.Column("signal_type", sa.String(length=24), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reported_by", sa.String(length=255), nullable=False),
        sa.Column("reported_on", sa.Date(), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("response_action", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "signal_type IN ('incident', 'feedback', 'material_change')",
            name="ck_operational_signals_type",
        ),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_operational_signals_severity",
        ),
        sa.CheckConstraint(
            "status IN ('new', 'triaged', 'investigating', 'closed')",
            name="ck_operational_signals_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"]),
        sa.ForeignKeyConstraint(["review_id"], ["review_records.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_operational_signals_id"), "operational_signals", ["id"], unique=False
    )
    op.create_index(
        "ix_operational_signals_system_date",
        "operational_signals",
        ["ai_system_id", "reported_on"],
        unique=False,
    )
    op.create_index(
        "ix_operational_signals_user_status",
        "operational_signals",
        ["user_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_operational_signals_user_severity",
        "operational_signals",
        ["user_id", "severity"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_operational_signals_user_severity", table_name="operational_signals"
    )
    op.drop_index(
        "ix_operational_signals_user_status", table_name="operational_signals"
    )
    op.drop_index(
        "ix_operational_signals_system_date", table_name="operational_signals"
    )
    op.drop_index(op.f("ix_operational_signals_id"), table_name="operational_signals")
    op.drop_table("operational_signals")
