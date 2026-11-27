# Phase 4 Synchronization and Continuous Development Runbook

## Current repository state

The validated Phase 4 implementation exists in the development working tree, but the GitHub `main` branch used by the Windows checkout is older. The Windows `git pull --ff-only` operation only downloaded two older backend changes because the Phase 4 files were not yet present on `origin/main`.

The Windows checkout also contains a manually created `backend/scripts/backfill_phase4.py`. Keep that file only as a temporary local copy until the canonical Phase 4 files are committed to the repository. The durable fix is to publish the complete Phase 4 change set, not to keep relying on manual file creation.

## Files that must be synchronized as one Phase 4 change set

The following backend files define the Phase 4 model and migration contract:

```text
backend/db/models.py
backend/alembic/versions/0002_phase4_integrity.py
backend/assessments/crud.py
backend/assessments/router.py
backend/assessments/schemas.py
backend/scripts/__init__.py
backend/scripts/backfill_phase4.py
backend/test_phase4_integrity.py
```

The frontend and acceptance-test files should be synchronized in the same release branch or in a directly dependent follow-up commit:

```text
frontend/src/services/api.ts
frontend/src/services/apiErrors.ts
frontend/src/context/AuthContext.tsx
frontend/src/pages/AssessmentPage.tsx
frontend/src/pages/DashboardPage.tsx
frontend/src/pages/LoginPage.tsx
frontend/src/pages/ReportPage.tsx
frontend/src/tests/ApiErrors.test.ts
frontend/e2e/mock-api.ts
frontend/e2e/complete-user-journey.spec.ts
frontend/e2e/phase4-error-recovery.spec.ts
frontend/playwright.config.ts
```

The three `AssessmentResult` fields are not standalone additions. They must ship with the migration and backfill utility:

```text
questionnaire_version
questionnaire_snapshot
scoring_version
```

## Safe publication sequence from the canonical development checkout

Run these commands from the checkout containing the validated Phase 4 files. Do not run them from the older Windows checkout unless the files have already been copied there.

```bash
git status --short
git fetch origin
git switch -c phase4-integrity-and-e2e
```

Review the file list before staging. Do not stage `.env`, databases, logs, build output, screenshots, or credentials.

```bash
git add \
  backend/db/models.py \
  backend/alembic/versions/0002_phase4_integrity.py \
  backend/assessments/crud.py \
  backend/assessments/router.py \
  backend/assessments/schemas.py \
  backend/scripts/__init__.py \
  backend/scripts/backfill_phase4.py \
  backend/test_phase4_integrity.py \
  frontend/src/services/api.ts \
  frontend/src/services/apiErrors.ts \
  frontend/src/context/AuthContext.tsx \
  frontend/src/pages/AssessmentPage.tsx \
  frontend/src/pages/DashboardPage.tsx \
  frontend/src/pages/LoginPage.tsx \
  frontend/src/pages/ReportPage.tsx \
  frontend/src/tests/ApiErrors.test.ts \
  frontend/e2e/mock-api.ts \
  frontend/e2e/complete-user-journey.spec.ts \
  frontend/e2e/phase4-error-recovery.spec.ts \
  frontend/playwright.config.ts

git diff --cached --check
git diff --cached --stat
git commit -m "feat: complete phase 4 integrity and recovery validation"
git push -u origin phase4-integrity-and-e2e
```

After the push, open a pull request from `phase4-integrity-and-e2e` into `main`. Do not push directly to `main` until the CI checks pass.

If the repository has required Git author configuration, set your own identity; do not use another person’s identity:

```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"
```

## Safe Windows synchronization after the pull request is merged

First close running development servers and activate the same Python environment used for the project. Then open Command Prompt in the outer repository directory:

```cmd
cd /d C:\Users\PC\AI_Governance_Assessor_v2.1
```

Create a recovery branch before changing anything:

```cmd
git status --short
git switch -c backup-before-phase4-sync
```

If the status shows local files you need, preserve them before synchronization. Do not delete them automatically. After the Phase 4 pull request is merged, fetch and update the main branch:

```cmd
git fetch origin
git switch main
git pull --ff-only origin main
```

Confirm the Phase 4 files now exist:

```cmd
dir backend\scripts
dir /s /b backend\*backfill_phase4.py
findstr /n /c:"questionnaire_version" backend\db\models.py
findstr /n /c:"questionnaire_snapshot" backend\db\models.py
findstr /n /c:"scoring_version" backend\db\models.py
```

