import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/lost_phone_response.dart';
import 'lost_phone_api_client.dart';

final lostPhoneRepositoryProvider = Provider<LostPhoneRepository>((ref) {
  final api = ref.watch(lostPhoneApiProvider);
  return LostPhoneRepository(api);
});

class LostPhoneRepository {
  final LostPhoneApiClient _api;

  LostPhoneRepository(this._api);

  Future<LostPhoneResponse> triggerLostPhone() async {
    return await _api.triggerLostPhone();
  }
}
