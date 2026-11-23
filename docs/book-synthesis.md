# Four-book synthesis for the AI Governance Assessor

## Why these four books are enough to start

The four uploaded books cover four different layers of the same problem. *Modern Software Engineering* by David Farley focuses on how to learn, design, test, and manage complexity. *Accelerate* by Nicole Forsgren, Jez Humble, and Gene Kim focuses on delivery performance, technical practices, culture, and sustainable improvement. *Team Topologies* by Matthew Skelton and Manuel Pais focuses on cognitive load, team boundaries, and fast flow. *LLM-Assisted Software Design* by Samuel Bastiat focuses on how humans can use language models as structured design partners without surrendering judgment.

Together they suggest that the next stage of this project is not “add more features.” It is to make the product easier to understand, safer to change, faster to validate, and clearer about who owns each decision.

## The combined model

Farley’s central contribution is an engineering loop: work in small increments, obtain feedback early, measure reality, run experiments, and manage complexity through modularity, cohesion, separation of concerns, information hiding, and controlled coupling. For this repository, the practical implication is to make every feature small enough to test through a synthetic user journey and every architectural change small enough to reverse.

*Accelerate* adds an outcome lens. Delivery quality should be observed through change lead time, deployment frequency, failed-deployment recovery time, change fail rate, and deployment rework rate. The project should not turn these into vanity targets. It should use them to identify friction: how long a clean checkout takes to rebuild, how quickly a broken image can be recovered, and whether each release can be validated without manual guesswork.

*Team Topologies* explains why cognitive load matters even for a solo developer. The repository currently contains backend, frontend, CLI, Docker, security, assessment logic, reports, and documentation. That is a reasonable structure, but the product domain is beginning to expand. If organization, evidence, findings, framework mappings, and remediation are added without boundaries, the codebase will become difficult to reason about. The future domain should therefore be split around user-facing flow and stable concepts, not around a large collection of technical utilities.

Bastiat’s book adds a collaboration discipline for AI-assisted work. Each task should identify its context, intention, constraints, desired output, and validation evidence. The model can explore, mirror, critique, summarize, and generate alternatives, but the human decides what is accepted. This is especially important for a governance product: an AI-generated recommendation must never become an unreviewed compliance claim.

## Mapping the books to this repository

### Current stability work

The Docker and frontend failures were a Farley-style feedback problem. The system provided useful evidence: the backend health endpoint worked, the Nginx page worked, but the browser rendered a blank page. The fix required narrowing the fault boundary, reproducing the production bundle, correcting stale service-worker caching, and adding a visible runtime recovery screen.

The lesson is to keep a failure-specific diagnostic path in the repository. A future `scripts/preflight` command should check Docker availability, Compose configuration, required environment variables, service health, frontend HTTP status, API proxy status, and browser-cache guidance. This is a small, high-leverage improvement because it shortens the feedback loop for every future contributor.

### Assessment workflow

The current assessment flow should be treated as a stream-aligned product journey: create an assessment, provide context, answer relevant questions, review, submit, inspect findings, and export a report. The backend modules should support that journey without leaking database details into every page.

The next tests should follow the journey rather than the file tree. A synthetic browser test should register a user, create an assessment, complete all categories, review the result, export CSV/PDF, and sign out. A second test should prove that another user cannot read or export the first user’s assessment. These tests provide the early feedback and empiricism emphasized by Farley and the small-batch, safe-delivery orientation emphasized by *Accelerate*.

### Product domain

The product should gradually move from a questionnaire model toward an evidence-backed findings model. The stable concepts are likely to be `AI system`, `assessment`, `assessment version`, `question`, `answer`, `evidence`, `finding`, `recommendation`, `owner`, `review`, and `export`. This is a candidate domain vocabulary, not a command to create every table immediately.

The first domain decision to record should be whether a score is a descriptive summary, a risk indicator, or a maturity estimate. The application should not mix those meanings. A score should be traceable to the questionnaire version, answer values, weighting rule, and evidence completeness. A reviewer should be able to understand what changed when a score changes.

### Framework alignment

NIST AI RMF provides a useful top-level structure: Govern, Map, Measure, and Manage. The current categories can remain as lenses, but reports should explain which AI RMF function each result supports. ISO/IEC 42001 is useful for the management-system layer: policy ownership, continual improvement, traceability, risk treatment, and review cycles. The application should reference these frameworks and record versions without copying protected standards text or claiming certification.

