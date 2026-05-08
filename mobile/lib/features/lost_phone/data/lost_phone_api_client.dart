import '../../../app/config.dart';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../auth/data/auth_repository.dart';
import '../domain/lost_phone_response.dart';

final lostPhoneApiProvider = Provider<LostPhoneApiClient>((ref) {
  final authRepo = ref.watch(authRepositoryProvider);
  return LostPhoneApiClient(authRepo);
});

class LostPhoneApiClient {
  final AuthRepository _authRepo;
  final String _baseUrl = Config.apiUrl;

  LostPhoneApiClient(this._authRepo);

  Future<Map<String, String>> _getHeaders() async {
    final token = await _authRepo.getIdToken();
    if (token == null) throw Exception('Not authenticated');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<LostPhoneResponse> triggerLostPhone() async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('$_baseUrl/alerts/lost-phone'),
      headers: headers,
    );

    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception('Failed to trigger lost phone alert: ${response.body}');
    }

    return LostPhoneResponse.fromJson(json.decode(response.body));
  }
}
