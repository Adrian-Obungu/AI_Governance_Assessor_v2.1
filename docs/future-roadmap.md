# AI Governance Assessor: future progression roadmap

## Current position

The project has crossed an important threshold: it is no longer primarily a broken local Docker exercise. The repository now has a functioning FastAPI/PostgreSQL/React/Vite stack, migrations, a CLI, automated backend and frontend checks, a Docker runbook, threat-model documentation, and a styled login experience. The most recent Windows evidence confirms that the frontend and API rendered correctly after clearing the stale PWA cache.

The current Docker error is environmental rather than application-level. PowerShell reports that the Docker Desktop Linux engine named pipe does not exist. That means Docker Desktop is closed, still starting, switched to Windows containers, or otherwise not exposing its Linux engine. It is not evidence of a new repository failure. The operator procedure should eventually include a preflight that checks `docker version` before attempting Compose commands and tells the user to start Docker Desktop or switch to Linux containers.

The repository is now at the “validated prototype” stage. It should not yet be described as a production-ready governance platform. Its strongest value is as a demonstrable, self-hostable workflow for turning governance questions into structured answers, category scores, recommendations, and exports.

## What the attached book contributes

Samuel Bastiat’s *LLM-Assisted Software Design* is most useful here as a practice framework. Its central argument is that an LLM should expand human reasoning, not replace engineering judgment. The book describes a recurring movement through exploration, framing, refactoring, documentation, validation, and co-design. It also presents the LLM as a mirror, critic, tutor, and shared thinking surface rather than an autonomous production decision-maker.

That maps directly onto this project. Exploration means learning the governance domain and the target users. Framing means converting broad goals such as “assess AI risk” into explicit actors, evidence, decisions, and acceptance criteria. Refactoring means examining the existing implementation before adding new features. Validation means testing authorization, scoring, exports, accessibility, and Docker startup with synthetic data. Documentation means keeping the threat model, limitations, runbook, API contract, and architecture decisions aligned. Co-design means using the model to generate alternatives while the human remains responsible for choosing and testing them.

The book’s most actionable practice is its living usage map. For each substantial change, record the current situation, the human decision required, the LLM posture being used, the artifact produced, and the validation evidence. A small `docs/decision-log.md` or ADR collection would make this project show not only what was built, but how disciplined AI-assisted engineering was used to build it.

The book also warns against cognitive overload, the generative tunnel effect, the illusion of velocity, decision bias, and blind automation. Those warnings should become product requirements. The assessor should reduce unnecessary questions, expose why a question is being asked, separate evidence from interpretation, and never imply that a generated score is a certification or an objective truth.

## Repository findings that should guide the next stage

The architecture is understandable and appropriately sized for the current stage. The backend is divided into authentication, assessments, audit logging, database models, and reporting. The frontend has separate pages for login, dashboard, assessment, and report. Docker provides PostgreSQL, a backend health check, and an Nginx-served frontend. CI runs Black, Ruff, backend tests, CLI tests, and a frontend production build.

The quality gates are still weighted toward code correctness rather than user-journey correctness. Backend tests cover root and health endpoints, account creation, duplicate signup, login, password reset request, assessment creation and listing, questionnaires, answer submission, summaries, CSV export, and unauthenticated access. The frontend suite currently focuses on protected-route behavior. There is not yet a browser-level test proving registration or login, assessment completion, report rendering, export behavior, or recovery from API failures.

The security documentation needs a claims audit before the project is presented as a serious governance product. The documentation describes rate limiting, account lockout, audit logging, immutable results, and security-event tracking. Some of those controls appear in the implementation, but the repository should distinguish what is implemented, what is partially implemented, and what remains a deployment responsibility. The security guide also describes SQLite in its database section while Docker uses PostgreSQL. That is a documentation inconsistency worth correcting.

The current data model is primarily user-and-assessment oriented. To become valuable beyond a questionnaire demo, the application will need explicit concepts for an AI system, organization or business unit, assessment scope, assessment version, evidence item, control or question, finding, remediation action, owner, due date, status, and review history. These concepts should be introduced only after the core workflow and authorization boundaries are tested; premature domain expansion would increase complexity without increasing trust.

