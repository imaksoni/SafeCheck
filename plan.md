1. **Integrate Workmanager**
   - We already added `workmanager` to `pubspec.yaml`. We need to wire it up in `mobile/lib/main.dart` to initialize the `BackgroundTaskManager` and schedule periodic syncing.
2. **Add background task registration**
   - Create `mobile/lib/app/background/background_task_manager.dart` (already started).
   - Implement `callbackDispatcher` with logic to:
     - Retry pending outbox events (via `syncOutbox` on `safetySessionsRepositoryProvider` and `snapshotsRepositoryProvider`).
     - Capture a new snapshot (refresh/sync latest snapshot) using `snapshotsControllerProvider`.
   - Implement `BackgroundTaskManager.initialize` and `registerPeriodicSync`.
3. **Handle platform limitations / Notes**
   - Add clear TODOs/notes regarding iOS Background Fetch vs Android Periodic Tasks. For Android, Workmanager sets minimum 15-minute intervals. For iOS, Workmanager triggers via background fetch which is non-deterministic.
4. **Local SQLite access**
   - Because `callbackDispatcher` runs in a new Dart isolate, it must re-initialize its dependencies. Riverpod's `ProviderContainer` is instantiated in the isolate, getting fresh instances of local database classes. Since `sqflite` works seamlessly across isolates (as the native C library handles concurrent writes/reads properly), background paths are safe.
5. **Update README.md**
   - Add a section on Platform Setup for Background Jobs (e.g., changes to `Info.plist` or `AndroidManifest.xml` that users will need to make manually in standard environments).
6. **Testing**
   - Write tests for `BackgroundTaskManager` where we mock Riverpod containers and ensure the `syncRetry` task calls expected methods. Since Workmanager is a native plugin, we'll unit test the dispatch logic by mocking repositories.
