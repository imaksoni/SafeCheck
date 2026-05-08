# Architecture

## Overview
SafeCheck is a full-stack monorepo consisting of a Flutter mobile application and a FastAPI backend with a PostgreSQL database.

## Mobile (Flutter)
- Feature-first directory structure (`lib/features/`).
- Routing is handled via `AppRouter` in `lib/app/router.dart`.
- Firebase Authentication is used to obtain ID tokens securely via `flutter_secure_storage`.
- Uses Riverpod 3 for state management, with `AsyncNotifier` for controllers.

### Offline-First Sync & Background Tasks
- The Flutter app leverages a local SQLite database for offline caching.
- Uses an Outbox pattern (`pending_outbox_events` table) to track sync statuses ('pending', 'synced', 'failed').
- Background processing is handled by Workmanager. Since Workmanager tasks run in isolated Dart environments, the background entry point initializes its own `ProviderContainer` to access repositories and perform periodic synchronization and snapshot captures.

## Backend (FastAPI)
- Uses FastAPI, SQLAlchemy 2.0 (with DeclarativeBase), and Alembic for migrations.
- Validates requests via Firebase Admin SDK to verify ID tokens, utilizing `get_current_user` FastAPI dependency.
- Background jobs (e.g., checking for expired safety sessions) are exposed as internal REST endpoints under `/api/v1/jobs/`. These endpoints are designed to be invoked by external schedulers like cron or AWS EventBridge rather than running a stateful worker queue like Celery.

## Core Data Flows

### Alert Creation
1. Users trigger SOS manually or a background job detects an expired safety session.
2. The endpoint creates an `Alert` record.
3. Relevant `TrustedContact` records (filtered by `allow_session_alerts`) are found.
4. An `AlertDelivery` record is generated for each eligible contact, putting it in a "pending" queue for delivery.

### Lost-Phone Flow
1. A user can trigger a lost-phone alert through a designated UI flow.
2. The `/api/v1/alerts/lost-phone` endpoint finds the latest stored snapshot for the user.
3. A new `Alert` of type `lost_phone` is generated, linking this latest snapshot.
4. `TrustedContact` records with `allow_lost_phone_alerts` enabled are identified.
5. Pending `AlertDelivery` records are created to inform these specific contacts.
