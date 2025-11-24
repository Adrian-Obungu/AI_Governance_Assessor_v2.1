# AI Governance Assessor

A production-quality AI governance assessment platform with FastAPI backend, React PWA frontend, and CLI tools.

## Features

- **Comprehensive Assessment**: Evaluate AI systems across Data Privacy, Model Risk, Ethics, and Compliance
- **Secure Authentication**: Bcrypt password hashing, account lockout, rate limiting
- **Multi-Format Reports**: Export assessments as CSV or PDF
- **Progressive Web App**: Offline-capable React frontend with responsive design
- **CLI Tools**: Command-line interface for automation and scripting
- **Fully Containerized**: Docker Compose for easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Running with Docker

```bash
# Clone the repository
git clone <repository-url>
cd ai-governance-assessor

# Copy environment template
cp .env.example .env

# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

See [docs/runbook.md](docs/runbook.md) for detailed development setup instructions.

## Architecture

- **Backend**: FastAPI + SQLite + Alembic migrations
- **Frontend**: React + Vite + TypeScript + Tailwind CSS + PWA
- **CLI**: Typer-based command-line tools
- **Database**: SQLite with versioned schema migrations
- **CI/CD**: GitHub Actions for linting, testing, and builds

## Documentation

- [API Documentation](docs/api_docs.md)
- [Security Guide](docs/security.md)
- [Operations Runbook](docs/runbook.md)

## Testing

```bash
# Backend tests
cd backend
pytest

# CLI tests
cd cli
pytest

# Frontend tests
cd frontend
npm test
```

## License

MIT License - See LICENSE file for details
