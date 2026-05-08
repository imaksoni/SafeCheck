import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/app/background/background_task_manager.dart';
import 'package:mobile/features/safety_sessions/data/safety_sessions_repository.dart';
import 'package:mobile/features/snapshots/data/snapshots_repository.dart';
import 'package:mobile/features/snapshots/presentation/snapshots_controller.dart';

class MockSafetySessionsRepository extends Mock implements SafetySessionsRepository {}
class MockSnapshotsRepository extends Mock implements SnapshotsRepository {}
class MockSnapshotsController extends AsyncNotifier<void> with Mock implements SnapshotsController {}

void main() {
  group('BackgroundTaskManager', () {
    late MockSafetySessionsRepository mockSafetySessionsRepo;
    late MockSnapshotsRepository mockSnapshotsRepo;
    late MockSnapshotsController mockSnapshotsController;

    setUp(() {
      mockSafetySessionsRepo = MockSafetySessionsRepository();
      mockSnapshotsRepo = MockSnapshotsRepository();
      mockSnapshotsController = MockSnapshotsController();
    });

    test('executeBackgroundTask handles syncRetry correctly', () async {
      when(() => mockSafetySessionsRepo.syncOutbox()).thenAnswer((_) async => {});
      when(() => mockSnapshotsRepo.syncOutbox()).thenAnswer((_) async => {});
      when(() => mockSnapshotsController.captureSnapshot(source: 'background_sync')).thenAnswer((_) async => {});

      final container = ProviderContainer(
        overrides: [
          safetySessionsRepositoryProvider.overrideWithValue(mockSafetySessionsRepo),
          snapshotsRepositoryProvider.overrideWithValue(mockSnapshotsRepo),
          snapshotsControllerProvider.overrideWith(() => mockSnapshotsController),
        ],
      );

      final result = await executeBackgroundTask('syncRetry', container);

      expect(result, isTrue);

      verify(() => mockSafetySessionsRepo.syncOutbox()).called(1);
      verify(() => mockSnapshotsRepo.syncOutbox()).called(1);
      verify(() => mockSnapshotsController.captureSnapshot(source: 'background_sync')).called(1);
    });

    test('executeBackgroundTask returns true even if captureSnapshot fails', () async {
      when(() => mockSafetySessionsRepo.syncOutbox()).thenAnswer((_) async => {});
      when(() => mockSnapshotsRepo.syncOutbox()).thenAnswer((_) async => {});
      when(() => mockSnapshotsController.captureSnapshot(source: 'background_sync')).thenThrow(Exception('Location denied'));

      final container = ProviderContainer(
        overrides: [
          safetySessionsRepositoryProvider.overrideWithValue(mockSafetySessionsRepo),
          snapshotsRepositoryProvider.overrideWithValue(mockSnapshotsRepo),
          snapshotsControllerProvider.overrideWith(() => mockSnapshotsController),
        ],
      );

      final result = await executeBackgroundTask('syncRetry', container);

      // Should still be true, as we catch the snapshot error
      expect(result, isTrue);

      verify(() => mockSafetySessionsRepo.syncOutbox()).called(1);
      verify(() => mockSnapshotsRepo.syncOutbox()).called(1);
      verify(() => mockSnapshotsController.captureSnapshot(source: 'background_sync')).called(1);
    });

    test('executeBackgroundTask returns false on major failure', () async {
      when(() => mockSafetySessionsRepo.syncOutbox()).thenThrow(Exception('DB error'));

      final container = ProviderContainer(
        overrides: [
          safetySessionsRepositoryProvider.overrideWithValue(mockSafetySessionsRepo),
        ],
      );

      final result = await executeBackgroundTask('syncRetry', container);

      // Should be false
      expect(result, isFalse);
    });
  });
}
