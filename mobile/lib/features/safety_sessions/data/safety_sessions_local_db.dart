import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../trusted_contacts/data/local_database.dart';
import '../domain/safety_session.dart';

final safetySessionsLocalDbProvider = Provider<SafetySessionsLocalDb>((ref) {
  final db = ref.watch(localDatabaseProvider);
  return SafetySessionsLocalDb(db);
});

class SafetySessionsLocalDb {
  final LocalDatabase _db;

  SafetySessionsLocalDb(this._db);

  Future<int> insertSession(SafetySession session) async {
    final db = await _db.database;
    return await db.insert('safety_sessions', {
      'server_id': session.serverId,
      'title': session.title,
      'destination': session.destination,
      'companion_name': session.companionName,
      'companion_phone': session.companionPhone,
      'notes': session.notes,
      'status': session.status,
      'start_at': session.startAt.toIso8601String(),
      'deadline_at': session.deadlineAt.toIso8601String(),
      'cancelled_at': session.cancelledAt?.toIso8601String(),
      'alert_sent_at': session.alertSentAt?.toIso8601String(),
      'sync_status': session.syncStatus,
    });
  }

  Future<void> updateSession(SafetySession session) async {
    final db = await _db.database;
    await db.update('safety_sessions', {
      'server_id': session.serverId,
      'title': session.title,
      'destination': session.destination,
      'companion_name': session.companionName,
      'companion_phone': session.companionPhone,
      'notes': session.notes,
      'status': session.status,
      'start_at': session.startAt.toIso8601String(),
      'deadline_at': session.deadlineAt.toIso8601String(),
      'cancelled_at': session.cancelledAt?.toIso8601String(),
      'alert_sent_at': session.alertSentAt?.toIso8601String(),
      'sync_status': session.syncStatus,
    }, where: 'local_id = ?', whereArgs: [session.localId]);
  }

  Future<SafetySession?> getSession(int localId) async {
    final db = await _db.database;
    final maps = await db.query('safety_sessions', where: 'local_id = ?', whereArgs: [localId]);
    if (maps.isEmpty) return null;
    final map = maps.first;
    return SafetySession(
      localId: map['local_id'] as int?,
      serverId: map['server_id'] as int?,
      title: map['title'] as String,
      destination: map['destination'] as String?,
      companionName: map['companion_name'] as String?,
      companionPhone: map['companion_phone'] as String?,
      notes: map['notes'] as String?,
      status: map['status'] as String,
      startAt: DateTime.parse(map['start_at'] as String),
      deadlineAt: DateTime.parse(map['deadline_at'] as String),
      cancelledAt: map['cancelled_at'] != null ? DateTime.parse(map['cancelled_at'] as String) : null,
      alertSentAt: map['alert_sent_at'] != null ? DateTime.parse(map['alert_sent_at'] as String) : null,
      syncStatus: map['sync_status'] as String,
    );
  }

  Future<List<SafetySession>> getSessions() async {
    final db = await _db.database;
    final maps = await db.query('safety_sessions', orderBy: 'start_at DESC');

    return maps.map((map) {
      return SafetySession(
        localId: map['local_id'] as int?,
        serverId: map['server_id'] as int?,
        title: map['title'] as String,
        destination: map['destination'] as String?,
        companionName: map['companion_name'] as String?,
        companionPhone: map['companion_phone'] as String?,
        notes: map['notes'] as String?,
        status: map['status'] as String,
        startAt: DateTime.parse(map['start_at'] as String),
        deadlineAt: DateTime.parse(map['deadline_at'] as String),
        cancelledAt: map['cancelled_at'] != null ? DateTime.parse(map['cancelled_at'] as String) : null,
        alertSentAt: map['alert_sent_at'] != null ? DateTime.parse(map['alert_sent_at'] as String) : null,
        syncStatus: map['sync_status'] as String,
      );
    }).toList();
  }

  Future<void> cacheSessions(List<SafetySession> sessions) async {
    final db = await _db.database;
    await db.transaction((txn) async {
      // Keep unsynced sessions (pending or failed)
      await txn.delete('safety_sessions', where: 'sync_status = ?', whereArgs: ['synced']);

      for (final session in sessions) {
        await txn.insert('safety_sessions', {
          'server_id': session.serverId,
          'title': session.title,
          'destination': session.destination,
          'companion_name': session.companionName,
          'companion_phone': session.companionPhone,
          'notes': session.notes,
          'status': session.status,
          'start_at': session.startAt.toIso8601String(),
          'deadline_at': session.deadlineAt.toIso8601String(),
          'cancelled_at': session.cancelledAt?.toIso8601String(),
          'alert_sent_at': session.alertSentAt?.toIso8601String(),
          'sync_status': 'synced',
        });
      }
    });
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
