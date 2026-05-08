import '../../../app/config.dart';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../auth/data/auth_repository.dart';
import '../domain/snapshot.dart';

final snapshotsApiProvider = Provider<SnapshotsApiClient>((ref) {
  final authRepo = ref.watch(authRepositoryProvider);
  return SnapshotsApiClient(authRepo);
});

class SnapshotsApiClient {
  final AuthRepository _authRepo;
  final String _baseUrl = Config.apiUrl;

  SnapshotsApiClient(this._authRepo);

  Future<Map<String, String>> _getHeaders() async {
    final token = await _authRepo.getIdToken();
    if (token == null) throw Exception('Not authenticated');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<Snapshot> createSnapshot(Snapshot snapshot) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('$_baseUrl/snapshots'),
      headers: headers,
      body: json.encode(snapshot.toJson()),
    );

    if (response.statusCode == 201) {
      return Snapshot.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create snapshot');
    }
  }

  Future<Snapshot?> getLatestSnapshot() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('$_baseUrl/snapshots/latest'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return Snapshot.fromJson(json.decode(response.body));
    } else if (response.statusCode == 404) {
      return null;
    } else {
      throw Exception('Failed to load latest snapshot');
    }
  }
}
