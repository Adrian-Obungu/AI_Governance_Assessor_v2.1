"""Add review and reassessment records.

Revision ID: 0007
Revises: 0006
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "review_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ai_system_id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=True),
        sa.Column("reassessment_id", sa.Integer(), nullable=True),
        sa.Column("reviewer", sa.String(length=255), nullable=False),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("decision", sa.String(length=24), nullable=False),
        sa.Column("material_change", sa.Boolean(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("next_review_date", sa.Date(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "decision IN ('continue', 'reassess', 'pause', 'retire')",
            name="ck_review_records_decision",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ai_system_id"], ["ai_systems.id"]),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["reassessment_id"], ["assessments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_review_records_id"), "review_records", ["id"], unique=False
    )
    op.create_index(
        "ix_review_records_system_date",
        "review_records",
        ["ai_system_id", "review_date"],
        unique=False,
    )
    op.create_index(
        "ix_review_records_user_decision",
        "review_records",
        ["user_id", "decision"],
        unique=False,
    )
    op.create_index(
        "ix_review_records_user_material_change",
        "review_records",
        ["user_id", "material_change"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_review_records_user_material_change", table_name="review_records")
    op.drop_index("ix_review_records_user_decision", table_name="review_records")
    op.drop_index("ix_review_records_system_date", table_name="review_records")
    op.drop_index(op.f("ix_review_records_id"), table_name="review_records")
    op.drop_table("review_records")
