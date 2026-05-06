# Setup Instructions

## Prerequisites
- Docker and Docker Compose
- Flutter SDK (stable)
- Python 3.12 (optional, for local development outside Docker)

## Backend
1. Copy `.env.example` to `.env` in `backend/` directory.
2. Run `docker compose up -d --build` from the root directory.
3. Access `http://localhost:8000/health` to verify it is running.

## Mobile
1. Copy `.env.example` to `.env` in `mobile/` directory.
2. Run `flutter pub get` in `mobile/`.
3. Run the app using `flutter run` or via your IDE.
