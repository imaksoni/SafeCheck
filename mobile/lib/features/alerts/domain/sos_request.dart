import '../../snapshots/domain/snapshot.dart';

class SosRequest {
  final int? sessionId;
  final Snapshot? snapshot;

  SosRequest({this.sessionId, this.snapshot});

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'snapshot': snapshot?.toJson(),
    };
  }

  factory SosRequest.fromJson(Map<String, dynamic> json) {
    return SosRequest(
      sessionId: json['session_id'],
      snapshot: json['snapshot'] != null ? Snapshot.fromJson(json['snapshot']) : null,
    );
  }
}
