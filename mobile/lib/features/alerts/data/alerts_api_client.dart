import '../../../app/config.dart';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../auth/data/auth_repository.dart';
import '../domain/sos_request.dart';

final alertsApiProvider = Provider<AlertsApiClient>((ref) {
  final authRepo = ref.watch(authRepositoryProvider);
  return AlertsApiClient(authRepo);
});

class AlertsApiClient {
  final AuthRepository _authRepo;
  final String _baseUrl = Config.apiUrl;

  AlertsApiClient(this._authRepo);

  Future<Map<String, String>> _getHeaders() async {
    final token = await _authRepo.getIdToken();
    if (token == null) throw Exception('Not authenticated');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<void> sendSos(SosRequest request) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('$_baseUrl/alerts/sos'),
      headers: headers,
      body: json.encode(request.toJson()),
    );

    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception('Failed to send SOS: ${response.body}');
    }
  }
}
