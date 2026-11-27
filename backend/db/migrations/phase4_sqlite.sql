-- Phase 4 SQLite migration.
-- SQLite cannot add a UNIQUE constraint or alter NOT NULL columns in place.
-- Run the preflight queries first, then use the Alembic 0002 migration for the
-- production-safe table rebuild. This file is also suitable for a controlled
-- disposable test database.
PRAGMA foreign_keys = ON;

-- Preflight: both queries must return zero rows before cleanup/constraint creation.
SELECT assessment_id, category, COUNT(*) AS duplicate_count
FROM assessment_results
GROUP BY assessment_id, category
HAVING COUNT(*) > 1;

SELECT DISTINCT category
FROM assessment_results
WHERE category NOT IN ('data_privacy', 'model_risk', 'ethics', 'compliance');

-- Deterministically retain the newest result in each duplicate group.
DELETE FROM assessment_results
WHERE id IN (
    SELECT older.id
    FROM assessment_results AS older
    JOIN assessment_results AS newer
      ON newer.assessment_id = older.assessment_id
     AND newer.category = older.category
     AND (
          COALESCE(newer.created_at, '') > COALESCE(older.created_at, '')
          OR (
              COALESCE(newer.created_at, '') = COALESCE(older.created_at, '')
              AND newer.id > older.id
          )
     )
);

ALTER TABLE assessment_results ADD COLUMN questionnaire_version VARCHAR(32);
ALTER TABLE assessment_results ADD COLUMN questionnaire_snapshot JSON;
ALTER TABLE assessment_results ADD COLUMN scoring_version VARCHAR(32);

-- The exact questionnaire_snapshot must be populated by the Python backfill or
-- Alembic 0002 before the rebuilt table is made NOT NULL.
UPDATE assessment_results
SET questionnaire_version = COALESCE(questionnaire_version, '1.0'),
    scoring_version = COALESCE(scoring_version, '1.0')
WHERE questionnaire_version IS NULL OR scoring_version IS NULL;

SELECT id
FROM assessment_results
WHERE questionnaire_snapshot IS NULL;

UPDATE assessments
SET status = 'draft'
WHERE status IS NULL OR status NOT IN ('draft', 'in_progress', 'completed');

UPDATE assessments
SET completed_at = COALESCE(completed_at, updated_at, created_at, CURRENT_TIMESTAMP)
WHERE status = 'completed' AND completed_at IS NULL;

-- These indexes can be created directly; the unique constraint is added by the
-- Alembic batch rebuild so existing SQLite tables remain portable.
CREATE INDEX IF NOT EXISTS ix_assessments_user_created_at
    ON assessments (user_id, created_at);
CREATE INDEX IF NOT EXISTS ix_assessments_user_status
    ON assessments (user_id, status);
CREATE INDEX IF NOT EXISTS ix_assessment_results_assessment_category
    ON assessment_results (assessment_id, category);

-- Validation queries after the Alembic rebuild:
SELECT assessment_id, category, COUNT(*) AS duplicate_count
FROM assessment_results
GROUP BY assessment_id, category
HAVING COUNT(*) > 1;

PRAGMA foreign_key_check;
