import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:mobile/features/auth/data/secure_token_storage.dart';
import 'package:mobile/features/trusted_contacts/data/trusted_contacts_api_client.dart';
import 'package:mobile/features/trusted_contacts/domain/trusted_contact.dart';

class MockSecureTokenStorage extends Mock implements SecureTokenStorage {}

void main() {
  late MockSecureTokenStorage mockTokenStorage;
  late TrustedContactsApiClient apiClient;

  setUp(() {
    mockTokenStorage = MockSecureTokenStorage();
    apiClient = TrustedContactsApiClient(mockTokenStorage);
    when(() => mockTokenStorage.getToken()).thenAnswer((_) async => 'mock_token');
  });

  group('TrustedContactsApiClient', () {
    test('initializes correctly with TokenStorage', () {
      expect(apiClient, isNotNull);
    });
  });
}
