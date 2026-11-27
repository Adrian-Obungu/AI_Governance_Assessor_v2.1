# Project outcomes

## Reliability milestone: ownership and local startup diagnostics

- [x] The backend test suite includes two synthetic users and verifies that a user cannot list, read, update, answer, summarize, export, or delete another user’s assessment.
- [x] Windows contributors have a repository-local Docker preflight at `scripts/preflight.ps1` that distinguishes a missing Docker CLI, an unavailable Docker Desktop Linux engine, invalid Compose configuration, occupied ports, and service readiness problems.
- [ ] The Windows Docker preflight is run against the local machine and its output is recorded in the release evidence.

## Core user journey

- [x] A repeatable PowerShell API journey covers synthetic signup/login, assessment creation, all questionnaire categories, summary, CSV/PDF exports, and unauthenticated rejection.
- [x] A synthetic browser journey registers a user, creates an assessment, completes all questionnaire categories, reviews the report, exports CSV/PDF, and signs out.
- [ ] The frontend test suite covers login form behavior, API loading/error states, assessment progress, report rendering, and recovery from an expired token.
- [ ] The project has a repeatable clean-checkout smoke procedure that validates frontend HTTP delivery, API proxying, authentication, assessment creation, answer submission, summary rendering, and exports.

## Governance trust model

- [ ] Cross-user authorization coverage includes every future assessment, evidence, finding, review, and export endpoint.
- [ ] Assessment versions preserve the questionnaire and scoring interpretation used when an assessment was completed.
- [ ] Findings link a conclusion to evidence, priority, owner, due date, status, and reviewer notes.
- [ ] Reports distinguish calculated score, evidence completeness, assessor confidence, and unresolved questions.

## Phase 5A: AI-system inventory and contextual intake

- [x] An authenticated user can create an AI-system record with a name, purpose, department, business owner, provider/vendor, lifecycle stage, geographies, data categories, affected groups, and review date.
- [x] The inventory API validates field lengths and lifecycle values, scopes list/read/update operations to the authenticated owner, and returns `404` for another user’s record.
- [x] The inventory database migration is compatible with SQLite development and PostgreSQL deployment and includes ownership and review indexes; live SQLite migration validation reached revision `0003`.
- [x] The frontend offers a mobile-friendly inventory page with a short guided form, plain-language explanations, a clear next action, preserved form state after validation errors, and visible lifecycle/review information.
- [x] The dashboard links users to the inventory before they begin a questionnaire, so the product starts with a system context rather than a score alone.
- [x] The implementation includes backend regression tests and frontend/API contract coverage: backend `23 passed`, frontend `15 passed`, lint passed, and production build passed.

## Engineering stewardship
## Phase 5F: Operational signals and incident/feedback intake

- [x] An authenticated user can record an incident, user feedback item, or material change against an owned AI system with a summary, severity, source, discovered date, owner, status, response/action, and reviewer notes.
- [x] A signal may optionally link to an owned finding or review, and the API rejects inaccessible or context-mismatched links with `404`.
- [x] Signal type, severity, and workflow status are validated; list filters support AI system, type, severity, and status; records are ownership-scoped.
- [x] The migration is SQLite-development and PostgreSQL-deployment compatible and preserves existing records; disposable SQLite upgrade reaches revision `0008`.
- [x] The frontend provides a mobile-friendly signals workspace with one clear intake form, filters, visible severity/status, and a human-controlled close action.
- [x] Signals are operational governance records only: the feature does not claim legal incident classification, certification, objective safety, automated triage, or autonomous high-impact decisions.
- [x] Backend regression tests and frontend/API contract coverage pass, together with Black, Ruff, ESLint, TypeScript/Vite production build, `git diff --check`, and migration validation.

## Phase 5G: Consolidated governance activity view

- [x] An authenticated user can view a derived timeline combining their AI-system inventory, linked assessments, evidence records, findings, human reviews, and operational signals.
- [x] Activity events expose source type, source identifier, AI-system context, occurred date/time, title, summary, and relevant status, priority, or severity without duplicating records in a new database table.
- [x] The activity API is read-only, ownership-scoped, supports AI-system and source-type filters, and returns no events for another user’s system.
- [x] The frontend provides a low-cognitive-load timeline with a system filter, source filter, clear event labels, and an explanation that it is a derived activity view.
- [x] The view preserves human-led governance boundaries and does not infer legal conclusions, objective safety, certification, or automated decisions.
- [x] Backend and frontend contract tests, formatting, lint, production build, and `git diff --check` pass.

