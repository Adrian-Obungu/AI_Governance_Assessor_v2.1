# Phase 4 Technical Specification

## Scope

This specification defines the implementation contract for two related hardening tracks:

- **Phase 4A — Frontend error handling and token recovery**
- **Phase 4B — Assessment data integrity, versioning, and database constraints**

The design preserves the current React/Vite/FastAPI/SQLAlchemy architecture, keeps the existing successful user journey intact, and adds explicit behavior for expired sessions, network failures, malformed submissions, duplicate submissions, and questionnaire changes.

## Current-state assumptions

The current frontend stores the bearer token and email in `localStorage`, uses direct `fetch` calls in `frontend/src/services/api.ts`, and protects routes with `ProtectedRoute`. Assessment pages reload both the assessment and the questionnaire collection after every category submission.

The current database has `assessments` and `assessment_results`. `AssessmentResult` stores answers in a JSON column, but there is no database-level uniqueness constraint for `(assessment_id, category)`. The assessment model contains `schema_version`, but result rows do not preserve the questionnaire or scoring interpretation used at submission time.

The current assessment status values are represented as strings: `draft`, `in_progress`, and `completed`.

---

# Phase 4A — Frontend error handling and token recovery

## Goals

1. Make authentication failures deterministic and user-visible.
2. Prevent stale or infinite loading states after expired sessions.
3. Give users a safe retry path for transient network and server failures.
4. Preserve entered assessment answers when a submission fails.
5. Prevent duplicate answer submissions and duplicate export requests.
6. Keep the successful Playwright journey unchanged.

## Non-goals

- Replacing the authentication model with an external identity provider.
- Introducing a global state library.
- Automatically retrying non-idempotent answer submissions.
- Hiding authorization failures behind generic retry messages.

## Error taxonomy

The frontend API layer must normalize failures into a small typed set:

```ts
export type ApiErrorKind =
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'validation'
  | 'conflict'
  | 'rate_limited'
  | 'server'
  | 'network'
  | 'aborted'
  | 'unknown';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly detail?: string;
  readonly retryable: boolean;

  constructor(
    message: string,
    options: {
      kind: ApiErrorKind;
      status?: number;
      detail?: string;
      retryable?: boolean;
    },
  ) {
    super(message);
    this.name = 'ApiError';
    this.kind = options.kind;
    this.status = options.status;
    this.detail = options.detail;
    this.retryable = options.retryable ?? false;
  }
}
```

### Error mapping

| Response/condition | Kind | Retry | Required UI behavior |
|---|---|---:|---|
| `401` | `unauthorized` | No | Clear auth state and redirect to `/login` with a session-expired notice |
| `403` | `forbidden` | No | Show an access-denied message; do not retry automatically |
| `404` | `not_found` | No | Show resource-not-found state |
| `409` | `conflict` | No | Explain that the resource changed or was already submitted; reload current state |
| `422` | `validation` | No | Show server validation details near the form or assessment section |
| `429` | `rate_limited` | After delay | Show rate-limit message and retry guidance |
| `5xx` | `server` | Once manually | Show temporary service error with a Retry action |
| Fetch rejection | `network` | Once manually | Show offline/network message with a Retry action |
| AbortController cancellation | `aborted` | No | Do not show an error for intentional navigation/unmount cancellation |

## API client contract

Replace direct per-method `fetch` error handling with a single request helper in `frontend/src/services/api.ts`.

Required behavior:

1. Attach `Authorization: Bearer <token>` when a token is supplied.
2. Parse JSON error bodies when available, but tolerate empty or non-JSON error responses.
3. Convert HTTP failures into `ApiError`.
4. Apply a default timeout of 15 seconds using `AbortController`.
5. Allow callers to provide an external `AbortSignal`.
6. Never retry `POST /answers` automatically.
7. Provide an `onUnauthorized` callback or injected auth handler so the API layer can trigger logout without importing React context.
8. Preserve response bodies for CSV/PDF blob endpoints.

Suggested request shape:

```ts
interface RequestOptions extends RequestInit {
  token?: string;
  timeoutMs?: number;
  signal?: AbortSignal;
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T>;
```

The helper must distinguish an intentional abort from a timeout. Both may use `AbortError` internally, but a timeout should become a retryable `network` or `server`-style error while an unmount/navigation abort should be silent.

## Token recovery flow

### Auth context additions

Extend `AuthContext` with:

```ts
interface AuthContextType {
  token: string | null;
  email: string | null;
  isAuthenticated: boolean;
  login: (token: string, email: string) => void;
  logout: () => void;
  expireSession: (message?: string) => void;
  sessionMessage: string | null;
  clearSessionMessage: () => void;
}
```

`expireSession()` must:

1. Remove `auth_token` and `auth_email` from `localStorage`.
2. Clear React auth state.
3. Store a short-lived user-facing message such as `Your session expired. Please sign in again.`
4. Navigate to `/login` once.
5. Be idempotent if multiple requests return `401` at the same time.

Do not allow each failed request to trigger its own navigation. Use a ref or a centralized transition guard.

### Route behavior

`ProtectedRoute` must continue redirecting unauthenticated users to `/login`. The login page must render `sessionMessage` once, with `role="alert"`, then clear it after display or after the next successful login.

Direct navigation to `/assessment/:id` or `/report/:id` after expiration must result in `/login`, not a blank page or an infinite loading indicator.

## Page-level state contracts

### Dashboard

States:

- `loading`: initial list request is pending.
- `ready`: list rendered.
- `error`: list failed; show message and Retry button.
- `creating`: create button disabled and labelled `Creating...`.
- `createError`: modal remains open and preserves title/description/template values.

A failed list request must not silently render an empty assessment list. Empty state is valid only after a successful response containing zero assessments.

### Assessment page

States:

- Initial loading
- Loaded category
- Saving section
- Save error
- Session expired
- Assessment not found
- Completed/report navigation

On answer submission failure:

- Keep all selected answers in local React state.
- Keep the current category selected.
- Re-enable the submit button.
- Display an alert with a Retry action or allow the user to press the same submit button again.
- Do not display `Section saved`.

On a `409` duplicate/concurrent submission:

1. Reload the assessment.
2. Reconcile the category status.
3. Tell the user that the section was already saved.
4. Continue to the next incomplete category or report.

On `401`, use the centralized token recovery flow.

The `useEffect` that loads assessment data must include all relevant dependencies or use a stable callback. It must not race a token change or update state after unmount.

### Report page

States:

- Loading
- Loaded report
- Report load error
- Exporting CSV/PDF
- Export error
- Session expired

Only one export may run at a time. Export buttons must remain disabled during the request and be re-enabled after success or failure. A failed export must preserve the report and show an actionable alert.

Object URLs must be revoked after the browser has received the download click, preferably on the next task tick rather than immediately in the same synchronous block.

## Retry policy

Automatic retry is intentionally limited:

- GET questionnaire/list/detail/summary: no automatic retry in the first implementation; expose a manual Retry action.
- POST answer submission: never automatic.
- CSV/PDF export: manual retry only.
- `429`: Retry-After may be honored once for GET requests; do not retry answer writes.

A retry must use the same route and current auth token. If the token has expired, token recovery takes precedence over retry.

## Abort and stale-update protection

Every page-level load operation must use an `AbortController` and abort on unmount or route-ID change. Before setting state after an awaited request, either rely on an active-signal check or use a request generation counter.

Required invariant:

> No unmounted page may update React state after its request completes.

## User-visible copy

Use consistent, non-technical messages:

- Session: `Your session expired. Please sign in again.`
- Network: `We could not reach the service. Check your connection and try again.`
- Temporary server failure: `The service is temporarily unavailable. Please try again.`
- Save failure: `We could not save this section. Your answers are still here; try again.`
- Report failure: `We could not load this report. Please try again.`
- Export failure: `We could not export the CSV/PDF report. Please try again.`
- Not found: `This assessment could not be found or you no longer have access to it.`