The repository contains an ignored local `test.db`, but it is not tracked by Git. That is acceptable for local tests, provided the file remains ignored and CI continues creating an isolated test database. The repository should add a CI or pre-commit check that fails if database files, `.env` files, exports, or generated reports are accidentally added.

## Product direction

The strongest product direction is an evidence-first AI governance workbench rather than a generic maturity quiz. Its differentiator would be the connection between a question, the evidence supplied, the risk or control interpretation, the accountable owner, and the next action. Scores should summarize the evidence state; they should not replace it.

The information architecture should eventually align with NIST AI RMF’s Govern, Map, Measure, and Manage functions. NIST describes the Playbook as a voluntary companion containing suggested actions, references, and guidance for achieving outcomes across those four functions.[1] The current categories—data privacy, model risk, ethics, and compliance—can remain as domain lenses, but the user journey and report should show how each answer contributes to governance, mapping, measurement, or management.

ISO/IEC 42001 should be treated as a management-system reference rather than merely another checklist. ISO describes it as a standard for establishing, implementing, maintaining, and continually improving an AI management system, including policies, objectives, processes, traceability, transparency, and reliability.[2] This suggests a future feature set around policy ownership, recurring reviews, corrective actions, evidence retention, and continual improvement. It does not mean the application should claim ISO certification or reproduce the standard’s copyrighted text.

The threat model should evolve with the product. OWASP’s 2025 GenAI guidance highlights prompt injection, sensitive information disclosure, supply-chain risk, data and model poisoning, improper output handling, excessive agency, system-prompt leakage, vector and embedding weaknesses, misinformation, and unbounded consumption.[3] The current application does not yet use an LLM in its runtime assessment path, so these risks should be documented as future-scope risks rather than presented as current controls. If an AI recommendation feature is later added, it should begin as a non-authoritative drafting assistant with bounded permissions, explicit provenance, human review, and no ability to silently alter assessment records.

## Recommended sequence

### Stage 1: prove the workflow

First, create one repeatable synthetic end-to-end journey. It should register a test user, create an assessment, answer every section, display progress, calculate a summary, export CSV and PDF, and log out. Run it against Docker Compose on Windows and against the test configuration in CI. Add a browser-level test for this path. This stage converts “the stack starts” into “a user can complete the product’s stated use case.”

The same stage should add cross-user authorization tests. Create two synthetic users and confirm that one cannot read, change, or export the other’s assessment. Test reset-token single use and expiry. Verify that errors do not reveal whether a private account exists. These are higher-value tests than adding more visual polish.

### Stage 2: make the assessment cognitively manageable

Move from displaying a full category questionnaire to a guided, resumable workflow. Show one question or one small related group at a time. Explain the purpose of each section in plain language. Add autosave or explicit draft-save semantics, a review screen, a completion summary, and a clear distinction between unanswered, not applicable, unknown, and supported by evidence.

Introduce branching only where it removes irrelevant questions. Do not use branching to hide material risk. Record the questionnaire version so future changes do not rewrite the meaning of old assessments. This is where the book’s framing and counterexample patterns are useful: for each question, ask what decision it supports, what evidence would change the answer, and what misleading answer a user might give.

### Stage 3: turn scores into managed findings

Replace the report’s score-only emphasis with findings and actions. Each finding should have a plain-language title, affected domain, evidence gap, impact explanation, priority, suggested owner, due date, status, and reviewer notes. Preserve the raw answer and scoring rule so a reviewer can understand how the conclusion was produced.

Add an assessment review state such as draft, in review, accepted, needs remediation, and archived. Separate the assessor’s confidence from the system’s calculated score. A high score with weak evidence should be visibly different from a high score backed by strong evidence.

### Stage 4: add framework mapping and version control

Add a framework mapping layer without copying protected standards text into the repository. A mapping record can contain a framework name, reference identifier, short internal description, source URL, version, and the project’s interpretation. Start with NIST AI RMF and a small, explicitly curated crosswalk to the project’s categories. Add ISO/IEC 42001 as a management-system lens after the first mapping is stable.

Create ADRs for architectural decisions such as PostgreSQL in Docker, the React Router boundary, PWA caching policy, authentication-token storage, assessment versioning, and the decision not to make an automated compliance claim. ADR guidance defines an architecture decision as a justified choice addressing an architecturally significant requirement and recommends retaining rationale, trade-offs, and consequences in a decision log.[4]

