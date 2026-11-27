# Phase 5A Plan: AI-System Inventory and Contextual Intake

## Outcome

Add a user-owned AI-system inventory so a governance review starts with a real system or AI-enabled process rather than an anonymous questionnaire. The first vertical slice supports creating, listing, viewing, and updating inventory records. Assessments will remain compatible with the existing workflow; later work will attach assessments, evidence, findings, owners, and reassessments to an inventory record.

## Scope for this slice

Required behavior:

- An authenticated user can create an AI-system record.
- The record captures a name, purpose, department, owner, lifecycle stage, provider/vendor, geography, data categories, affected groups, and review date.
- The API validates required values and restricts records to their owning user.
- A user can list and view only their own records.
- A user can update their own record.
- The frontend provides a low-cognitive-load inventory page with a short guided form, clear explanations, and a list of existing systems.
- The dashboard provides a clear entry point to the inventory.
- The feature uses SQLite-compatible and PostgreSQL-compatible migrations.
- Tests cover validation, ownership isolation, create/list/update behavior, and the frontend API contract.

Out of scope:

- Evidence uploads.
- Findings or remediation actions.
- Automated legal or compliance conclusions.
- ML recommendations.
- Sharing records across users or organizations.
- Linking an assessment to an inventory record; that is the next incremental slice after this foundation is stable.

## Data model

Create `ai_systems` with:

- `id`, `user_id`, `name`, `purpose`.
- `department`, `business_owner`, `provider`, `lifecycle_stage`.
- `geographies` JSON list, `data_categories` JSON list, `affected_groups` JSON list.
- `review_date`, `created_at`, `updated_at`.
- A user/name index and an ownership index.
- A lifecycle check constraint for `discovery`, `pilot`, `in_production`, `retired`.

The model uses JSON lists for this first slice so the form remains simple and the later evidence/context model can evolve without premature normalization. Values are user-entered context, not verified legal classifications.

## API

Add authenticated endpoints under `/inventory`:

- `POST /inventory`
- `GET /inventory`
- `GET /inventory/{system_id}`
- `PUT /inventory/{system_id}`

Return `404` for records owned by another user to avoid exposing their existence. Use Pydantic field limits and a `review_date` date field.

## Frontend interaction design

Design movement: **calm operational workspace** — a plain-language, mobile-first control room rather than an enterprise GRC dashboard.

Core principles: progressive disclosure, one clear next action, context before scoring, and visible ownership. The form uses three short groups: identify the system, understand its context, and set the next review. Help text explains why each group matters. The list shows lifecycle, owner, provider, and review date without overwhelming the user.

Color philosophy: retain the existing blue/teal trust palette and use amber only for review attention. Avoid red for ordinary incomplete context.

Layout paradigm: a focused page with a prominent “Add AI system” action, a compact list of system cards, and a form panel that can be completed on a phone.

Interaction philosophy: autosave is not introduced in this first slice, so the form must preserve entered state after validation errors and show a clear unsaved-state warning only if the user navigates away. Success returns to the inventory list with the new record visible.

Brand voice: “Start with the system you need to understand.” and “Capture enough context to choose the right governance work next.”

## Project structure

- `backend/db/models.py`: `AISystem` ORM entity.
- `backend/inventory/schemas.py`: request/response validation.
- `backend/inventory/crud.py`: ownership-scoped data access.
- `backend/inventory/router.py`: authenticated API routes.
- `backend/alembic/versions/0003_ai_system_inventory.py`: schema migration.
- `backend/test_inventory.py`: backend regression and ownership tests.
- `frontend/src/pages/InventoryPage.tsx`: inventory list and intake form.
- `frontend/src/services/api.ts`: inventory API client.
- `frontend/src/types/index.ts`: inventory types.
- `frontend/src/App.tsx`: protected route.
- `frontend/src/pages/DashboardPage.tsx`: entry point.

## Validation and delivery

Run backend inventory tests and the full backend suite with the temporary `.env` protection already established for Windows. Run frontend unit tests, lint, and production build. Add a focused mocked API contract test for inventory creation/listing. Do not run database write mode against staging as part of this feature; the migration remains subject to the existing manual deployment process.

## Phase 5B: Link assessments to inventory context

