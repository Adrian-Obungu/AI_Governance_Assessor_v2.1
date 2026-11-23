# Project outcomes

## Reliability milestone: ownership and local startup diagnostics

- [x] The backend test suite includes two synthetic users and verifies that a user cannot list, read, update, answer, summarize, export, or delete another user’s assessment.
- [x] Windows contributors have a repository-local Docker preflight at `scripts/preflight.ps1` that distinguishes a missing Docker CLI, an unavailable Docker Desktop Linux engine, invalid Compose configuration, occupied ports, and service readiness problems.
- [ ] The Windows Docker preflight is run against the local machine and its output is recorded in the release evidence.

## Core user journey

- [ ] A synthetic browser journey registers a user, creates an assessment, completes all questionnaire categories, reviews the report, exports CSV/PDF, and signs out.
- [ ] The frontend test suite covers login form behavior, API loading/error states, assessment progress, report rendering, and recovery from an expired token.
- [ ] The project has a repeatable clean-checkout smoke procedure that validates frontend HTTP delivery, API proxying, authentication, assessment creation, answer submission, summary rendering, and exports.

## Governance trust model

- [ ] Cross-user authorization coverage includes every future assessment, evidence, finding, review, and export endpoint.
- [ ] Assessment versions preserve the questionnaire and scoring interpretation used when an assessment was completed.
- [ ] Findings link a conclusion to evidence, priority, owner, due date, status, and reviewer notes.
- [ ] Reports distinguish calculated score, evidence completeness, assessor confidence, and unresolved questions.

## Engineering stewardship

- [ ] Architecture Decision Records document authentication storage, PostgreSQL/Docker boundaries, assessment versioning, PWA caching, and the non-certification product boundary.
- [ ] Security documentation distinguishes implemented controls from recommended deployment controls and matches the PostgreSQL production path.
- [ ] CI includes secret/database artifact checks and a production-image or disposable-Compose smoke gate where the runner supports it.
