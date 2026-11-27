-- Phase 4 PostgreSQL migration.
-- Run the duplicate and unknown-category checks first. The migration is intentionally
-- fail-closed before the unique constraint is created.
BEGIN;

-- Preflight: these queries must return zero rows before proceeding.
-- Duplicate result groups:
SELECT assessment_id, category, COUNT(*) AS duplicate_count
FROM assessment_results
GROUP BY assessment_id, category
HAVING COUNT(*) > 1;

-- Unknown categories:
SELECT DISTINCT category
FROM assessment_results
WHERE category NOT IN ('data_privacy', 'model_risk', 'ethics', 'compliance');

-- Keep the latest deterministic result if a controlled cleanup is approved.
WITH ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY assessment_id, category
               ORDER BY created_at DESC NULLS LAST, id DESC
           ) AS row_number
    FROM assessment_results
)
DELETE FROM assessment_results
WHERE id IN (SELECT id FROM ranked WHERE row_number > 1);

ALTER TABLE assessment_results
    ADD COLUMN IF NOT EXISTS questionnaire_version VARCHAR(32),
    ADD COLUMN IF NOT EXISTS questionnaire_snapshot JSONB,
    ADD COLUMN IF NOT EXISTS scoring_version VARCHAR(32);

-- The application backfill job must populate exact snapshots before these statements.
-- See backfill_phase4.sql and backend/alembic/versions/0002_phase4_integrity.py.
UPDATE assessment_results
SET questionnaire_version = COALESCE(questionnaire_version, '1.0'),
    scoring_version = COALESCE(scoring_version, '1.0')
WHERE questionnaire_version IS NULL OR scoring_version IS NULL;

-- Do not use an invented snapshot for production history. This statement only exposes
-- rows still requiring the application backfill before NOT NULL is enforced.
SELECT id
FROM assessment_results
WHERE questionnaire_snapshot IS NULL;

ALTER TABLE assessment_results
    ALTER COLUMN questionnaire_version SET NOT NULL,
    ALTER COLUMN questionnaire_snapshot SET NOT NULL,
    ALTER COLUMN scoring_version SET NOT NULL;

UPDATE assessments
SET status = 'draft'
WHERE status IS NULL OR status NOT IN ('draft', 'in_progress', 'completed');

UPDATE assessments
SET completed_at = COALESCE(completed_at, updated_at, created_at, CURRENT_TIMESTAMP)
WHERE status = 'completed' AND completed_at IS NULL;

ALTER TABLE assessments
    ADD CONSTRAINT ck_assessments_status
    CHECK (status IN ('draft', 'in_progress', 'completed')) NOT VALID;

ALTER TABLE assessments
    ADD CONSTRAINT ck_assessments_completed_at
    CHECK (status <> 'completed' OR completed_at IS NOT NULL) NOT VALID;

ALTER TABLE assessment_results
    ADD CONSTRAINT ck_assessment_results_category
    CHECK (category IN ('data_privacy', 'model_risk', 'ethics', 'compliance')) NOT VALID;

ALTER TABLE assessment_results
    ADD CONSTRAINT uq_assessment_results_assessment_category
    UNIQUE (assessment_id, category);

CREATE INDEX IF NOT EXISTS ix_assessments_user_created_at
    ON assessments (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_assessments_user_status
    ON assessments (user_id, status);
CREATE INDEX IF NOT EXISTS ix_assessment_results_assessment_category
    ON assessment_results (assessment_id, category);

COMMIT;
