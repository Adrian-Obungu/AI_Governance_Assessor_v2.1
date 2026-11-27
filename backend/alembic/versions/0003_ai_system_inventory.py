"""Add the AI-system inventory table.

Revision ID: 0003
Revises: 0002
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_systems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("business_owner", sa.String(length=255), nullable=True),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("lifecycle_stage", sa.String(length=32), nullable=False),
        sa.Column("geographies", sa.JSON(), nullable=False),
        sa.Column("data_categories", sa.JSON(), nullable=False),
        sa.Column("affected_groups", sa.JSON(), nullable=False),
        sa.Column("review_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "lifecycle_stage IN ('discovery', 'pilot', 'in_production', 'retired')",
            name="ck_ai_systems_lifecycle_stage",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_systems_id"), "ai_systems", ["id"], unique=False)
    op.create_index("ix_ai_systems_user_created_at", "ai_systems", ["user_id", "created_at"], unique=False)
    op.create_index("ix_ai_systems_user_review_date", "ai_systems", ["user_id", "review_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_systems_user_review_date", table_name="ai_systems")
    op.drop_index("ix_ai_systems_user_created_at", table_name="ai_systems")
    op.drop_index(op.f("ix_ai_systems_id"), table_name="ai_systems")
    op.drop_table("ai_systems")
