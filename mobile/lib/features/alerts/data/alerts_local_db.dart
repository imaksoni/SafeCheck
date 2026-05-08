import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../trusted_contacts/data/local_database.dart';

final alertsLocalDbProvider = Provider<AlertsLocalDb>((ref) {
  final db = ref.watch(localDatabaseProvider);
  return AlertsLocalDb(db);
});

class AlertsLocalDb {
  final LocalDatabase _db;

  AlertsLocalDb(this._db);

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
