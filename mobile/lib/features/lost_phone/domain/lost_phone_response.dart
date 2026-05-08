import '../../snapshots/domain/snapshot.dart';

class LostPhoneResponse {
  final int alertId;
  final DateTime createdAt;
  final String type;
  final Snapshot? snapshot;
  final DateTime? lastSyncedAt;
  final List<String> notifiedContacts;

  LostPhoneResponse({
    required this.alertId,
    required this.createdAt,
    required this.type,
    this.snapshot,
    this.lastSyncedAt,
    required this.notifiedContacts,
  });

  factory LostPhoneResponse.fromJson(Map<String, dynamic> json) {
    return LostPhoneResponse(
      alertId: json['alert_id'],
      createdAt: DateTime.parse(json['created_at']),
      type: json['type'],
      snapshot: json['snapshot'] != null ? Snapshot.fromJson(json['snapshot']) : null,
      lastSyncedAt: json['last_synced_at'] != null ? DateTime.parse(json['last_synced_at']) : null,
      notifiedContacts: List<String>.from(json['notified_contacts']),
    );
  }
}
