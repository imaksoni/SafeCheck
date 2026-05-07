import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/safety_session.dart';
import 'safety_sessions_api_client.dart';
import 'safety_sessions_local_db.dart';

final safetySessionsRepositoryProvider = Provider<SafetySessionsRepository>((ref) {
  final api = ref.watch(safetySessionsApiProvider);
  final localDb = ref.watch(safetySessionsLocalDbProvider);
  return SafetySessionsRepository(api, localDb);
});

class SafetySessionsRepository {
  final SafetySessionsApiClient _api;
  final SafetySessionsLocalDb _localDb;

  SafetySessionsRepository(this._api, this._localDb);

  Future<List<SafetySession>> getSessions() async {
    try {
      // Before getting sessions, try to sync any pending outbox events
      await syncOutbox();
      final sessions = await _api.getSessions();
      await _localDb.cacheSessions(sessions);
      return await _localDb.getSessions();
    } catch (e) {
      // Fallback to local
      return await _localDb.getSessions();
    }
  }

  Future<SafetySession> createSession(SafetySession session) async {
    // Save locally first as pending
    final pendingSession = session.copyWith(syncStatus: 'pending');
    final localId = await _localDb.insertSession(pendingSession);
    final localSession = pendingSession.copyWith(localId: localId);

    // Save to outbox
    await _localDb.insertOutboxEvent(
      'safety_session',
      localId,
      'create',
      json.encode(localSession.toJson()),
    );

    // Try to sync outbox
    await syncOutbox();

    // Return the updated local session (might be synced now)
    return await _localDb.getSession(localId) ?? localSession;
  }

  Future<SafetySession> cancelSession(SafetySession session) async {
    // Update locally as pending
    final cancelled = session.copyWith(
      status: 'cancelled',
      cancelledAt: DateTime.now(),
      syncStatus: 'pending'
    );
    await _localDb.updateSession(cancelled);

    // Save to outbox
    await _localDb.insertOutboxEvent(
      'safety_session',
      session.localId,
      'cancel',
      '{}', // payload not really needed for cancel, but keep valid JSON
    );

    // Try to sync outbox
    await syncOutbox();

    return await _localDb.getSession(session.localId!) ?? cancelled;
  }

  Future<SafetySession> completeSession(SafetySession session) async {
    // Update locally as pending
    final completed = session.copyWith(status: 'completed', syncStatus: 'pending');
    await _localDb.updateSession(completed);

    // Save to outbox
    await _localDb.insertOutboxEvent(
      'safety_session',
      session.localId,
      'complete',
      '{}',
    );

    // Try to sync outbox
    await syncOutbox();

    return await _localDb.getSession(session.localId!) ?? completed;
  }

  Future<void> syncOutbox() async {
    final events = await _localDb.getPendingOutboxEvents();

    for (final event in events) {
      final id = event['id'] as int;
      final localId = event['entity_id'] as int;
      final action = event['action'] as String;

      try {
        final session = await _localDb.getSession(localId);
        if (session == null) {
          // Local session no longer exists, discard event
          await _localDb.deleteOutboxEvent(id);
          continue;
        }

        if (action == 'create') {
          final serverSession = await _api.createSession(session);
          await _localDb.updateSession(serverSession.copyWith(localId: localId, syncStatus: 'synced'));
        } else if (action == 'cancel') {
          if (session.serverId == null) throw Exception('No server ID for cancel');
          final updatedSession = await _api.cancelSession(session.serverId!);
          await _localDb.updateSession(updatedSession.copyWith(localId: localId, syncStatus: 'synced'));
        } else if (action == 'complete') {
          if (session.serverId == null) throw Exception('No server ID for complete');
          final updatedSession = await _api.completeSession(session.serverId!);
          await _localDb.updateSession(updatedSession.copyWith(localId: localId, syncStatus: 'synced'));
        }

        // Success: delete the outbox event
        await _localDb.deleteOutboxEvent(id);

      } catch (e) {
        // Mark failed
        await _localDb.markOutboxEventFailed(id);

        // Update session status to failed
        final session = await _localDb.getSession(localId);
        if (session != null) {
          await _localDb.updateSession(session.copyWith(syncStatus: 'failed'));
        }
      }
    }
  }
}