The next vertical slice adds an optional `ai_system_id` to an assessment. New assessments may reference one AI-system record owned by the authenticated user; existing assessments remain valid with no linked system. The API must reject another user’s system with `404`, preserve ownership boundaries, and expose the linked system summary in assessment responses. The dashboard creation flow will offer the user’s inventory records as an optional context choice, while the questionnaire and scoring behavior remain unchanged.

This slice excludes evidence, findings, remediation, automated recommendations, and hosted sensitive-data deployment. It will use a nullable foreign key, ownership-aware validation, a SQLite/PostgreSQL-compatible migration, backend regression tests, and a frontend API/UI contract test.

## Phase 5C: Evidence records without file uploads

The next vertical slice adds structured evidence metadata so users can record what supports a governance review without introducing document storage or upload risk. An evidence record belongs to the authenticated user and must link to an owned AI system; it may optionally link to an owned assessment. It captures title, explanation, evidence type, source/location, owner, collection date, review date, status, and reviewer notes.

The first UI is a mobile-friendly evidence workspace with a short form, status and review-date visibility, and filters by AI system and status. “Source/location” is a URL or human-readable reference only; this slice does not upload, scan, OCR, classify, or retain files. Evidence is recorded supporting context, not verified proof, legal advice, certification, or an automated compliance conclusion.

Implementation files for this slice are `backend/evidence/` for schemas, ownership-scoped CRUD, and routes; `backend/alembic/versions/0005_evidence_records.py` for the portable migration; `backend/test_evidence.py` for API and isolation coverage; `frontend/src/pages/EvidencePage.tsx` for the guided workspace; and the shared frontend API/types, protected route, dashboard entry point, route manifest, and API contract test.

Phase 5C validation completed with the full backend suite (`30 passed`), frontend tests (`18 passed`), Black, Ruff, ESLint, TypeScript/Vite production build, `git diff --check`, and a disposable SQLite migration through revision `0005`.

## Phase 5D: Findings and owned remediation actions

This slice adds one focused finding record rather than a separate task-management system. Each finding links an owned AI system and evidence record, may link an assessment, and captures a plain-language conclusion, priority, accountable owner, remediation action, due date, workflow status, and reviewer notes. The API verifies that the evidence belongs to the selected AI system so records cannot silently mix contexts.

The frontend findings workspace follows the same calm operational pattern as inventory and evidence: filters first, one clear “Add finding” action, and cards that show the conclusion, remediation action, owner, due date, priority, status, and evidence reference. It stores working governance records only; it does not generate legal conclusions, certification claims, objective safety decisions, or automated high-impact decisions.

Implementation files are `backend/findings/` for schemas, ownership-scoped CRUD, and routes; `backend/alembic/versions/0006_findings_remediation.py` for the portable migration; `backend/test_findings.py` for authorization and context-link coverage; `frontend/src/pages/FindingsPage.tsx` for the guided workspace; and the shared frontend API/types, protected route, dashboard entry point, route manifest, and API contract test.

Phase 5D validation completed with the full backend suite (`33 passed`), frontend tests (`20 passed`), Black, Ruff, ESLint, TypeScript/Vite production build, `git diff --check`, and a disposable SQLite migration through revision `0006`.

## Phase 5E: Human review and reassessment workflow

This slice adds a review record for a human decision about an AI system. It captures the reviewer, review date, decision (`continue`, `reassess`, `pause`, or `retire`), material-change flag, change summary, next review date, reviewer notes, and optional links to the assessment being reviewed and a follow-up reassessment. Linked assessments must belong to the same user and AI-system context.

The frontend review workspace keeps the next action clear: select the system, record the human decision, explain any material change, optionally link the reassessment assessment, and set the next review date. It records review context and traceability only; it does not automate legal, certification, safety, or high-impact decisions.

Implementation files are `backend/reviews/` for schemas, ownership-scoped CRUD, and routes; `backend/alembic/versions/0007_review_reassessment.py` for the portable migration; `backend/test_reviews.py` for authorization and context-link coverage; `frontend/src/pages/ReviewsPage.tsx` for the guided workspace; and the shared frontend API/types, protected route, dashboard entry point, route manifest, and API contract test.

Phase 5E validation completed with the full backend suite (`36 passed`), frontend tests (`22 passed`), Black, Ruff, ESLint, TypeScript/Vite production build, `git diff --check`, and a disposable SQLite migration through revision `0007`.

## Phase 5F: Operational signals and incident/feedback intake

