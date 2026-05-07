import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../auth/data/secure_token_storage.dart';
import '../domain/trusted_contact.dart';

final trustedContactsApiProvider = Provider<TrustedContactsApiClient>((ref) {
  final tokenStorage = ref.watch(secureTokenStorageProvider);
  return TrustedContactsApiClient(tokenStorage);
});

class TrustedContactsApiClient {
  // In a real app, this should be configurable (e.g. from env)
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1/trusted-contacts';
  final SecureTokenStorage _tokenStorage;

  TrustedContactsApiClient(this._tokenStorage);

  Future<Map<String, String>> _getHeaders() async {
    final token = await _tokenStorage.getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<List<TrustedContact>> getContacts() async {
    final headers = await _getHeaders();
    final response = await http.get(Uri.parse(baseUrl), headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => TrustedContact.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load contacts');
    }
  }

  Future<TrustedContact> createContact(TrustedContact contact) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse(baseUrl),
      headers: headers,
      body: json.encode(contact.toJson()),
    );

    if (response.statusCode == 201) {
      return TrustedContact.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create contact');
    }
  }

  Future<TrustedContact> updateContact(TrustedContact contact) async {
    final headers = await _getHeaders();
    final response = await http.put(
      Uri.parse('$baseUrl/${contact.id}'),
      headers: headers,
      body: json.encode(contact.toJson()),
    );

    if (response.statusCode == 200) {
      return TrustedContact.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to update contact');
    }
  }

  Future<void> deleteContact(int id) async {
    final headers = await _getHeaders();
    final response = await http.delete(
      Uri.parse('$baseUrl/$id'),
      headers: headers,
    );

    if (response.statusCode != 204) {
      throw Exception('Failed to delete contact');
    }
  }
}
