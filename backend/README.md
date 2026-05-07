# SafeCheck Backend

This directory contains the FastAPI backend for the SafeCheck application.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: Firebase Admin SDK

## Local Development Setup

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12+

### 2. Environment Variables
Copy the example environment file to `.env`:
```bash
cp .env.example .env
```

To enable Firebase token verification, you need to provide Firebase credentials in the `.env` file via `FIREBASE_CREDENTIALS` (JSON string) or use the default `GOOGLE_APPLICATION_CREDENTIALS` logic.

### 3. Run with Docker Compose
From the root of the repository, run:
```bash
docker compose up -d --build
```
This will start both the PostgreSQL database and the FastAPI application on http://localhost:8000.

### 4. Migrations
Run Alembic migrations to initialize the database schema:
```bash
docker compose exec backend alembic upgrade head
```

### 5. Running Tests
You can run tests locally using `pytest`:
```bash
pip install -r requirements.txt
pytest tests/
```

## API Documentation
Once the server is running, you can access the automatically generated API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
