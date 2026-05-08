import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../auth/data/secure_token_storage.dart';
import '../../../app/config.dart';
import 'dart:io' show Platform;

final deviceRepositoryProvider = Provider<DeviceRepository>((ref) {
  return DeviceRepository(ref.watch(secureTokenStorageProvider));
});

class DeviceRepository {
  final SecureTokenStorage _tokenStorage;

  DeviceRepository(this._tokenStorage);

  Future<void> registerDevice({String? fcmToken}) async {
    final token = await _tokenStorage.getToken();
    if (token == null) return;

    final platform = Platform.isIOS ? 'ios' : Platform.isAndroid ? 'android' : 'unknown';
    // Simplified device name, could use device_info_plus package later
    final deviceName = 'SafeCheck Device ($platform)';

    final response = await http.post(
      Uri.parse('${Config.apiUrl}/devices/register'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'platform': platform,
        'device_name': deviceName,
        'fcm_token': fcmToken,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to register device');
    }
  }

  Future<void> sendHeartbeat() async {
    final token = await _tokenStorage.getToken();
    if (token == null) return;

    final platform = Platform.isIOS ? 'ios' : Platform.isAndroid ? 'android' : 'unknown';
    final deviceName = 'SafeCheck Device ($platform)';

    final response = await http.post(
      Uri.parse('${Config.apiUrl}/devices/heartbeat?device_name=${Uri.encodeComponent(deviceName)}'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode != 200) {
      print('Failed to send device heartbeat: ${response.statusCode}');
    }
  }

  Future<void> updateFcmToken(String fcmToken) async {
    final token = await _tokenStorage.getToken();
    if (token == null) return;

    final platform = Platform.isIOS ? 'ios' : Platform.isAndroid ? 'android' : 'unknown';
    final deviceName = 'SafeCheck Device ($platform)';

    final response = await http.post(
      Uri.parse('${Config.apiUrl}/devices/fcm-token?device_name=${Uri.encodeComponent(deviceName)}'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'fcm_token': fcmToken,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to update FCM token');
    }
  }
}