All messages must use `role="alert"` or `role="status"` appropriately and remain accessible to screen readers.

## Phase 4A tests

### Unit tests

Add tests for:

1. HTTP `401` invokes `expireSession` once.
2. `403`, `404`, `409`, `422`, `429`, `5xx`, network failure, timeout, and abort map correctly.
3. A failed assessment save preserves selected answers.
4. A failed assessment list does not render the empty state.
5. A failed report export re-enables both buttons and displays an alert.
6. The session-expired message is displayed once on the login page.
7. An aborted request does not display an error.
8. Retry uses the current token and does not duplicate answer writes.

### Playwright scenarios

Extend the native suite with deterministic route interception for:

- Expired token during dashboard load
- Expired token during assessment save
- Network failure during answer submission
- Server error during report load
- Failed CSV/PDF export
- Refresh after completing two categories
- Double-click on `Save and continue`
- Mobile viewport and keyboard-only answer selection

### Acceptance criteria

- No protected page remains indefinitely in a loading state after `401`.
- A `401` results in exactly one redirect to `/login`.
- Failed writes preserve user input.
- Empty states are not shown for failed list requests.
- Every retryable failure has an accessible retry path.
- Existing happy-path Playwright evidence remains green.

---

# Phase 4B — Database schema and integrity design

## Goals

1. Prevent duplicate category results for one assessment.
2. Make category submission idempotent under retries and concurrent requests.
3. Preserve the questionnaire and scoring rules used for each result.
4. Constrain assessment status to supported values and legal transitions.
5. Support PostgreSQL production while remaining compatible with SQLite test fixtures.
6. Provide a safe migration path for existing data.

## Proposed schema changes

### `assessments`

Retain existing columns and formalize:

| Column | Type | Change |
|---|---|---|
| `schema_version` | `VARCHAR(32)` | Normalize default to the application assessment schema version, for example `1.0` |
| `status` | `VARCHAR(20)` | Add a database check constraint for `draft`, `in_progress`, `completed` |
| `completed_at` | `TIMESTAMP NULL` | Must be non-null when status is `completed` in application logic; enforce with a check constraint where supported |
| `user_id` | integer FK | Add index for per-user listing |

Recommended indexes:

```text
ix_assessments_user_id_created_at (user_id, created_at DESC)
ix_assessments_user_id_status (user_id, status)
```

A database-level conditional constraint for `completed_at` is desirable:

```sql
CHECK (
  (status = 'completed' AND completed_at IS NOT NULL)
  OR status <> 'completed'
)
```

If SQLite migration behavior makes this difficult, enforce it in the application and add the constraint in the PostgreSQL migration path, with a follow-up SQLite-compatible migration.

### `assessment_results`

Add or formalize:

| Column | Type | Nullability | Purpose |
|---|---|---:|---|
| `assessment_id` | integer FK | not null | Parent assessment |
| `category` | `VARCHAR(100)` | not null | Stable category key |
| `questions` | JSON | not null | Submitted answer map, retained for compatibility |
| `questionnaire_version` | `VARCHAR(32)` | not null | Version of questionnaire definition |
| `questionnaire_snapshot` | JSON | not null | Exact questions/options/weights used for the result |
| `scoring_version` | `VARCHAR(32)` | not null | Version of scoring algorithm |
| `score` | integer | not null | Normalized 0–100 score |
| `maturity_level` | `VARCHAR(50)` | not null | Calculated maturity |
| `recommendations` | text | nullable | Generated recommendation text |
| `created_at` | timestamp | not null | Last submission/update timestamp |

The result row should be updated in place when the same category is resubmitted. It should not create a second row.

## Required unique constraint

Add the primary integrity constraint:

```sql
CONSTRAINT uq_assessment_results_assessment_category
UNIQUE (assessment_id, category)
```

This constraint must be present in both PostgreSQL and SQLite test schemas.

Also add an index for assessment result lookup:

```text
ix_assessment_results_assessment_category (assessment_id, category)
```

