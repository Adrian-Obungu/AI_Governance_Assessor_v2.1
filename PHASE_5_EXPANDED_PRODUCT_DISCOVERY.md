# Phase 5 Expanded Product Discovery

## The immediate correction to product positioning

The current application should not yet claim that it helps teams establish a “defensible governance baseline” unless the product actually captures system context, preserves evidence, assigns owners, records decisions, and supports review. At present, the most accurate description is narrower:

> **AI Governance Assessor helps teams organize an initial AI-governance self-assessment and identify questions that may require follow-up.**

Once the platform has inventory, evidence, ownership, review history, and action tracking, a stronger but still careful description becomes appropriate:

> **AI Governance Assessor helps teams document AI use cases, organize governance evidence, identify follow-up work, and track review decisions over time.**

The words “helps,” “organize,” “identify,” and “track” are intentional. They describe software assistance rather than legal certification, objective safety, regulatory approval, or a guarantee that risk has been reduced.

## The product opportunity beyond a questionnaire

The shared problem across the researched departments and sectors is not simply that people need better questions. It is that organizations struggle to maintain an accurate AI-use inventory, collect trustworthy evidence, decide who is accountable, convert gaps into work, respond to changes and incidents, and demonstrate what was decided and why.

The product should therefore become a governance operations workspace around the assessment. The common workflow is:

1. **Inventory:** What AI system or use case exists, who provides it, what it does, what data it uses, who owns it, and who may be affected?
2. **Context:** Where is it deployed, what is its lifecycle stage, what human decisions surround it, and what would change the risk or review requirements?
3. **Assessment:** What controls and questions apply to this particular context?
4. **Evidence:** Which policies, contracts, test results, system descriptions, approvals, training records, incidents, or monitoring records support the answers?
5. **Decision:** What remains uncertain, what needs review, and which human role is accountable for the decision?
6. **Action:** What finding, task, owner, priority, due date, evidence target, and approval state should be created?
7. **Operation:** What changes, complaints, incidents, review dates, or evidence expirations should reopen the work?
8. **Reassessment:** What changed, what improved, what remains unresolved, and what should happen next?

This is materially more valuable than a form because it creates continuity between an initial answer and the work that follows it.

## Cross-sector opportunities

For product and engineering teams, the platform can connect an AI-use inventory to model or vendor versions, data sources, evaluation results, human-oversight plans, release changes, incidents, and engineering tasks. The useful value is not deciding whether a system is safe. It is ensuring that the right evidence and reviewers are involved before and after change.

For legal, privacy, risk, and compliance teams, the platform can organize impact-assessment inputs, contracts, data-flow descriptions, policies, exceptions, approvals, evidence freshness, and review triggers. It should help people prepare and manage governance work, but must not present generated output as legal advice or a compliance conclusion.

For HR and internal operations, the product can support AI-use records, employee feedback, vendor reviews, accessibility concerns, worker consultation, training, and escalation. It must explicitly avoid ranking, rejecting, hiring, firing, promoting, disciplining, or performance-scoring people through ML.

For sales, marketing, and customer-success teams, the value is a controlled record of customer-facing AI uses, approved descriptions, data handling, vendor information, campaign or support review, escalation paths, and source-linked customer responses. The platform should not automatically publish content, promise compliance, or make decisions about customers.

In financial services, insurance, healthcare, education, and government, the same common workflow applies, but the contextual fields and review roles differ. Financial teams may need customer-impact, model-risk, monitoring, and redress fields. Healthcare teams may need intended use, clinical workflow, validation, patient-safety, quality, and incident fields. Education teams may need learner age, safeguarding, assessment integrity, staff guidance, and parent/learner communication fields. Public-sector teams may need public benefit, affected populations, procurement, equality or rights review, frontline oversight, and recourse fields.

The product should not build eight unrelated products. It should build a common governance data model with configurable intake fields, roles, evidence templates, action types, and review triggers.

## ML features that are worth considering

ML is applicable, but only after the deterministic workflow foundation exists. The best first features assist with document-heavy and language-heavy work without changing official records or making high-impact decisions.

