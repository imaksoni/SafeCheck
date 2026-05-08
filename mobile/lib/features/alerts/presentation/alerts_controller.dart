import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/sos_request.dart';
import '../data/alerts_repository.dart';
import '../../snapshots/presentation/snapshots_controller.dart';
import '../../snapshots/domain/snapshot.dart';
import 'dart:async';

enum SosState { idle, loading, success, pending, error }

class AlertsState {
  final SosState sosState;
  final String? errorMessage;
  final bool hasShownSnackbar;

  AlertsState({this.sosState = SosState.idle, this.errorMessage, this.hasShownSnackbar = false});

  AlertsState copyWith({SosState? sosState, String? errorMessage, bool? hasShownSnackbar}) {
    return AlertsState(
      sosState: sosState ?? this.sosState,
      errorMessage: errorMessage ?? this.errorMessage,
      hasShownSnackbar: hasShownSnackbar ?? this.hasShownSnackbar,
    );
  }
}

final alertsControllerProvider = NotifierProvider<AlertsController, AlertsState>(() {
  return AlertsController();
});

class AlertsController extends Notifier<AlertsState> {
  Timer? _syncTimer;

  @override
  AlertsState build() {
    // Start periodic sync of outbox
    _syncTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      _repository.syncOutbox();
    });

    // Initial sync
    _repository.syncOutbox();

    ref.onDispose(() {
      _syncTimer?.cancel();
    });

    return AlertsState();
  }

  AlertsRepository get _repository => ref.read(alertsRepositoryProvider);

  Future<void> triggerSos({int? sessionId}) async {
    state = state.copyWith(sosState: SosState.loading, hasShownSnackbar: false);

    try {
      // Get the current snapshot if possible
      Snapshot? snapshot;
      try {
        final snapshotsNotifier = ref.read(snapshotsControllerProvider.notifier);
        // Ensure we have a fresh snapshot
        await snapshotsNotifier.captureSnapshot(sessionId: sessionId, source: 'manual_sos');
        snapshot = await snapshotsNotifier.getLatestLocalSnapshot();
      } catch (e) {
        // Continue even if snapshot fails
      }

      final request = SosRequest(
        sessionId: sessionId,
        snapshot: snapshot,
      );

      await _repository.sendSos(request);
      state = state.copyWith(sosState: SosState.success);
    } on SosQueuedException {
      state = state.copyWith(sosState: SosState.pending);
    } catch (e) {
      state = state.copyWith(
        sosState: SosState.error,
        errorMessage: e.toString(),
      );
    }
  }

  void markSnackbarShown() {
    state = state.copyWith(hasShownSnackbar: true);
  }

  void reset() {
    state = AlertsState();
  }
}
