import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/snapshot.dart';
import 'snapshots_api_client.dart';
import 'snapshots_local_db.dart';

final snapshotsRepositoryProvider = Provider<SnapshotsRepository>((ref) {
  final api = ref.watch(snapshotsApiProvider);
  final localDb = ref.watch(snapshotsLocalDbProvider);
  return SnapshotsRepository(api, localDb);
});

class SnapshotsRepository {
  final SnapshotsApiClient _api;
  final SnapshotsLocalDb _localDb;

  SnapshotsRepository(this._api, this._localDb);

  Future<Snapshot?> getLatestLocalSnapshot() async {
    return await _localDb.getLatestLocalSnapshot();
  }

  Future<Snapshot?> getLatestSyncedSnapshot() async {
    return await _localDb.getLatestSyncedSnapshot();
  }

  Future<Snapshot> saveSnapshot(Snapshot snapshot) async {
    final pendingSnapshot = snapshot.copyWith(syncStatus: 'pending');
    final localId = await _localDb.insertSnapshot(pendingSnapshot);
    final localSnapshot = pendingSnapshot.copyWith(localId: localId);

    await _localDb.insertOutboxEvent(
      'snapshot',
      localId,
      'create',
      json.encode(localSnapshot.toJson()),
    );

    // Attempt to sync immediately
    await syncOutbox();

    return await _localDb.getSnapshot(localId) ?? localSnapshot;
  }

  Future<void> syncOutbox() async {
    final events = await _localDb.getPendingOutboxEvents();

    for (final event in events) {
      final id = event['id'] as int;
      final entityType = event['entity_type'] as String;

      if (entityType != 'snapshot') continue;

      final localId = event['entity_id'] as int;
      final action = event['action'] as String;

      try {
        final snapshot = await _localDb.getSnapshot(localId);
        if (snapshot == null) {
          await _localDb.deleteOutboxEvent(id);
          continue;
        }

        if (action == 'create') {
          final serverSnapshot = await _api.createSnapshot(snapshot);
          await _localDb.updateSnapshot(serverSnapshot.copyWith(localId: localId, syncStatus: 'synced'));
        }

        // Success
        await _localDb.deleteOutboxEvent(id);

      } catch (e) {
        // Leave outbox event as pending so it is retried later
        // Only mark the local snapshot as failed sync status optionally,
        // but leaving as pending is better if we are going to retry.
      }
    }
  }
}