### Stage 5: harden deployment and operating trust

Add a Docker preflight and more useful diagnostics. The preflight should check Docker availability, Docker Desktop Linux-engine availability, Compose configuration, required `.env` values, port conflicts, and service health. The runbook should distinguish “Docker is unavailable,” “the image failed to build,” “the container is unhealthy,” “the API is unhealthy,” and “the browser has stale site data.”

Add dependency scanning, container image scanning, secret scanning, database backup and restore exercises, structured audit events, and a documented retention policy. Add a CI job that builds the production image and runs a smoke test against a disposable Compose stack where the GitHub runner permits it. Keep the existing local Windows Docker smoke test as evidence in the release checklist, not as a claim that the sandbox tested Docker.

## Progress measures

Use a small set of project-level measures instead of maximizing activity. Track the percentage of critical user journeys covered by automated tests, the time required for a new user to complete a synthetic assessment, the number of unanswered or ambiguous questions discovered during user review, the percentage of findings with evidence and owners, and the number of releases that can be rebuilt from a clean checkout.

For engineering delivery, DORA recommends five performance metrics: change lead time, deployment frequency, failed deployment recovery time, change fail rate, and deployment rework rate.[5] These should be used as a learning baseline, not as individual performance targets. For this project, the most useful first signals are clean-checkout rebuild time, time from commit to a tested local release, and recovery time from a broken frontend deployment.

## Books and publications worth sourcing

Start with a small reading sequence rather than collecting everything at once. *Domain-Driven Design: Tackling Complexity in the Heart of Software* by Eric Evans is useful when the application moves from questionnaire screens to concepts such as systems, evidence, findings, owners, and review states. *Designing Data-Intensive Applications* by Martin Kleppmann becomes valuable when assessment history, exports, audit logs, and reliable versioning create data-consistency questions. *Architecture Patterns with Python* by Harry Percival and Bob Gregory is a practical bridge between the current FastAPI codebase and clearer domain boundaries.

For delivery and organization, *Team Topologies* by Matthew Skelton and Manuel Pais provides a model for team types and interaction patterns that helps explain ownership boundaries as the project grows.[6] *Accelerate* by Nicole Forsgren, Jez Humble, and Gene Kim pairs well with DORA’s research when you want to measure whether engineering practices are improving delivery rather than merely increasing activity. *Modern Software Engineering* by David Farley is a useful companion for feedback, small batches, automation, and reducing the cost of change.

For security and AI governance, source the official NIST AI RMF 1.0 and Playbook first, then ISO/IEC 42001 through an authorized copy or preview, ISO/IEC 23894 for AI risk-management guidance, and the current OWASP GenAI/LLM Top 10. Do not rely on unsourced summaries of standards when deciding what the product claims to implement. The project should store links, version identifiers, and internal interpretations rather than reproducing copyrighted standard text.

The attached Bastiat book itself is suitable as the working method for our collaboration. Its public project and updates are listed as `s31db/llm-dev-books` on GitHub and on Leanpub. The sections most relevant to this repository are the situation typology in pages 47–50, the personal prompt-library practice in pages 51–52, the augmented agility and human-control guidance in pages 59–62, and the workshop methods beginning on page 63.

## Immediate next decision

The next implementation should not add an AI chatbot. It should add the synthetic browser journey, cross-user authorization tests, assessment versioning, and the Docker Desktop preflight. Those changes will tell us whether the product is reliable enough to deserve richer governance features. Once those gates pass, the next product decision is whether the primary user is an internal compliance assessor, an engineering team preparing evidence, or a consultant managing multiple client assessments. That choice determines the domain model, pricing potential, and the public project’s strongest market story.

## References

[1]: https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook "NIST AI RMF Playbook"
[2]: https://www.iso.org/standard/42001 "ISO/IEC 42001:2023 Information technology — Artificial intelligence — Management system"
[3]: https://genai.owasp.org/llm-top-10/ "OWASP Top 10 for LLMs and GenAI Applications"
[4]: https://adr.github.io/ "Architectural Decision Records"
[5]: https://dora.dev/guides/dora-metrics/ "DORA’s software delivery performance metrics"
[6]: https://teamtopologies.com/book "Team Topologies"