Depending on the database, the unique constraint may already create an equivalent index. Avoid creating a duplicate physical index if the migration engine/database can reuse the unique index.

## Category validation

The application must validate that `category` belongs to the authoritative questionnaire registry before inserting or updating a result.

The database should also constrain category values where practical. A portable database check can be added:

```sql
CHECK (category IN ('data_privacy', 'model_risk', 'ethics', 'compliance'))
```

Because future categories may be added, the preferred long-term approach is application validation plus a versioned category registry rather than a hard-coded database check. If the check is added now, every new category requires a migration.

## Answer validation contract

Database JSON cannot reliably enforce question IDs and option values across PostgreSQL and SQLite. Enforce this at the service boundary before mutation:

1. Resolve the questionnaire by category and requested questionnaire version.
2. Require exactly the known question IDs.
3. Reject unknown question IDs.
4. Require each answer value to be one of the defined option values.
5. Reject missing answers.
6. Normalize all values to integers.
7. Calculate score only from validated answers.

Return HTTP `422` with structured detail for invalid payloads.

Example validation error:

```json
{
  "detail": {
    "code": "invalid_answers",
    "category": "data_privacy",
    "missing_questions": ["privacy_3"],
    "unknown_questions": [],
    "invalid_values": []
  }
}
```

## Questionnaire and scoring snapshots

At submission time, persist:

```json
{
  "questionnaire_version": "1.0",
  "scoring_version": "1.0",
  "questionnaire_snapshot": {
    "category": "data_privacy",
    "title": "Data Privacy Assessment",
    "description": "...",
    "questions": [
      {
        "id": "privacy_1",
        "text": "...",
        "weight": 20,
        "options": [
          {"value": 0, "label": "..."},
          {"value": 10, "label": "..."},
          {"value": 20, "label": "..."}
        ]
      }
    ]
  }
}
```

The snapshot is immutable after the result is written. Resubmitting the same category with the same assessment schema may replace the result snapshot; changing the questionnaire version should require a new assessment or an explicit revision workflow.

The report should use the stored result snapshot and stored scoring version for historical assessments rather than re-reading the current questionnaire registry.

## Status integrity and legal transitions

Supported statuses:

```text
draft -> in_progress -> completed
```

Allowed idempotent transitions:

```text
draft -> draft
in_progress -> in_progress
completed -> completed
```

Disallowed transitions:

```text
completed -> draft
completed -> in_progress
```

The update endpoint must not allow arbitrary status changes from client input. Status should be derived from answer submission and completion logic. If administrative status changes are required later, create a separate privileged workflow.

Application-level transition helper:

```python
ALLOWED_STATUS_TRANSITIONS = {
    "draft": {"draft", "in_progress"},
    "in_progress": {"in_progress", "completed"},
    "completed": {"completed"},
}
```

## Idempotent submission algorithm

`submit_category_answers()` must become safe under client retries:

1. Load the assessment by `assessment_id` and `user_id`.
2. Validate the category and answer map.
3. Resolve the current questionnaire/scoring version.
4. Start a transaction.
5. Select the result row for `(assessment_id, category)`.
6. Update it if present; otherwise insert it.
7. Flush the result.
8. Recalculate completion using the count of distinct valid categories.
9. Set `completed_at` only on the first transition to `completed`.
10. Commit.
11. If a unique-constraint race occurs, roll back, reload the existing result, and apply the update path once.

For PostgreSQL, use an `INSERT ... ON CONFLICT (assessment_id, category) DO UPDATE` path or a SQLAlchemy equivalent. For SQLite tests, a retry-on-integrity-error path is acceptable if the dialect-specific upsert is not introduced immediately.

## Migration plan

### Migration 1 — Preflight and cleanup

Before adding the unique constraint:

1. Identify duplicate result rows:

```sql
SELECT assessment_id, category, COUNT(*)
FROM assessment_results
GROUP BY assessment_id, category
HAVING COUNT(*) > 1;
```