If the fields or script are absent after `git pull`, stop. The Phase 4 commit has not been merged into the branch you pulled; do not manually mix versions again.

## Local validation after synchronization

Activate the project environment and set the import path:

```cmd
.venv\Scripts\activate
set PYTHONPATH=.
python --version
python -c "import pydantic_settings; print('dependencies ok')"
```

Run the backend tests:

```cmd
cd /d C:\Users\PC\AI_Governance_Assessor_v2.1\backend
set PYTHONPATH=..
python -m pytest -q
```

Run frontend checks from a second Command Prompt or after returning to the repository root, using Node.js installed for the project:

```cmd
cd /d C:\Users\PC\AI_Governance_Assessor_v2.1\frontend
npm ci
npm run test
npm run lint
npm run build
```

Run the mocked browser suite only after the frontend development server is available and the Playwright browser is installed:

```cmd
npx playwright install chromium
set BASE_URL=http://127.0.0.1:5173/
set E2E_EVIDENCE=1
npm run test:e2e
```

## Correct write-mode sequence for a real staging database

Do not run write mode until all of the following are true:

- the Phase 4 migration is present in the synchronized branch;
- the model contains all three metadata fields;
- the backfill script is tracked by Git rather than manually created only on one machine;
- a current database backup or provider snapshot exists;
- the dry-run has been reviewed;
- the duplicate preflight reports no duplicate `(assessment_id, category)` groups;
- the unknown-category preflight reports no unknown categories;
- the exact staging database has been confirmed by the operator.

In Windows Command Prompt, set the private DSN without printing it:

```cmd
set "STAGING_DATABASE_URL=PASTE_PRIVATE_POSTGRES_CONNECTION_STRING_HERE"
if defined STAGING_DATABASE_URL (echo STAGING_DATABASE_URL is set) else (echo STAGING_DATABASE_URL is missing)
```

Run the migration using the synchronized Phase 4 branch. For PostgreSQL, the full requirements file must be installed in the Python 3.12 virtual environment, including the PostgreSQL driver. If the organization blocks installation of `psycopg2-binary`, use the organization-approved Python/container environment rather than bypassing policy.

Run the dry-run first:

```cmd
cd /d C:\Users\PC\AI_Governance_Assessor_v2.1
set PYTHONPATH=.
python -m backend.scripts.backfill_phase4 --database-url "%STAGING_DATABASE_URL%" --dry-run
```

Only if the output is clean and a backup exists, run the write mode:

```cmd
python -m backend.scripts.backfill_phase4 --database-url "%STAGING_DATABASE_URL%"
```

Verify afterward with a read-only query or the provider’s database console that the result rows contain non-null values for `questionnaire_version`, `questionnaire_snapshot`, and `scoring_version`. Do not paste the DSN or query output containing credentials into chat.

## Continuous integration gates

The CI pipeline should become a release gate rather than only a build check. Every pull request should run backend tests, frontend unit tests, lint, frontend production build, migration compilation, and the mocked Playwright suite. The E2E job should use a deterministic API mock and must not require staging credentials.

The release branch should also verify:

- `git diff --check`;
- migration SQL compilation for PostgreSQL;
- SQLite schema or migration smoke validation;
- duplicate and unknown-category backfill preflight;
- ownership tests for assessment, result, finding, evidence, and export endpoints as those resources are added;
- no tracked `.env`, database, token, report, or personal-data artifacts.

Staging write-mode backfills must remain an explicit, manually approved deployment step. They should not run automatically on every push or pull request.

## Continuous development sequence

The next product increments should preserve the governance workflow direction:

1. Stabilize the Phase 4 branch and merge the complete integrity/recovery change set.
2. Add contextual AI-system intake and a versioned AI-use inventory.
3. Add evidence records with provenance, freshness, access control, and reviewer disposition.
4. Convert material assessment gaps into owned findings and remediation actions.
5. Add review dates, material-change triggers, incident/feedback intake, and reassessment history.
6. Add framework crosswalks and role-specific reports without claiming certification.
7. Prototype source-grounded ML only after the deterministic workflow is stable. ML may extract candidate fields, match evidence, draft actions, or flag changes; it must show source passages, uncertainty, and human approval, and must never make high-impact decisions or declare compliance.

The product claim should remain aligned with implementation. Until the inventory, evidence, ownership, and review features exist, describe the product as helping teams organize an initial self-assessment and identify follow-up questions. After those features are implemented, describe it as helping teams document AI use cases, organize governance evidence, identify follow-up work, and track review decisions over time.
