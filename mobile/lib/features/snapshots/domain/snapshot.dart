class Snapshot {
  final int? localId;
  final int? serverId;
  final int? sessionId;
  final double latitude;
  final double longitude;
  final double? accuracy;
  final int batteryPercent;
  final bool isBatteryLow;
  final String networkType;
  final bool isOnline;
  final DateTime capturedAt;
  final String source;
  final String syncStatus;

  Snapshot({
    this.localId,
    this.serverId,
    this.sessionId,
    required this.latitude,
    required this.longitude,
    this.accuracy,
    required this.batteryPercent,
    required this.isBatteryLow,
    required this.networkType,
    required this.isOnline,
    required this.capturedAt,
    required this.source,
    this.syncStatus = 'synced',
  });

  Snapshot copyWith({
    int? localId,
    int? serverId,
    int? sessionId,
    double? latitude,
    double? longitude,
    double? accuracy,
    int? batteryPercent,
    bool? isBatteryLow,
    String? networkType,
    bool? isOnline,
    DateTime? capturedAt,
    String? source,
    String? syncStatus,
  }) {
    return Snapshot(
      localId: localId ?? this.localId,
      serverId: serverId ?? this.serverId,
      sessionId: sessionId ?? this.sessionId,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      accuracy: accuracy ?? this.accuracy,
      batteryPercent: batteryPercent ?? this.batteryPercent,
      isBatteryLow: isBatteryLow ?? this.isBatteryLow,
      networkType: networkType ?? this.networkType,
      isOnline: isOnline ?? this.isOnline,
      capturedAt: capturedAt ?? this.capturedAt,
      source: source ?? this.source,
      syncStatus: syncStatus ?? this.syncStatus,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (serverId != null) 'id': serverId,
      if (sessionId != null) 'session_id': sessionId,
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'battery_percent': batteryPercent,
      'is_battery_low': isBatteryLow,
      'network_type': networkType,
      'is_online': isOnline,
      'captured_at': capturedAt.toIso8601String(),
      'source': source,
    };
  }

  factory Snapshot.fromJson(Map<String, dynamic> json) {
    return Snapshot(
      serverId: json['id'] as int?,
      sessionId: json['session_id'] as int?,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracy: json['accuracy'] != null ? (json['accuracy'] as num).toDouble() : null,
      batteryPercent: json['battery_percent'] as int,
      isBatteryLow: json['is_battery_low'] as bool,
      networkType: json['network_type'] as String,
      isOnline: json['is_online'] as bool,
      capturedAt: DateTime.parse(json['captured_at'] as String),
      source: json['source'] as String,
    );
  }
}
