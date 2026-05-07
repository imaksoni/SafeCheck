class TrustedContact {
  final int? id;
  final String name;
  final String phone;
  final String? relation;
  final bool allowSessionAlerts;
  final bool allowLostPhoneAlerts;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  TrustedContact({
    this.id,
    required this.name,
    required this.phone,
    this.relation,
    this.allowSessionAlerts = false,
    this.allowLostPhoneAlerts = false,
    this.createdAt,
    this.updatedAt,
  });

  factory TrustedContact.fromJson(Map<String, dynamic> json) {
    return TrustedContact(
      id: json['id'],
      name: json['name'],
      phone: json['phone'],
      relation: json['relation'],
      allowSessionAlerts: json['allow_session_alerts'] ?? false,
      allowLostPhoneAlerts: json['allow_lost_phone_alerts'] ?? false,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'phone': phone,
      'relation': relation,
      'allow_session_alerts': allowSessionAlerts,
      'allow_lost_phone_alerts': allowLostPhoneAlerts,
    };
  }

  TrustedContact copyWith({
    int? id,
    String? name,
    String? phone,
    String? relation,
    bool? allowSessionAlerts,
    bool? allowLostPhoneAlerts,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return TrustedContact(
      id: id ?? this.id,
      name: name ?? this.name,
      phone: phone ?? this.phone,
      relation: relation ?? this.relation,
      allowSessionAlerts: allowSessionAlerts ?? this.allowSessionAlerts,
      allowLostPhoneAlerts: allowLostPhoneAlerts ?? this.allowLostPhoneAlerts,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
