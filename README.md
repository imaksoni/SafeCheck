# SafeCheck
Delayed SOS for solo travel and first meetings

## Overview
This repository contains the mobile app and backend services for SafeCheck.
- Mobile app: built with Flutter.
- Backend: built with FastAPI, PostgreSQL, SQLAlchemy 2.0, and Alembic.

## Quick Start

### 1. Setup Environment
Copy `.env.example` files in both the `backend/` and `mobile/` directories to their respective `.env` files.

```bash
cp backend/.env.example backend/.env
cp mobile/.env.example mobile/.env
```

### 2. Start Backend Locally (Docker)
Ensure Docker is installed and running, then execute:

```bash
docker compose up --build -d
```
The backend should be available at http://localhost:8000.
You can verify it via `curl http://localhost:8000/health`.

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

### 4. Run Mobile App
Navigate to the mobile directory and run:

```bash
cd mobile
flutter pub get
flutter run
```

## Documentation
For more detailed information, please see the `docs/` folder:
- [Architecture](docs/architecture.md)
- [Detailed Setup](docs/setup.md)