This slice adds one operational signal record rather than separate incident-management and feedback products. A signal belongs to the authenticated user and an AI-system inventory record, and may optionally link to a finding or human review from that same system context. Supported types are `incident`, `feedback`, and `material_change`; supported severities are `low`, `medium`, `high`, and `critical`; supported workflow statuses are `new`, `triaged`, `investigating`, and `closed`.

Each record captures a title, plain-language description, reported-by source, discovered date, owner, response or next action, and reviewer notes. The API validates Pydantic values and database checks, scopes all reads and writes to the authenticated owner, supports filters by system/type/severity/status, and returns `404` for inaccessible or context-mismatched links. This keeps the record useful for small teams without claiming that the platform has determined a legal incident category or objective safety outcome.

The frontend adds a mobile-friendly operational signals workspace with a short intake form, simple filters, visible severity and status, and a human-controlled “Mark closed” action. The dashboard presents signals as the next operational step after review: teams can record what happened, assign an owner, and carry the item into future human review. No automated classification, automated triage, file upload, sensitive-data hosting, certification, legal conclusion, or autonomous high-impact decision is introduced.

Implementation files are `backend/signals/` for schemas, ownership-scoped CRUD, and routes; `backend/alembic/versions/0008_operational_signals.py` for the portable migration; `backend/test_signals.py` for validation, filtering, context-link, and isolation coverage; `frontend/src/pages/SignalsPage.tsx` for the guided workspace; and the shared frontend API/types, protected route, dashboard entry point, and route manifest.

Validation must include the full backend suite, focused signal tests, Black, Ruff, frontend Vitest, ESLint, TypeScript/Vite production build, `git diff --check`, and disposable SQLite migration through revision `0008`. Any staging write-mode migration or backfill remains a manual operator action and is not part of CI.

## Phase 5G: Consolidated governance activity view

This slice adds a derived, read-only activity timeline instead of another persistent case-management table. It combines records that already exist for a user-owned AI system: inventory context, linked assessments, metadata-only evidence, findings, human reviews, and operational signals. The API returns source type and identifier, system context, occurred timestamp, title, summary, and the relevant status, priority, or severity.

The timeline is assembled at read time from existing ownership-scoped tables. It supports optional AI-system and source-type filters, returns an empty result when an inaccessible system identifier is supplied, and never exposes another user’s records. Dates that are stored as dates are normalized to the start of that day for consistent ordering; record timestamps are used where available.

The frontend presents a calm operational timeline with two filters and clear source badges. It is a navigation and orientation surface, not a new workflow: users continue to edit evidence, findings, reviews, and signals in their existing workspaces. The page explains that events are derived from recorded governance work and does not infer legal conclusions, certification, objective safety, or automated decisions.

Implementation files are `backend/activity/` for the response schema, derived query logic, and route; `backend/test_activity.py` for ordering, filtering, invalid-filter, and cross-user coverage; `frontend/src/pages/ActivityPage.tsx` for the timeline; and the shared frontend API/types, protected route, dashboard entry point, route manifest, and API contract test. No migration is required for this read model.

## Phase 5H: AI-system governance snapshot

This slice adds a derived snapshot for each owned AI system. It summarizes workflow coverage counts for linked assessments, evidence records, findings, human reviews, and operational signals. It also exposes open findings, overdue remediation actions, active signals, reached review dates, and human-readable attention items. These are indicators of recorded workflow state, not a risk score, legal conclusion, certification, or objective safety measure.

The backend assembles snapshots at read time from existing tables under `/governance/snapshots`, with an optional AI-system filter. Attention ordering is intentionally transparent: missing assessment context, missing evidence, overdue/open remediation, active signals, and reached review dates become prompts for human follow-up. The API is read-only and owner-scoped, and no migration is required.

The frontend presents one selected system at a time by default, with coverage cards, attention items, the next suggested workflow action, and navigation links to inventory, evidence, findings, reviews, and signals. The language explains that the snapshot reflects recorded governance work and should be reviewed by a person.

Implementation files are `backend/snapshot/` for schemas, derived query logic, and routes; `backend/test_snapshot.py` for coverage, attention ordering, filters, and user isolation; `frontend/src/pages/SnapshotPage.tsx` for the workspace; and the shared frontend API/types, protected route, dashboard entry point, route manifest, and API contract test. No new persistent entity or automated decision engine is introduced.
