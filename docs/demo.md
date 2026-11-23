# Short end-to-end demonstration

This is a local smoke demonstration using synthetic data only.

## 1. Start the services

```bash
cp .env.example .env
docker compose up --build -d
```

## 2. Confirm service health

```bash
curl -f http://localhost:8000/health
curl -I http://localhost/
```

Expected result: the API health check returns HTTP 200 and the frontend responds with HTTP 200.

## 3. Open the API and application

- API documentation: <http://localhost:8000/docs>
- Frontend: <http://localhost/>

Create a local synthetic account through the application, create an assessment named `Synthetic payroll assistant`, answer only with fabricated information, and verify that the assessment summary renders.

## 4. Validate CLI connectivity

From the `cli` directory, configure the local API URL according to the CLI help and run:

```bash
python -m pytest -q
```

## 5. Stop and remove local state

```bash
docker compose down -v
```

The `-v` flag removes the local PostgreSQL volume. Do not use it if you need to preserve local demo data.

This demonstration is not a production-readiness claim. It verifies only that the local stack starts, responds, authenticates a synthetic user, creates an assessment, and renders a result.
