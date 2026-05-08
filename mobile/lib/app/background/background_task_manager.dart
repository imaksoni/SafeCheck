import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:workmanager/workmanager.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:firebase_core/firebase_core.dart';
import '../../features/safety_sessions/data/safety_sessions_repository.dart';
import '../../features/snapshots/data/snapshots_repository.dart';
import '../../features/snapshots/presentation/snapshots_controller.dart';

// TODO: Initialize Firebase options properly for background if depending on API

// TODO: Respect platform limitations for Android/iOS differences
// Android supports periodic background tasks (minimum 15 mins).
// iOS background fetch is opportunistic and not guaranteed to run precisely.

@pragma('vm:entry-point')
void callbackDispatcher() {
  WidgetsFlutterBinding.ensureInitialized();
  Workmanager().executeTask((task, inputData) async {
    return await executeBackgroundTask(task, ProviderContainer());
  });
}

// Extracted for testing
Future<bool> executeBackgroundTask(String task, ProviderContainer container) async {
  try {
    if (task == "syncRetry") {
      // 1. Retry pending outbox events
      await container.read(safetySessionsRepositoryProvider).syncOutbox();
      await container.read(snapshotsRepositoryProvider).syncOutbox();

      // 2. Refresh/sync latest snapshot during active session
      // Note: For background location, we would need appropriate platform permissions.
      // We capture snapshot and the save process triggers sync automatically.
      try {
        await container.read(snapshotsControllerProvider.notifier).captureSnapshot(source: 'background_sync');
      } catch (e) {
        debugPrint("Failed to capture background snapshot: $e");
        // We still consider the sync task successful even if snapshot fails (e.g. no location permission in background)
      }
    }

    container.dispose();
    return true;
  } catch (e) {
    debugPrint("Background task error: $e");
    container.dispose();
    return false; // Task failed, workmanager might retry depending on policy
  }
}

class BackgroundTaskManager {
  Future<void> initialize() async {
    await Workmanager().initialize(
      callbackDispatcher,
      isInDebugMode: kDebugMode,
    );
  }

  void registerPeriodicSync() {
    // TODO: Platform specific setup notes
    // For Android, this creates a periodic job minimum 15m. Needs AndroidManifest.xml updates.
    // For iOS, registerPeriodicTask is not supported the same way, we might need to rely on Background Fetch via Info.plist UIBackgroundModes.
    Workmanager().registerPeriodicTask(
      "sync_retry_task",
      "syncRetry",
      frequency: const Duration(minutes: 15), // Minimum allowed for Android
      constraints: Constraints(
        networkType: NetworkType.connected,
      ),
    );
  }
}
