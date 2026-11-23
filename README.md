# AI Governance Assessor

A self-hostable assessment platform for translating practical AI governance controls into structured evidence, maturity scores, and exportable reports.

The project is designed for security, compliance, and engineering teams that need a repeatable way to document how an AI system is governed. It is an assessment aid—not a legal-certification engine and not a substitute for professional advice.

## Current status

This repository is the candidate canonical implementation of the AI Governance Assessor. It is under active validation and cleanup. Treat the current release as a development/assessment environment until the end-to-end checks below pass in CI and locally.

## Capabilities

- Assess AI systems across data privacy, model risk, ethics, and compliance domains.
- Provide a FastAPI backend with authenticated assessment workflows.
- Provide a React/Vite progressive web application.
- Provide a Typer-based CLI for scripted workflows.
- Export assessment results as CSV and PDF.
- Run locally with Docker Compose and PostgreSQL.
- Run automated backend, frontend, and CLI tests.

## Architecture

- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL in Docker.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, and PWA support.
- **CLI:** Typer client for automation and scripting.
- **Testing:** pytest, Vitest, and GitHub Actions CI.
- **Local test database:** SQLite is used by the backend test configuration; it is not production storage.

## Quick start with Docker

### Prerequisites

- Docker Engine and Docker Compose
- Node.js 18+ for frontend development outside Docker
- Python 3.11+ for backend and CLI development outside Docker

### Start the stack

```bash
git clone https://github.com/Adrian-Obungu/AI_Governance_Assessor_v2.1.git
cd AI_Governance_Assessor_v2.1
cp .env.example .env
# Replace every development placeholder in .env before using the stack beyond local testing.
docker compose up --build
```

The default local services are:

- Frontend: <http://localhost/>
- Backend health check: <http://localhost:8000/health>
- API documentation: <http://localhost:8000/docs>

Stop the stack with:

```bash
docker compose down
```

## Local validation commands

```bash
# Backend
cd backend
python -m pytest -q

# CLI
cd ../cli
python -m pytest -q

# Frontend
cd ../frontend
npm ci
npm test
npm run build
```

The complete short demonstration is in [`docs/demo.md`](docs/demo.md). Operational setup is in [`docs/runbook.md`](docs/runbook.md), and the security model is in [`docs/threat-model.md`](docs/threat-model.md).

## Security and privacy boundary

Do not commit databases, credentials, access tokens, password-reset tokens, user exports, production logs, or personal data. Use `.env.example` only as a configuration template. Keep real secrets in the deployment secret store.

The project is intended for authorized internal assessments. Only assess systems for which you have explicit permission. Do not upload confidential model data or personal information to an unapproved deployment.

See [`docs/limitations.md`](docs/limitations.md) for known limitations and [`docs/security.md`](docs/security.md) for implementation guidance.

## Roadmap

1. Complete backend, CLI, frontend, and Docker smoke validation.
2. Add deterministic sample data and a repeatable demo fixture.
3. Document assessment scoring and framework mappings with citations.
4. Add stronger audit-log and deployment-hardening guidance.
5. Publish a versioned release only after the security and reproducibility gates pass.

## License

MIT License. See [`LICENSE`](LICENSE).
