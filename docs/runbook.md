# Operations runbook

## Docker quick start

From the repository root:

```powershell
cd C:\path\to\AI_Governance_Assessor_v2.1
.\scripts\preflight.ps1 -Start -Build
docker compose ps
```

The preflight is intentionally run from the repository root. It checks that the Docker CLI exists, that Docker Desktop's Linux engine is reachable, that `.env` exists (copying `.env.example` for local development when needed), that Compose can resolve its configuration, and whether the host ports are already occupied. Without `-Start`, it performs diagnostics only; use `-Start` to launch the existing images or `-Start -Build` after code or Dockerfile changes.

On Linux/macOS, use `cp .env.example .env` instead. The Docker template now includes the PostgreSQL variables required by Compose. The local services are:

- Frontend: <http://localhost/>
- Backend health check: <http://localhost:8000/health>
- API documentation: <http://localhost:8000/docs>

Use detached mode (`-d`) so closing the terminal does not stop the stack. View service logs when diagnosing a problem:

```powershell
docker compose logs --tail=100
docker compose logs --tail=100 backend frontend db
```

Verify the endpoints without PowerShell 5.1 HTML parsing prompts:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/health
Invoke-WebRequest -UseBasicParsing http://localhost/
```

After the services are healthy, run the disposable synthetic API journey. It creates a unique `example.test` account, reads the live questionnaire schema, submits the highest available option for every question, verifies the summary, downloads both exports, and checks that unauthenticated assessment access is rejected:

```powershell
.\scripts\smoke-journey.ps1
```

The journey is API-level evidence rather than a browser test. It does not use real credentials, production data, or a persistent test account. The account remains local database data; remove it with `docker compose down -v` only when you intentionally want to destroy the local PostgreSQL volume.

Stop the stack with `docker compose down`. Remove the local PostgreSQL volume only when you intentionally want to destroy local data:

```bash
docker compose down -v
```

## Docker troubleshooting

Use the first failing preflight message to classify the problem rather than repeatedly rebuilding the application:

| Preflight result | Meaning | Next action |
| --- | --- | --- |
| `Docker CLI was not found` | Docker Desktop or its CLI is not installed/on `PATH`. | Install or repair Docker Desktop, then reopen PowerShell. |
| `Linux engine is unavailable` | Docker Desktop is closed, still starting, or using the wrong container mode. | Start Docker Desktop, switch to Linux containers, wait for readiness, and rerun the preflight. |
| `No .env ...` or Compose configuration failure | Local configuration is missing or invalid. | Review `.env.example`, create `.env`, then run `docker compose config`. Never commit `.env`. |
| Port warning | Another process or an existing stack is listening on port 80 or 8000. | Confirm whether it is this project; stop the conflict or change the host mapping. |
| Service endpoint not ready | Compose started, but the application or proxy has not become healthy. | Run `docker compose ps` and `docker compose logs --tail=100 backend frontend db`. |

If `docker compose ps` is run outside the repository root, Compose cannot find `docker-compose.yml` and reports `no configuration file provided`. Change into the repository root before running Compose commands.

If the frontend build reports that `nginx.conf` is missing, confirm that the command is run from the repository root and that the Compose file uses the repository-root frontend build context. The canonical file is `docker/nginx.conf`.

If PostgreSQL variables are reported as blank, confirm that `.env` exists in the repository root and was copied from `.env.example`. Do not commit `.env`.

If a port is already in use, stop the conflicting process or change the host-side port mapping in `docker-compose.yml`. The application container ports remain 80 and 8000.

## Manual backend setup

Use Python 3.11, matching the container and CI runtime. Python 3.14 is not currently the supported project runtime.

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///./test.db"
$env:SECRET_KEY = "local-validation-only"
python -m pytest -q
```

On Linux/macOS, activate with `source .venv/bin/activate` and set the variables with `export`.

For a manual server run, use a local SQLite URL for development or a PostgreSQL URL for a database-backed deployment. Run migrations before starting the server:

```bash
cd ..
PYTHONPATH=. alembic -c backend/alembic.ini upgrade head
PYTHONPATH=. python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Manual CLI setup

```bash
cd cli
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -r requirements.txt
python -m pytest -q
python main.py --help
```

## Frontend setup

```bash
cd frontend
npm ci
npm test
npm run build
npm run dev
```

The frontend development server runs on port 5173. In the Docker deployment, Nginx serves the built application on port 80 and proxies `/api/` requests to the backend service.

## Validation checklist

Run the backend suite, CLI suite, and frontend suite before opening a pull request. The public CI workflow also runs Black, Ruff, backend tests, CLI tests, and the frontend production build.

```bash
cd backend && pytest -q
cd ../cli && pytest -q
cd ../frontend && npm test && npm run build
```

The Docker smoke test is complete when `docker compose ps` reports healthy database, backend, and frontend services; the backend health endpoint returns HTTP 200; the frontend returns HTTP 200; and `scripts\smoke-journey.ps1` reports that signup, login, all four categories, summary, both exports, and unauthenticated rejection passed. Run the stack detached so the validation terminal remains usable.

## Security boundary

Use synthetic data only in local demonstrations. Never commit `.env`, database files, password-reset tokens, access tokens, user exports, or production logs. Replace all development secrets and configure TLS, restricted CORS, backups, monitoring, and an approved secret store before deployment beyond a local machine.
