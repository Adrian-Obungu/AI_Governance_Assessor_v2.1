# Operations Runbook

## Quick Start

### Local Development

```bash
# 1. Clone repository
git clone <repository-url>
cd ai-governance-assessor

# 2. Copy environment file
cp .env.example .env

# 3. Start services with Docker
docker-compose up --build

# Access points:
# - Frontend: http://localhost:80
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Manual Setup (Without Docker)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
python main.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

#### CLI Setup

```bash
cd cli

# Install dependencies
pip install -r requirements.txt

# Run CLI
python main.py --help
```

## Database Management

### Running Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Database Backup

```bash
# Backup SQLite database
cp backend/ai_governance.db backend/ai_governance.db.backup.$(date +%Y%m%d_%H%M%S)

# Restore from backup
cp backend/ai_governance.db.backup.20241124_050000 backend/ai_governance.db
```

### Reset Database

```bash
cd backend

# Delete database
rm ai_governance.db

# Run migrations to recreate
alembic upgrade head
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_main.py

# Run with verbose output
pytest -v
```

### CLI Tests

```bash
cd cli

# Run CLI tests
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests (if configured)
npm test

# Build test
npm run build
```

## Docker Operations

### Build and Start

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
```

### Stop and Clean

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove all containers, networks, and images
docker-compose down --rmi all
```

### Rebuild Specific Service

```bash
# Rebuild backend only
docker-compose build backend
docker-compose up -d backend

# Rebuild frontend only
docker-compose build frontend
docker-compose up -d frontend
```

### Access Container Shell

```bash
# Backend container
docker-compose exec backend sh

# Frontend container
docker-compose exec frontend sh
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:80/
```

### View Logs

```bash
# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend
```

### Database Inspection

```bash
# Access SQLite database
sqlite3 backend/ai_governance.db

# Common queries
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM assessments;
SELECT * FROM failed_logins ORDER BY attempted_at DESC LIMIT 10;
```

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port 8000 already in use
lsof -i :8000  # Find process using port
kill -9 <PID>  # Kill process

# 2. Database migration failed
docker-compose exec backend alembic upgrade head

# 3. Missing environment variables
cat .env  # Verify all required variables are set
```

### Frontend Won't Build

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf dist

# Rebuild
npm run build
```

### Database Locked Error

```bash
# SQLite database is locked
# 1. Stop all services
docker-compose down

# 2. Remove lock file if exists
rm backend/ai_governance.db-shm
rm backend/ai_governance.db-wal

# 3. Restart services
docker-compose up
```

### Permission Errors (Linux/Mac)

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker volume permissions
docker-compose down -v
docker-compose up
```

## Deployment

### Production Checklist

- [ ] Update `SECRET_KEY` in .env
- [ ] Configure production CORS origins
- [ ] Set up HTTPS/TLS
- [ ] Configure production database (consider PostgreSQL)
- [ ] Set up log aggregation
- [ ] Configure monitoring and alerting
- [ ] Set up automated backups
- [ ] Review and adjust rate limits
- [ ] Disable debug mode
- [ ] Set `ENVIRONMENT=production`

### Environment Variables

Required for production:

```bash
# Security
SECRET_KEY=<strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./ai_governance.db

# CORS
CORS_ORIGINS=https://your-domain.com

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/ai-governance"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp backend/ai_governance.db $BACKUP_DIR/ai_governance.db.$DATE

# Keep only last 30 days
find $BACKUP_DIR -name "ai_governance.db.*" -mtime +30 -delete
```

## CLI Usage

### Authentication

```bash
# Login
python cli/main.py login

# Logout
python cli/main.py logout
```

### Assessment Management

```bash
# List assessments
python cli/main.py list

# Create assessment
python cli/main.py create --title "Q4 2024 Assessment"

# View assessment
python cli/main.py show 1

# View report
python cli/main.py report 1

# Export assessment
python cli/main.py export 1 --format pdf --output report.pdf
python cli/main.py export 1 --format csv --output report.csv
```

## Maintenance

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update

# CLI
cd cli
pip install --upgrade -r requirements.txt
```

### Clean Up Old Data

```bash
# Remove old failed login attempts (older than 30 days)
sqlite3 backend/ai_governance.db "DELETE FROM failed_logins WHERE attempted_at < datetime('now', '-30 days');"

# Remove expired password reset tokens
sqlite3 backend/ai_governance.db "DELETE FROM password_resets WHERE expires_at < datetime('now');"
```

## Support

### Logs Location

- Backend: `docker-compose logs backend`
- Frontend: `docker-compose logs frontend`
- Database: SQLite file at `backend/ai_governance.db`

### Common Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up --build -d

# Run backend tests
cd backend && pytest

# Run migrations
cd backend && alembic upgrade head

# Access database
sqlite3 backend/ai_governance.db
```
