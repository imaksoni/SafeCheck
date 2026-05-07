import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final secureTokenStorageProvider = Provider<SecureTokenStorage>((ref) {
  return SecureTokenStorage(const FlutterSecureStorage());
});

class SecureTokenStorage {
  final FlutterSecureStorage _storage;

  SecureTokenStorage(this._storage);

  static const String _idTokenKey = 'safecheck_id_token';

  Future<void> saveToken(String token) async {
    await _storage.write(key: _idTokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _idTokenKey);
  }

  Future<void> deleteToken() async {
    await _storage.delete(key: _idTokenKey);
  }
}
