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
