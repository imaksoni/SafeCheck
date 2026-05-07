class SafetySession {
  final int? localId;
  final int? serverId;
  final String title;
  final String? destination;
  final String? companionName;
  final String? companionPhone;
  final String? notes;
  final String status;
  final DateTime startAt;
  final DateTime deadlineAt;
  final DateTime? cancelledAt;
  final DateTime? alertSentAt;
  final String syncStatus;

  SafetySession({
    this.localId,
    this.serverId,
    required this.title,
    this.destination,
    this.companionName,
    this.companionPhone,
    this.notes,
    this.status = 'active',
    required this.startAt,
    required this.deadlineAt,
    this.cancelledAt,
    this.alertSentAt,
    this.syncStatus = 'pending',
  });

  SafetySession copyWith({
    int? localId,
    int? serverId,
    String? title,
    String? destination,
    String? companionName,
    String? companionPhone,
    String? notes,
    String? status,
    DateTime? startAt,
    DateTime? deadlineAt,
    DateTime? cancelledAt,
    DateTime? alertSentAt,
    String? syncStatus,
  }) {
    return SafetySession(
      localId: localId ?? this.localId,
      serverId: serverId ?? this.serverId,
      title: title ?? this.title,
      destination: destination ?? this.destination,
      companionName: companionName ?? this.companionName,
      companionPhone: companionPhone ?? this.companionPhone,
      notes: notes ?? this.notes,
      status: status ?? this.status,
      startAt: startAt ?? this.startAt,
      deadlineAt: deadlineAt ?? this.deadlineAt,
      cancelledAt: cancelledAt ?? this.cancelledAt,
      alertSentAt: alertSentAt ?? this.alertSentAt,
      syncStatus: syncStatus ?? this.syncStatus,
    );
  }

  factory SafetySession.fromJson(Map<String, dynamic> json) {
    return SafetySession(
      serverId: json['id'] as int?,
      title: json['title'] as String,
      destination: json['destination'] as String?,
      companionName: json['companion_name'] as String?,
      companionPhone: json['companion_phone'] as String?,
      notes: json['notes'] as String?,
      status: json['status'] as String,
      startAt: DateTime.parse(json['start_at'] as String),
      deadlineAt: DateTime.parse(json['deadline_at'] as String),
      cancelledAt: json['cancelled_at'] != null ? DateTime.parse(json['cancelled_at'] as String) : null,
      alertSentAt: json['alert_sent_at'] != null ? DateTime.parse(json['alert_sent_at'] as String) : null,
      syncStatus: 'synced',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      if (destination != null) 'destination': destination,
      if (companionName != null) 'companion_name': companionName,
      if (companionPhone != null) 'companion_phone': companionPhone,
      if (notes != null) 'notes': notes,
      'status': status,
      'start_at': startAt.toIso8601String(),
      'deadline_at': deadlineAt.toIso8601String(),
      if (cancelledAt != null) 'cancelled_at': cancelledAt?.toIso8601String(),
      if (alertSentAt != null) 'alert_sent_at': alertSentAt?.toIso8601String(),
    };
  }
}
