# Threat model

## Scope

This threat model covers the local and self-hosted AI Governance Assessor application: the React frontend, FastAPI API, CLI, PostgreSQL database, exported reports, and deployment configuration.

## Assets

- User accounts, password hashes, access tokens, and password-reset tokens.
- AI-system assessment answers, evidence, scores, and exported reports.
- Organization names and audit-log records.
- Deployment secrets, database credentials, and SMTP credentials.

## Trust boundaries

1. Browser or CLI client to the API.
2. API to PostgreSQL.
3. API and frontend containers to the local Docker network.
4. Operators and deployment secret stores to the application.
5. Exported CSV/PDF files leaving the application environment.

## Threat actors

- An unauthenticated internet user probing the API.
- An authenticated user attempting to access another organization’s assessments.
- A malicious or compromised operator with access to deployment infrastructure.
- Accidental disclosure through committed databases, logs, exports, or `.env` files.

## Primary threats and mitigations

| Threat | Required mitigation |
| --- | --- |
| Credential stuffing or brute-force login | Password hashing, rate limiting, lockout controls, strong deployment secrets, and monitoring. |
| Broken object-level authorization | Verify organization and assessment ownership on every read, update, export, and delete operation. |
| Token theft or reset-token reuse | TLS in deployment, short-lived access tokens, one-time reset tokens, secure storage, and rotation after incidents. |
| Database disclosure | Never commit runtime databases; restrict database network access; encrypt backups; minimize retained data. |
| Sensitive report leakage | Treat CSV/PDF exports as confidential; use controlled storage and explicit deletion/retention policies. |
| Misuse against an unauthorized AI system | Require explicit authorization and keep this tool limited to governance documentation and assessment workflows. |
| Supply-chain or dependency compromise | Pin and review dependencies, run CI checks, and review changes before deployment. |

## Out of scope

This project does not provide a complete legal determination, model red-team capability, data-loss prevention system, identity provider, or production-grade managed security service.

## Security acceptance criteria

Before public deployment, verify that test users and sample data are synthetic, production secrets are absent, authorization tests cover cross-user access, reset tokens cannot be reused, exports are access-controlled, and logs do not contain passwords or tokens.
