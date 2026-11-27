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

- [ ] Architecture Decision Records document authentication storage, PostgreSQL/Docker boundaries, assessment versioning, PWA caching, and the non-certification product boundary.
- [ ] Security documentation distinguishes implemented controls from recommended deployment controls and matches the PostgreSQL production path.
- [ ] CI includes secret/database artifact checks and a production-image or disposable-Compose smoke gate where the runner supports it.