## Phase 5B: Assessment context linkage

- [x] An assessment may optionally reference one AI-system inventory record while existing unlinked assessments remain valid.
- [x] The backend validates that the selected inventory record belongs to the authenticated user and returns `404` for cross-user linkage attempts.
- [x] Assessment responses expose the linked inventory identifier and basic system context without changing questionnaire scoring behavior.
- [x] The migration is SQLite-development and PostgreSQL-deployment compatible and preserves existing assessment rows; disposable SQLite upgrade reached revision `0004`.
- [x] The dashboard lets a user choose an inventory system when starting an assessment, with a clear “continue without linking” option.
- [x] Backend regression tests and frontend/API contract coverage pass: backend `27 passed`, frontend `16 passed`, lint passed, and production build passed.

## Phase 5C: Evidence records without file uploads

- [x] An authenticated user can create an evidence record with title, description, type, source/location, owner, collection date, review date, status, reviewer notes, AI-system link, and optional assessment link.
- [x] Evidence type and status values are validated, review dates are visible, and records are restricted to the authenticated owner.
- [x] The API rejects links to another user’s AI system or assessment with `404` and supports list filters for AI system and status.
- [x] The migration is SQLite-development and PostgreSQL-deployment compatible and preserves existing records; disposable SQLite upgrade reached revision `0005`.
- [x] The frontend provides a low-cognitive-load evidence page with a metadata-only form, status/review visibility, and filters by system and status.
- [x] The implementation explicitly excludes file uploads, OCR, ML classification, verified-proof claims, and sensitive hosted document storage.
- [x] Backend regression tests and frontend/API contract coverage pass: backend `30 passed`, frontend `18 passed`, lint passed, and production build passed.

## Phase 5D: Findings and owned remediation actions

- [x] An authenticated user can create a finding linked to an owned AI system, supporting evidence record, and optional assessment, with a conclusion, priority, accountable owner, remediation action, due date, status, and reviewer notes.
- [x] Finding priority and workflow status values are validated, due dates and remediation actions are visible, and records are restricted to the authenticated owner.
- [x] The API rejects inaccessible or context-mismatched system, evidence, and assessment links with `404` and supports list filters for system, priority, and status.
- [x] The migration is SQLite-development and PostgreSQL-deployment compatible and preserves existing records; disposable SQLite upgrade reached revision `0006`.
- [x] The frontend provides a low-cognitive-load findings page that turns an evidence-backed gap into one owned, reviewable next action.
- [x] Findings remain working governance records and do not claim legal conclusions, certification, objective safety, or automated risk decisions.
- [x] Backend regression tests and frontend/API contract coverage pass: backend `33 passed`, frontend `20 passed`, lint passed, and production build passed.

## Phase 5E: Human review and reassessment workflow

- [x] An authenticated user can record a review for an owned AI system with reviewer, review date, human decision, material-change flag, change summary, next review date, reviewer notes, and optional reviewed assessment.
- [x] A review can optionally link a reassessment assessment from the same AI-system context, and review decisions are validated and owner-scoped.
- [x] The API rejects inaccessible or context-mismatched system, assessment, and reassessment links with `404` and supports filters for system, decision, and material change.
- [x] The migration is SQLite-development and PostgreSQL-deployment compatible and preserves existing records; disposable SQLite upgrade reached revision `0007`.
- [x] The frontend provides a low-cognitive-load review page that makes the human decision, material change, reassessment link, and next review date visible.
- [x] The workflow records human review context only and does not automate legal, certification, safety, or high-impact decisions.
- [x] Backend regression tests and frontend/API contract coverage pass: backend `36 passed`, frontend `22 passed`, lint passed, and production build passed.

- [ ] Architecture Decision Records document authentication storage, PostgreSQL/Docker boundaries, assessment versioning, PWA caching, and the non-certification product boundary.
- [ ] Security documentation distinguishes implemented controls from recommended deployment controls and matches the PostgreSQL production path.
- [ ] CI includes secret/database artifact checks and a production-image or disposable-Compose smoke gate where the runner supports it.
