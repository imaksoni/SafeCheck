import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../trusted_contacts/data/local_database.dart';
import '../domain/snapshot.dart';

final snapshotsLocalDbProvider = Provider<SnapshotsLocalDb>((ref) {
  final db = ref.watch(localDatabaseProvider);
  return SnapshotsLocalDb(db);
});

class SnapshotsLocalDb {
  final LocalDatabase _db;

  SnapshotsLocalDb(this._db);

  Future<int> insertSnapshot(Snapshot snapshot) async {
    final db = await _db.database;
    return await db.insert('snapshots', {
      'server_id': snapshot.serverId,
      'session_id': snapshot.sessionId,
      'latitude': snapshot.latitude,
      'longitude': snapshot.longitude,
      'accuracy': snapshot.accuracy,
      'battery_percent': snapshot.batteryPercent,
      'is_battery_low': snapshot.isBatteryLow ? 1 : 0,
      'network_type': snapshot.networkType,
      'is_online': snapshot.isOnline ? 1 : 0,
      'captured_at': snapshot.capturedAt.toIso8601String(),
      'source': snapshot.source,
      'sync_status': snapshot.syncStatus,
    });
  }

  Future<void> updateSnapshot(Snapshot snapshot) async {
    final db = await _db.database;
    await db.update('snapshots', {
      'server_id': snapshot.serverId,
      'session_id': snapshot.sessionId,
      'latitude': snapshot.latitude,
      'longitude': snapshot.longitude,
      'accuracy': snapshot.accuracy,
      'battery_percent': snapshot.batteryPercent,
      'is_battery_low': snapshot.isBatteryLow ? 1 : 0,
      'network_type': snapshot.networkType,
      'is_online': snapshot.isOnline ? 1 : 0,
      'captured_at': snapshot.capturedAt.toIso8601String(),
      'source': snapshot.source,
      'sync_status': snapshot.syncStatus,
    }, where: 'local_id = ?', whereArgs: [snapshot.localId]);
  }

  Future<Snapshot?> getSnapshot(int localId) async {
    final db = await _db.database;
    final maps = await db.query('snapshots', where: 'local_id = ?', whereArgs: [localId]);
    if (maps.isEmpty) return null;
    return _fromMap(maps.first);
  }

  Future<Snapshot?> getLatestLocalSnapshot() async {
    final db = await _db.database;
    final maps = await db.query('snapshots', orderBy: 'captured_at DESC', limit: 1);
    if (maps.isEmpty) return null;
    return _fromMap(maps.first);
  }

  Future<Snapshot?> getLatestSyncedSnapshot() async {
    final db = await _db.database;
    final maps = await db.query('snapshots', where: 'sync_status = ?', whereArgs: ['synced'], orderBy: 'captured_at DESC', limit: 1);
    if (maps.isEmpty) return null;
    return _fromMap(maps.first);
  }

  Snapshot _fromMap(Map<String, dynamic> map) {
    return Snapshot(
      localId: map['local_id'] as int?,
      serverId: map['server_id'] as int?,
      sessionId: map['session_id'] as int?,
      latitude: (map['latitude'] as num).toDouble(),
      longitude: (map['longitude'] as num).toDouble(),
      accuracy: map['accuracy'] != null ? (map['accuracy'] as num).toDouble() : null,
      batteryPercent: map['battery_percent'] as int,
      isBatteryLow: (map['is_battery_low'] as int) == 1,
      networkType: map['network_type'] as String,
      isOnline: (map['is_online'] as int) == 1,
      capturedAt: DateTime.parse(map['captured_at'] as String),
      source: map['source'] as String,
      syncStatus: map['sync_status'] as String,
    );
  }

  Future<void> insertOutboxEvent(String entityType, int? entityId, String action, String payload) async {
    final db = await _db.database;
    await db.insert('pending_outbox_events', {
      'entity_type': entityType,
      'entity_id': entityId,
      'action': action,
      'payload': payload,
      'status': 'pending',
    });
  }

  Future<List<Map<String, dynamic>>> getPendingOutboxEvents() async {
    final db = await _db.database;
    return await db.query('pending_outbox_events', where: 'status = ?', whereArgs: ['pending'], orderBy: 'id ASC');
  }

  Future<void> markOutboxEventFailed(int eventId) async {
    final db = await _db.database;
    await db.update('pending_outbox_events', {'status': 'failed'}, where: 'id = ?', whereArgs: [eventId]);
  }

  Future<void> deleteOutboxEvent(int eventId) async {
    final db = await _db.database;
    await db.delete('pending_outbox_events', where: 'id = ?', whereArgs: [eventId]);
  }
}
