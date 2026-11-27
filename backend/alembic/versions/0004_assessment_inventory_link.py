"""Link assessments to optional AI-system inventory context.

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("assessments", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("ai_system_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_assessments_ai_system_id", "ai_systems", ["ai_system_id"], ["id"]
            )
    else:
        op.add_column("assessments", sa.Column("ai_system_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_assessments_ai_system_id", "assessments", "ai_systems", ["ai_system_id"], ["id"]
        )
    op.create_index("ix_assessments_ai_system_id", "assessments", ["ai_system_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_assessments_ai_system_id", table_name="assessments")
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("assessments", recreate="always") as batch_op:
            batch_op.drop_constraint("fk_assessments_ai_system_id", type_="foreignkey")
            batch_op.drop_column("ai_system_id")
    else:
        op.drop_constraint("fk_assessments_ai_system_id", "assessments", type_="foreignkey")
        op.drop_column("assessments", "ai_system_id")