### 1. Evidence extraction and control matching

Given an uploaded policy, contract, system description, model card, test report, or incident record, the system could extract candidate fields such as system name, purpose, vendor, data categories, owner, review date, and safeguards. It could suggest that a document may support a particular control.

Every extracted field should show the source passage, confidence or uncertainty, document version, and an accept/edit/reject control. The system must never silently mark a control satisfied.

### 2. Grounded gap-to-action drafting

Given a confirmed gap and a selected internal playbook, the system could draft a finding, evidence request, follow-up questions, and owner-specific task description. The output should link back to the confirmed answer and source material. A named owner must edit and approve the output before it becomes an assigned task or external communication.

### 3. Change, incident, and recurring-theme triage

The system could compare assessment versions, vendor terms, model descriptions, evidence dates, and incident narratives. It could flag possible material changes, duplicate records, stale evidence, or recurring themes.

This output is only an investigation lead. It must not claim that a change is legally material, that an incident proves harm, that bias occurred, or that a system should be shut down. Human reviewers decide what follows.

### 4. Permissioned governance search

A retrieval assistant could answer questions such as “Which systems have no current privacy review?” or “Which high-priority findings are overdue?” using the organization’s own permissioned records and approved guidance. Each answer must cite the records used and return “not found” or “needs review” rather than inventing an answer.

This should be a search and workflow interface, not an authoritative legal adviser.

## ML features to explicitly reject

The platform should not use ML to make or recommend employment, credit, insurance, admissions, grading, eligibility, benefits, healthcare, public-service, disciplinary, or deployment decisions. It should not infer protected traits, health, emotion, personality, credibility, or intent from text, voice, video, or behavior.

It should not produce a supposedly objective compliance score, declare certification, determine residual risk acceptance, decide breach-notification duties, or claim that a self-assessment proves legal compliance. Those boundaries are important for both safety and product credibility.

## Recommended product sequence

**Discovery first:** interview governance owners and operational contributors from three contrasting settings, such as a regulated business, an education or public-sector organization, and an ordinary SME. Observe how a real assessment becomes a decision, task, evidence request, or review. The goal is to find the repeated operational pain rather than assuming it.

**Deterministic operating layer next:** build the AI-system/use-case inventory, contextual intake, evidence register, version history, owner routing, action backlog, approval states, review calendar, incident/feedback log, permissions, audit history, and exports. This is the primary product differentiation.

**ML in shadow mode afterward:** test evidence extraction, control matching, gap-to-action drafting, and change/incident triage against customer-approved, preferably de-identified records. Measure citation accuracy, omission rate, hallucination rate, low-confidence escalation, reviewer acceptance/edit rate, prompt-injection resistance, and data leakage. Do not permit autonomous state changes during this stage.

**Controlled workflow pilots after that:** enable reviewed suggestions for a small number of customers and integrate with one issue tracker and one document source. Compare assisted and unassisted time, corrections, missed evidence, owner assignment, and completed remediation. Expand only if the evidence shows improvement without unacceptable errors or trust problems.

## Source basis

The direction is consistent with the lifecycle and governance principles in the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) and [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/), the proportionate assurance approach described in the [UK Introduction to AI Assurance](https://www.gov.uk/government/publications/introduction-to-ai-assurance/introduction-to-ai-assurance), and the management-system orientation of [ISO/IEC 42001](https://www.iso.org/standard/42001).

The need for careful data handling and review is also reflected in [ICO AI and data protection guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/ai-and-data-protection-risk-toolkit/), [EEOC AI and ADA resources](https://www.eeoc.gov/eeoc/disability-related-resources/artificial-intelligence-and-ada), the [CFPB complex-algorithm adverse-action guidance](https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/), [WHO Ethics and Governance of AI for Health](https://www.who.int/publications/i/item/9789240029200), [UNESCO Guidance for Generative AI in Education](https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research), and the [UK Government AI Playbook](https://www.gov.uk/government/publications/ai-playbook-for-the-government/artificial-intelligence-playbook-for-the-government-html).
