import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/auth/presentation/auth_controller.dart';
import 'package:mobile/features/auth/data/auth_repository.dart';
import 'package:firebase_auth/firebase_auth.dart';

class MockAuthRepository extends Mock implements AuthRepository {}
class MockUserCredential extends Mock implements UserCredential {}

void main() {
  late MockAuthRepository mockAuthRepository;
  late ProviderContainer container;

  setUp(() {
    mockAuthRepository = MockAuthRepository();
    container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(mockAuthRepository),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('AuthController', () {
    test('signIn success returns true', () async {
      final mockUserCredential = MockUserCredential();
      when(() => mockAuthRepository.signInWithEmailAndPassword('test@example.com', 'password'))
          .thenAnswer((_) async => mockUserCredential);

      final result = await container.read(authControllerProvider.notifier).signIn('test@example.com', 'password');

      expect(result, isTrue);
    });

    test('signIn failure returns false', () async {
      final exception = Exception('Login failed');
      when(() => mockAuthRepository.signInWithEmailAndPassword('test@example.com', 'wrongpassword'))
          .thenThrow(exception);

      final result = await container.read(authControllerProvider.notifier).signIn('test@example.com', 'wrongpassword');

      expect(result, isFalse);
    });
  });
}
