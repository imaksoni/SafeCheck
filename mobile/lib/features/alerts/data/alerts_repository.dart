import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/sos_request.dart';
import 'alerts_api_client.dart';
import 'alerts_local_db.dart';

final alertsRepositoryProvider = Provider<AlertsRepository>((ref) {
  final api = ref.watch(alertsApiProvider);
  final localDb = ref.watch(alertsLocalDbProvider);
  return AlertsRepository(api, localDb);
});

class AlertsRepository {
  final AlertsApiClient _api;
  final AlertsLocalDb _localDb;

  AlertsRepository(this._api, this._localDb);

  Future<void> sendSos(SosRequest request) async {
    try {
      // First try to process outbox if online
      await syncOutbox();

      // Then send the actual SOS
      await _api.sendSos(request);
    } catch (e) {
      // If network fails, add it to outbox
      await _localDb.insertOutboxEvent(
        'alert',
        null,
        'sos',
        json.encode(request.toJson()),
      );
      // We throw a specific exception to indicate it's pending
      throw SosQueuedException('SOS queued for offline delivery');
    }
  }

  Future<void> syncOutbox() async {
    final events = await _localDb.getPendingOutboxEvents();

    for (final event in events) {
      if (event['entity_type'] != 'alert') continue;

      final id = event['id'] as int;
      final action = event['action'] as String;
      final payload = event['payload'] as String;

      try {
        if (action == 'sos') {
          final request = SosRequest.fromJson(json.decode(payload));
          await _api.sendSos(request);
        }

        // Success: delete the outbox event
        await _localDb.deleteOutboxEvent(id);

      } catch (e) {
        // If it fails during sync, we leave it as pending to try again later
        // We do not mark it as failed unless it is a permanent error (like 400 Bad Request)
        // For simplicity and safety, we will leave it pending.
      }
    }
  }
}

class SosQueuedException implements Exception {
  final String message;
  SosQueuedException(this.message);

  @override
  String toString() => message;
}
