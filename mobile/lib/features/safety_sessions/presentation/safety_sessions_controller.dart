import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/safety_session.dart';
import '../data/safety_sessions_repository.dart';

final safetySessionsControllerProvider =
    AsyncNotifierProvider<SafetySessionsController, List<SafetySession>>(
  () => SafetySessionsController(),
);

class SafetySessionsController extends AsyncNotifier<List<SafetySession>> {
  @override
  Future<List<SafetySession>> build() async {
    return _repository.getSessions();
  }

  SafetySessionsRepository get _repository => ref.read(safetySessionsRepositoryProvider);

  Future<void> createSession(SafetySession session) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repository.createSession(session);
      return _repository.getSessions();
    });
  }

  Future<void> cancelSession(SafetySession session) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repository.cancelSession(session);
      return _repository.getSessions();
    });
  }

  Future<void> completeSession(SafetySession session) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repository.completeSession(session);
      return _repository.getSessions();
    });
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.getSessions());
  }
}
