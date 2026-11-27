# Phase 5 Implementation Plan

## Product decision

Phase 5 should turn AI Governance Assessor from a questionnaire into a lightweight governance workflow. The questionnaire remains the input mechanism, but it is not the product’s differentiator. The product value is the structured loop around it:

> establish context → answer with guidance and evidence → explain the risk → assign an owner → track remediation → reassess and show change.

The product must consistently describe results as a governance baseline and decision-support output, not legal certification or proof of compliance.

## Scope and priorities

### P0 — make the result actionable

1. **Contextual assessment intake**
   - Capture AI system name, purpose, business owner, technical owner, vendor/model, deployment context, data sensitivity, lifecycle stage, and assessment scope.
   - Show the context on the assessment header and report.
   - Explain why the context is collected and allow an explicit “unknown/not decided” value where appropriate.

2. **Explainable scoring and evidence guidance**
   - For every question, show a short rationale, “what good looks like,” and an optional evidence prompt.
   - Distinguish unanswered, answered-no, answered-yes, not-applicable, and “needs review.”
   - Report score, evidence completeness, assessor confidence, unresolved questions, and limitations separately. Do not collapse them into one pseudo-certification score.

3. **Action cards and basic findings workflow**
   - Convert material gaps into findings/action cards with title, rationale, priority, owner, due date, evidence target, status, reviewer notes, and review date.
   - Support statuses `open`, `in_progress`, `blocked`, `accepted`, and `done`.
   - Let a user create an action from a report finding, edit it, filter it, and mark it complete.

### P1 — make the output useful across frameworks and reviews

4. **Framework crosswalk view**
   - Map each question/finding to a small, curated set of NIST AI RMF functions/categories, EU AI Act concepts, and ISO/IEC 42001-oriented practices.
   - Label the mapping as guidance and explicitly state “not certification.”
   - Allow framework filtering in the report and action list.

5. **Report metadata and review controls**
   - Add assessor, assessment date, review date, assessment scope, questionnaire/scoring versions, evidence completeness, and confidence.
   - Add a simple review/attestation state (`draft`, `under_review`, `reviewed`) without implying legal approval.
   - Preserve the questionnaire and scoring snapshot already introduced in Phase 4.

### P2 — deliberately defer

Defer runtime enforcement, autonomous remediation, broad enterprise integrations, full policy libraries, complex approval/exception/signoff workflows, continuous monitoring, and large-scale evidence repositories. These are valuable only after users demonstrate that the core findings/action loop is used and produces reassessment behavior.

## Proposed data model changes

Add the following tables in a migration, retaining tenant/user ownership checks on every resource:

- `ai_systems`: `id`, `user_id`, `name`, `purpose`, `business_owner`, `technical_owner`, `vendor_model`, `deployment_context`, `data_sensitivity`, `lifecycle_status`, timestamps.
- `assessment_contexts`: `id`, `assessment_id`, `ai_system_id`, `scope`, `assessor_name`, `confidence`, `evidence_completeness`, `review_state`, `review_date`, timestamps.
- `question_guidance`: versioned seed/config data keyed by `(questionnaire_version, question_id)` with `rationale`, `good_practice`, `evidence_prompt`, and `framework_refs` JSON.
- `findings`: `id`, `assessment_id`, `assessment_result_id` nullable, `title`, `description`, `priority`, `owner`, `due_date`, `evidence_target`, `status`, `reviewer_notes`, `review_date`, timestamps.
- `finding_framework_refs`: `finding_id`, `framework`, `reference_code`, `mapping_note`.

Use unique constraints appropriate to the workflow, especially one active context per assessment and stable question identifiers within a questionnaire version. Add indexes for `(user_id, status)`, `(assessment_id, status)`, and due-date filtering. Store timestamps in UTC.

## API changes

Introduce typed endpoints under the existing authenticated API boundary:

