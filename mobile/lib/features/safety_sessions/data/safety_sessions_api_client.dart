import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../auth/data/secure_token_storage.dart';
import '../domain/safety_session.dart';

final safetySessionsApiProvider = Provider<SafetySessionsApiClient>((ref) {
  final tokenStorage = ref.watch(secureTokenStorageProvider);
  return SafetySessionsApiClient(tokenStorage);
});

class SafetySessionsApiClient {
  final SecureTokenStorage _tokenStorage;
  // TODO: Use env variable for base URL
  final String _baseUrl = 'http://10.0.2.2:8000/api/v1/sessions';

  SafetySessionsApiClient(this._tokenStorage);

  Future<Map<String, String>> _getHeaders() async {
    final token = await _tokenStorage.getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer \$token',
    };
  }

  Future<List<SafetySession>> getSessions() async {
    final response = await http.get(
      Uri.parse(_baseUrl),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => SafetySession.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load safety sessions: \${response.body}');
    }
  }

  Future<SafetySession> createSession(SafetySession session) async {
    final response = await http.post(
      Uri.parse(_baseUrl),
      headers: await _getHeaders(),
      body: json.encode(session.toJson()),
    );

    if (response.statusCode == 201) {
      return SafetySession.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create safety session: \${response.body}');
    }
  }

  Future<SafetySession> cancelSession(int id) async {
    final response = await http.post(
      Uri.parse('\$_baseUrl/\$id/cancel'),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      return SafetySession.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to cancel safety session: \${response.body}');
    }
  }

  Future<SafetySession> completeSession(int id) async {
    final response = await http.post(
      Uri.parse('\$_baseUrl/\$id/complete'),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      return SafetySession.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to complete safety session: \${response.body}');
    }
  }
}
