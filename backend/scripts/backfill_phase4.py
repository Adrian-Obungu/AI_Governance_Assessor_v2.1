"""Backfill Phase 4 metadata for existing assessment results.

Usage from the repository root:
    python -m backend.scripts.backfill_phase4 --database-url "$DATABASE_URL" --dry-run
    python -m backend.scripts.backfill_phase4 --database-url "$DATABASE_URL"

The command is deliberately fail-closed for unknown categories and duplicate
assessment/category pairs. Resolve those rows before running the write mode.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from backend.assessments.questionnaire import QUESTIONNAIRES

QUESTIONNAIRE_VERSION = "1.0"
SCORING_VERSION = "1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def run(database_url: str, dry_run: bool) -> int:
    engine = create_engine(database_url)
    with Session(engine) as db:
        duplicate_rows = db.execute(
            text(
                """
                SELECT assessment_id, category, COUNT(*) AS count
                FROM assessment_results
                GROUP BY assessment_id, category
                HAVING COUNT(*) > 1
                """
            )
        ).all()
        if duplicate_rows:
            raise RuntimeError(
                "Duplicate assessment/category rows exist; clean them before backfill: "
                f"{duplicate_rows}"
            )

        rows = db.execute(
            text("SELECT id, category FROM assessment_results ORDER BY id")
        ).mappings().all()
        unknown = sorted({row["category"] for row in rows if row["category"] not in QUESTIONNAIRES})
        if unknown:
            raise RuntimeError(f"Unknown assessment result categories: {unknown}")

        counts = Counter(row["category"] for row in rows)
        print(f"Rows to backfill: {len(rows)}")
        print(f"Categories: {dict(sorted(counts.items()))}")

        for row in rows:
            questionnaire = QUESTIONNAIRES[row["category"]]
            snapshot = {
                "category": row["category"],
                "title": questionnaire["title"],
                "description": questionnaire["description"],
                "questions": questionnaire["questions"],
            }
            if dry_run:
                continue
            db.execute(
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

        if dry_run:
            db.rollback()
            print("Dry run complete; no rows changed.")
        else:
            db.commit()
            print("Backfill committed.")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    return run(args.database_url, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
