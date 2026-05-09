# SafeCheck
Delayed SOS for solo travel and first meetings

## Overview
This repository contains the mobile app and backend services for SafeCheck.
- Mobile app: built with Flutter, Riverpod, and SQLite.
- Backend: built with FastAPI, PostgreSQL, SQLAlchemy 2.0, and Alembic.

## Quick Start

### 1. Setup Environment
Copy `.env.example` files in both the `backend/` and `mobile/` directories to their respective `.env` files.

```bash
cp backend/.env.example backend/.env
cp mobile/.env.example mobile/.env
```

### 2. Start Backend Locally (Docker)
Ensure Docker is installed and running. The Docker Compose file sets up the FastAPI application, PostgreSQL database, and Redis cache.

```bash
docker compose up --build -d
```
The backend should be available at http://localhost:8000.
You can verify it via `curl http://localhost:8000/health` (which will also indicate Redis status).

**Note:** Ensure `REDIS_URL` is set in your `.env` file (e.g., `REDIS_URL=redis://redis:6379/0` if running inside Docker Compose or `REDIS_URL=redis://localhost:6379/0` if running the backend bare-metal).

### 3. Firebase Setup
The mobile app uses Firebase for Authentication. To configure Firebase, install the FlutterFire CLI and configure the app for your Firebase project:

```bash
# Install the CLI if not already installed
dart pub global activate flutterfire_cli

# Configure Firebase
cd mobile
flutterfire configure
```
This will generate the required `firebase_options.dart` and update platform configurations. Then, uncomment the Firebase initialization code in `mobile/lib/main.dart`.

### 4. Background Tasks Platform Setup
The app uses Workmanager for syncing and snapshot capture in the background. Note the following platform caveats:

**Android:**
- Requires permissions in `AndroidManifest.xml` (e.g., `WAKE_LOCK`, `ACCESS_BACKGROUND_LOCATION` if capturing location in background).
- Supports periodic tasks, but Android enforces a minimum interval of 15 minutes.

**iOS:**
- Requires enabling "Background fetch" in Xcode (Capabilities -> Background Modes).
- Update `Info.plist` with `UIBackgroundModes` containing `fetch` (and `location` if needed).
- Background execution is opportunistic and non-deterministic (managed by iOS based on app usage).

### 5. Run Mobile App
Navigate to the mobile directory, install dependencies, and run:

```bash
cd mobile
flutter pub get

# By default, the app points to localhost (10.0.2.2 for Android emulators).
# To run with a custom API URL:
# flutter run --dart-define=API_URL=http://your-custom-url:8000/api/v1
flutter run
```

## Running Tests
### Backend
To run backend tests locally without Docker, you will need Python 3.12 installed.

```bash
cd backend
pip install -r requirements.txt
# Run tests using an in-memory or file-based SQLite database
DATABASE_URL=sqlite:///./test.db pytest tests/
```

### Mobile
To run Flutter tests:
```bash
cd mobile
flutter test
```

## Documentation
For more detailed information, please see the `docs/` folder:
- [Architecture](docs/architecture.md)
- [Detailed Setup](docs/setup.md)
