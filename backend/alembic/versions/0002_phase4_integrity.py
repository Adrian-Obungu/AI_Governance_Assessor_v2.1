"""Add Phase 4 assessment integrity and historical result metadata.

Revision ID: 0002
Revises: 0001
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from alembic import context

from backend.assessments.questionnaire import QUESTIONNAIRES

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

QUESTIONNAIRE_VERSION = "1.0"
SCORING_VERSION = "1.0"
VALID_CATEGORIES = tuple(category.value for category in QUESTIONNAIRES)


def _is_sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def _deduplicate_results() -> None:
    """Keep the newest row for each assessment/category before adding UNIQUE."""
    bind = op.get_bind()
    bind.execute(
        text(
            """
            DELETE FROM assessment_results
            WHERE id IN (
                SELECT older.id
                FROM assessment_results AS older
                JOIN assessment_results AS newer
                  ON newer.assessment_id = older.assessment_id
                 AND newer.category = older.category
                 AND (
                      newer.created_at > older.created_at
                      OR (newer.created_at = older.created_at AND newer.id > older.id)
                 )
            )
            """
        )
    )


def _backfill_result_metadata() -> None:
    bind = op.get_bind()
    rows = bind.execute(
        text("SELECT id, category FROM assessment_results")
    ).mappings()
    for row in rows:
        category = row["category"]
        questionnaire = QUESTIONNAIRES.get(category)
        if questionnaire is None:
            raise RuntimeError(
                f"Cannot backfill assessment_results.id={row['id']}: "
                f"unknown category {category!r}"
            )
        snapshot = {
            "category": category,
            "title": questionnaire["title"],
            "description": questionnaire["description"],
            "questions": questionnaire["questions"],
        }
        bind.execute(
            text(
                """
                UPDATE assessment_results
                   SET questionnaire_version = :questionnaire_version,
                       questionnaire_snapshot = :questionnaire_snapshot,
                       scoring_version = :scoring_version
                 WHERE id = :id
                """
            ),
            {
                "id": row["id"],
                "questionnaire_version": QUESTIONNAIRE_VERSION,
                "questionnaire_snapshot": json.dumps(snapshot),
                "scoring_version": SCORING_VERSION,
            },
        )


def upgrade() -> None:
    bind = op.get_bind()

    # Add nullable columns first so existing rows remain valid during the migration.
    for name, column in (
        ("questionnaire_version", sa.Column("questionnaire_version", sa.String(32))),
        ("questionnaire_snapshot", sa.Column("questionnaire_snapshot", sa.JSON())),
        ("scoring_version", sa.Column("scoring_version", sa.String(32))),
    ):
        op.add_column("assessment_results", column)

    if not context.is_offline_mode():
        _deduplicate_results()
        _backfill_result_metadata()

    # Existing status data is normalized before constraints are introduced.
    if not context.is_offline_mode():
        bind.execute(
            text(
                """
                UPDATE assessments
                   SET status = 'draft'
                 WHERE status IS NULL OR status NOT IN ('draft', 'in_progress', 'completed')
                """
            )
        )
        bind.execute(
            text(
                """
                UPDATE assessments
                   SET completed_at = COALESCE(completed_at, updated_at, created_at, CURRENT_TIMESTAMP)
                 WHERE status = 'completed' AND completed_at IS NULL
                """
            )
        )

    # SQLite requires a batch table rebuild for reliable NOT NULL/check changes.
    if _is_sqlite():
        with op.batch_alter_table("assessment_results") as batch:
            batch.alter_column("questionnaire_version", existing_type=sa.String(32), nullable=False)
            batch.alter_column("questionnaire_snapshot", existing_type=sa.JSON(), nullable=False)
            batch.alter_column("scoring_version", existing_type=sa.String(32), nullable=False)
            batch.create_unique_constraint(
                "uq_assessment_results_assessment_category",
                ["assessment_id", "category"],
            )
            batch.create_check_constraint(
                "ck_assessment_results_category",
                "category IN ('data_privacy', 'model_risk', 'ethics', 'compliance')",
            )
        with op.batch_alter_table("assessments") as batch:
            batch.create_check_constraint(
                "ck_assessments_status",
                "status IN ('draft', 'in_progress', 'completed')",
            )
            batch.create_check_constraint(
                "ck_assessments_completed_at",
                "status <> 'completed' OR completed_at IS NOT NULL",
            )
    else:
        op.alter_column("assessment_results", "questionnaire_version", existing_type=sa.String(32), nullable=False)
        op.alter_column("assessment_results", "questionnaire_snapshot", existing_type=sa.JSON(), nullable=False)
        op.alter_column("assessment_results", "scoring_version", existing_type=sa.String(32), nullable=False)
        op.create_unique_constraint(
            "uq_assessment_results_assessment_category",
            "assessment_results",
            ["assessment_id", "category"],
        )
        op.create_check_constraint(
            "ck_assessment_results_category",
            "assessment_results",
            "category IN ('data_privacy', 'model_risk', 'ethics', 'compliance')",
        )
        op.create_check_constraint(
            "ck_assessments_status",
            "assessments",
            "status IN ('draft', 'in_progress', 'completed')",
        )
        op.create_check_constraint(
            "ck_assessments_completed_at",
            "assessments",
            "status <> 'completed' OR completed_at IS NOT NULL",
        )

    op.create_index(
        "ix_assessments_user_created_at",
        "assessments",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_assessments_user_status",
        "assessments",
        ["user_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_assessment_results_assessment_category",
        "assessment_results",
        ["assessment_id", "category"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_results_assessment_category", table_name="assessment_results")
    op.drop_index("ix_assessments_user_status", table_name="assessments")
    op.drop_index("ix_assessments_user_created_at", table_name="assessments")

    if _is_sqlite():
        with op.batch_alter_table("assessment_results") as batch:
            batch.drop_constraint("ck_assessment_results_category", type_="check")
            batch.drop_constraint("uq_assessment_results_assessment_category", type_="unique")
            batch.drop_column("scoring_version")
            batch.drop_column("questionnaire_snapshot")
            batch.drop_column("questionnaire_version")
        with op.batch_alter_table("assessments") as batch:
            batch.drop_constraint("ck_assessments_completed_at", type_="check")
            batch.drop_constraint("ck_assessments_status", type_="check")
    else:
        op.drop_constraint("ck_assessments_completed_at", "assessments", type_="check")
        op.drop_constraint("ck_assessments_status", "assessments", type_="check")
        op.drop_constraint("ck_assessment_results_category", "assessment_results", type_="check")
        op.drop_constraint(
            "uq_assessment_results_assessment_category",
            "assessment_results",
            type_="unique",
        )
        op.drop_column("assessment_results", "scoring_version")
        op.drop_column("assessment_results", "questionnaire_snapshot")
        op.drop_column("assessment_results", "questionnaire_version")
