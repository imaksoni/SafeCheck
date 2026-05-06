# Architecture

## Overview
SafeCheck is a full-stack monorepo consisting of a Flutter mobile application and a FastAPI backend with a PostgreSQL database.

## Mobile (Flutter)
- Feature-first directory structure (`lib/features/`).
- Routing is handled via `AppRouter` in `lib/app/router.dart`.
- Firebase will be integrated later for authentication and notifications.

## Backend (FastAPI)
- Uses SQLAlchemy 2.0 with psycopg2 for database interactions.
- Alembic handles schema migrations.
- Structured following Domain-Driven Design (DDD) principles where applicable.