2. For each duplicate group, retain the latest row by `created_at` and merge or archive earlier rows according to the project’s retention decision.
3. Identify unsupported statuses and normalize them to the nearest supported state.
4. Identify completed assessments with null `completed_at` and populate it from the latest result timestamp or migration timestamp, with an audit note.
5. Verify every existing result category maps to a known questionnaire.

The migration must fail closed if duplicates cannot be resolved deterministically.

### Migration 2 — Add columns

Add nullable columns first for compatibility with existing rows:

- `questionnaire_version`
- `questionnaire_snapshot`
- `scoring_version`

Backfill existing rows using the current questionnaire registry and current scoring version. Mark the backfill as a historical reconstruction in migration documentation; it cannot recover questionnaire text that was never stored if the registry has already changed.

### Migration 3 — Add constraints and indexes

After backfill and cleanup:

1. Make the new result columns non-null.
2. Add the unique `(assessment_id, category)` constraint.
3. Add status and completion checks where supported.
4. Add user and result lookup indexes.
5. Add foreign-key enforcement in SQLite test configuration if it is not already enabled.

### Migration 4 — Application cutover

Deploy the service changes that:

- Validate answer maps.
- Populate snapshots and versions.
- Derive status transitions.
- Handle unique-constraint races.
- Read historical report data from stored snapshots.

## Data access/query changes

### Dashboard list

Introduce a lightweight response model that excludes full answer snapshots and detailed result payloads:

```text
AssessmentListResponse:
  id
  title
  description
  schema_version
  status
  created_at
  updated_at
  completed_at
  completed_category_count
```

The current nested `AssessmentResponse` remains for detail and report endpoints.

### Report summary

The report summary should include:

- assessment status
- completed category count
- schema version
- questionnaire/scoring versions represented by each result
- whether the report is complete
- category scores and maturity levels

If a report is incomplete, expose an explicit `is_complete: false` field rather than relying only on status text.

## Phase 4B tests

### Database and service tests

Add tests for:

1. Duplicate category submission updates one row rather than inserting a second row.
2. A database insert of a duplicate `(assessment_id, category)` fails with the expected constraint.
3. Concurrent or simulated race submissions converge to one result row.
4. Missing answer IDs return `422`.
5. Unknown answer IDs return `422`.
6. Invalid option values return `422`.
7. Unsupported category values return `422`.
8. Completed status cannot be reverted through the normal update endpoint.
9. `completed_at` is set exactly once.
10. A partial assessment remains incomplete.
11. A completed assessment has all expected distinct categories.
12. Reports for historical assessments use the stored questionnaire snapshot.
13. Dashboard list responses do not include full answer snapshots.
14. Existing data migration succeeds with duplicates, partial assessments, and legacy null versions.

### Acceptance criteria

- At most one result exists for each `(assessment_id, category)` pair.
- Invalid answer payloads cannot affect scores or completion state.
- Repeating a valid category submission is idempotent.
- Completed assessments cannot regress through normal client APIs.
- Historical reports remain interpretable after questionnaire changes.
- PostgreSQL and SQLite test schemas enforce the same logical invariants.
- All existing backend tests and the Playwright happy path remain green.

---

# Recommended implementation order

1. Add typed API errors and centralized request handling.
2. Add `expireSession()` and login-page session messaging.
3. Add frontend error/retry tests.
4. Add server-side answer validation without changing the schema.
5. Clean existing duplicate/invalid rows in a migration preflight.
6. Add result version/snapshot columns and backfill them.
7. Add the unique constraint and indexes.
8. Make submission idempotent and status transitions explicit.
9. Add concurrency, migration, and historical-report tests.
10. Run the full browser, backend, build, and clean-checkout smoke gates.

# Release gates

Phase 4A is complete when token expiry, network failure, API errors, and retry behavior are covered by unit and browser tests with no stale loading states.

Phase 4B is complete when the database constraints, validation, idempotent writes, version snapshots, migration path, and historical-report behavior are verified on both SQLite test fixtures and PostgreSQL staging.

Production deployment should not proceed until both release gates pass and the migration has been rehearsed against a copy of the production-shaped database.