- `POST /ai-systems`, `GET /ai-systems`, `GET /ai-systems/{id}`, `PATCH /ai-systems/{id}`.
- `GET /assessments/{id}/context`, `PUT /assessments/{id}/context`.
- Extend questionnaire responses with guidance and evidence fields without breaking the Phase 4 answer contract.
- `GET /assessments/{id}/findings`, `POST /assessments/{id}/findings`, `PATCH /findings/{id}`.
- `POST /assessments/{id}/findings/from-gap` to create an action from a material gap.
- `GET /assessments/{id}/crosswalk?framework=nist_ai_rmf|eu_ai_act|iso_42001`.
- Extend summary/report responses with `evidence_completeness`, `confidence`, `unresolved_questions`, `limitations`, context metadata, and prioritized findings.

Return structured 4xx errors, enforce ownership on every read/write/export path, and keep response schemas versioned. Do not expose credentials or private evidence in shareable URLs during Phase 5.

## Frontend changes

1. Add a short intake step before the questionnaire with a visible step indicator, saved draft state, and plain-language explanation.
2. Add progressive disclosure to questions: rationale and evidence help are collapsed by default but keyboard accessible.
3. Replace score-only recommendation text with prioritized finding cards and a clear next action.
4. Add report sections for context, score interpretation, evidence completeness, unresolved items, findings, and framework crosswalk.
5. Add an action list with filters for status, priority, owner, framework, and due date.
6. Preserve answer state and recovery behavior already covered by Phase 4.
7. Keep responsive keyboard operation, clear focus states, accessible status/error announcements, and no color-only risk indication.

## Delivery sequence

### Sprint 1: context and data foundations

- Finalize domain/API contracts and an ADR for the non-certification boundary.
- Add migrations, ORM models, ownership tests, and seed guidance/crosswalk data.
- Build intake UI and context persistence.
- Add report context metadata.

### Sprint 2: explainability and findings

- Add question guidance and evidence prompts.
- Define material-gap rules and create findings from gaps.
- Build finding CRUD, action cards, filters, and status transitions.
- Add report findings section.

### Sprint 3: crosswalk and review quality

- Add curated framework crosswalk endpoint and UI.
- Add confidence/evidence completeness/unresolved-question calculations.
- Add review metadata and `under_review`/`reviewed` state.
- Add export coverage for context, findings, and limitations.

### Sprint 4: validation and product learning

- Run moderated usability sessions with an executive, practitioner, privacy/risk user, and business owner.
- Measure completion, time to first finding, owner assignment, evidence attachment, action completion, and reassessment.
- Remove or simplify features that increase cognitive load without improving action creation.

## Acceptance criteria

- A user can create an AI-system context and associate it with an assessment without leaving the workflow.
- A user can understand why each high-impact question matters and what evidence could support an answer.
- A completed assessment reports score, evidence completeness, confidence, unresolved questions, limitations, and version metadata separately.
- At least one material gap can be converted into an action with owner, priority, due date, evidence target, and status.
- Findings and actions are isolated across users and protected by backend authorization tests.
- Framework mappings are visible, curated, and labeled as guidance rather than certification.
- Refresh, token expiry, network failure, duplicate submit, keyboard, and mobile scenarios remain passing.
- CSV/PDF exports include context, limitations, and findings without exposing another user’s data.
- No Phase 5 feature claims legal compliance, certification, or autonomous risk reduction.

## Validation checklist

Run after each vertical slice:

```bash
cd /home/ubuntu/AI_Governance_Assessor_v2.1
pytest -q
cd frontend
npm run test
npm run lint
npm run build
BASE_URL=http://127.0.0.1:5173/ E2E_EVIDENCE=1 npm run test:e2e
cd ..
alembic upgrade head --sql

git diff --check
```

Add API tests for ownership, invalid transitions, missing/unknown question handling, duplicate findings, invalid due dates, and framework filters. Add frontend tests for context validation, guidance disclosure, finding creation, filters, report labels, and recovery. Keep a temporary SQLite backfill smoke test and a duplicate preflight test in CI or release evidence.

## Success measures

The primary Phase 5 outcome is not more questions. It is measurable movement from assessment to action:

- percentage of completed assessments producing at least one owned finding;
- median time from completion to first owner assignment;
- evidence completeness at first review and reassessment;
- percentage of findings reaching `done` or `accepted` with reviewer notes;
- reassessment rate and change in unresolved material gaps;
- user-reported confidence in understanding both the result and its limitations.