OWASP’s current GenAI guidance should be kept in the future threat model. The current application does not yet execute an LLM in its assessment path, so prompt injection, excessive agency, system-prompt leakage, and unbounded consumption should be marked as future-scope risks. If an AI assistant is added, it should initially draft explanations or suggest follow-up questions. It should not edit assessment records, approve findings, or declare compliance.

## A reading-to-implementation sequence

Read Farley first for the chapters on iterative work, feedback, incrementalism, empiricism, experimentation, modularity, cohesion, separation of concerns, and managing coupling. Apply each chapter to one existing boundary in the repository. For example, use feedback to design the end-to-end browser test, incrementalism to split the evidence feature into small releases, and separation of concerns to keep scoring rules independent from report rendering.

Read the first half of *Accelerate* for measuring performance, technical practices, architecture, integrated security, product development, and sustainable work. Translate the ideas into a lightweight release scorecard. Do not attempt to implement the entire research model. Begin with a baseline for clean-checkout build time, time to validate a pull request, and recovery time after a failed local deployment.

Read Chapters 1–5 of *Team Topologies* for communication structures, Conway’s Law, team-first thinking, cognitive load, and the four fundamental topologies. For a solo project, reinterpret “team” as a durable area of responsibility. A stream-aligned area would own the assessment journey. A platform area would own Docker, CI, database migrations, and deployment. An enabling area would own security, accessibility, and framework interpretation. This keeps the repository navigable as it grows.

Read the framing and pattern sections of Bastiat’s book alongside actual implementation work. For each change, write a compact design brief: context, objective, constraints, options, chosen approach, risks, and validation evidence. This turns AI-assisted development into a repeatable engineering practice and creates a useful public record of professional growth.

## What to build next

The next release should focus on reliability evidence rather than additional visual polish. Add the browser-level synthetic journey, cross-user authorization coverage, assessment versioning, and Docker Desktop preflight diagnostics. Add a small ADR collection for the authentication-token approach, PostgreSQL/Docker boundary, assessment-versioning strategy, PWA caching policy, and non-certification product boundary.

After that, introduce evidence and findings. Allow an answer to be marked supported, unsupported, unknown, or not applicable. Store a short evidence reference and reviewer note. Generate a finding with priority, owner, due date, status, and rationale. Keep the scoring algorithm deterministic and inspectable before considering any LLM-generated interpretation.

Only after those foundations are stable should the product add an AI assistant. Its first safe role should be a design and review partner: clarify a question, identify missing evidence, suggest a counterexample, or draft plain-language explanations. Every generated output should show that it is AI-assisted, identify the underlying assessment context, and require human acceptance before persistence.

## Books and sources to add later

The current four-book set is enough for the next phase. If additional material becomes available later, the most useful additions would be Eric Evans’s *Domain-Driven Design* for the assessment domain model; Martin Kleppmann’s *Designing Data-Intensive Applications* for history, exports, audit logs, and consistency; and Harry Percival and Bob Gregory’s *Architecture Patterns with Python* for testable domain boundaries in the existing backend language.

For external reference material, continue with NIST AI RMF and its Playbook, ISO/IEC 42001 and ISO/IEC 23894 through authorized sources, OWASP GenAI guidance, the Architectural Decision Records community, and DORA’s current metrics guidance. These sources complement rather than replace the books: standards define governance expectations, research provides evidence, and books provide engineering heuristics.

## References

The page references in this document refer to the uploaded PDFs and their printed pagination. The public links below provide authoritative or publisher-maintained companion material for the non-book guidance.

- Bastiat, *LLM-Assisted Software Design*, attached PDF; public project: https://github.com/s31db/llm-dev-books
- Farley, *Modern Software Engineering: Doing What Works to Build Better Software Faster*, attached PDF.
- Forsgren, Humble, and Kim, *Accelerate*, attached PDF; DORA metrics: https://dora.dev/guides/dora-metrics/
- Skelton and Pais, *Team Topologies*, attached PDF; publisher page: https://teamtopologies.com/book
- NIST AI RMF Playbook: https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook
- ISO/IEC 42001: https://www.iso.org/standard/42001
- OWASP Top 10 for LLMs and GenAI Applications: https://genai.owasp.org/llm-top-10/
- Architectural Decision Records: https://adr.github.io/
