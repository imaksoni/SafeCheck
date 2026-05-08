import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/lost_phone_response.dart';
import '../data/lost_phone_repository.dart';

enum LostPhoneStatus { idle, loading, success, error }

class LostPhoneState {
  final LostPhoneStatus status;
  final String? errorMessage;
  final LostPhoneResponse? response;

  LostPhoneState({
    this.status = LostPhoneStatus.idle,
    this.errorMessage,
    this.response,
  });

  LostPhoneState copyWith({
    LostPhoneStatus? status,
    String? errorMessage,
    LostPhoneResponse? response,
  }) {
    return LostPhoneState(
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
      response: response ?? this.response,
    );
  }
}

final lostPhoneControllerProvider = NotifierProvider<LostPhoneController, LostPhoneState>(() {
  return LostPhoneController();
});

class LostPhoneController extends Notifier<LostPhoneState> {
  @override
  LostPhoneState build() {
    return LostPhoneState();
  }

  Future<void> triggerAlert() async {
    state = state.copyWith(status: LostPhoneStatus.loading);
    try {
      final repository = ref.read(lostPhoneRepositoryProvider);
      final response = await repository.triggerLostPhone();
      state = state.copyWith(status: LostPhoneStatus.success, response: response);
    } catch (e) {
      state = state.copyWith(status: LostPhoneStatus.error, errorMessage: e.toString());
    }
  }

  void reset() {
    state = LostPhoneState();
  }
}
