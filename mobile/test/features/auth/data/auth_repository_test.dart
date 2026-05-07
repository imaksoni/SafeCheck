import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:mobile/features/auth/data/auth_repository.dart';
import 'package:mobile/features/auth/data/secure_token_storage.dart';

class MockFirebaseAuth extends Mock implements FirebaseAuth {}
class MockSecureTokenStorage extends Mock implements SecureTokenStorage {}
class MockUserCredential extends Mock implements UserCredential {}
class MockUser extends Mock implements User {}

void main() {
  late AuthRepository authRepository;
  late MockFirebaseAuth mockFirebaseAuth;
  late MockSecureTokenStorage mockSecureTokenStorage;

  setUp(() {
    mockFirebaseAuth = MockFirebaseAuth();
    mockSecureTokenStorage = MockSecureTokenStorage();
    authRepository = AuthRepository(mockFirebaseAuth, mockSecureTokenStorage);
  });

  group('AuthRepository', () {
    test('signInWithEmailAndPassword saves token on success', () async {
      final mockUserCredential = MockUserCredential();
      final mockUser = MockUser();

      when(() => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'test@example.com',
            password: 'password123',
          )).thenAnswer((_) async => mockUserCredential);

      when(() => mockUserCredential.user).thenReturn(mockUser);
      when(() => mockUser.getIdToken()).thenAnswer((_) async => 'fake_token');
      when(() => mockSecureTokenStorage.saveToken('fake_token')).thenAnswer((_) async => {});

      await authRepository.signInWithEmailAndPassword('test@example.com', 'password123');

      verify(() => mockFirebaseAuth.signInWithEmailAndPassword(email: 'test@example.com', password: 'password123')).called(1);
      verify(() => mockUser.getIdToken()).called(1);
      verify(() => mockSecureTokenStorage.saveToken('fake_token')).called(1);
    });

    test('signOut deletes token', () async {
      when(() => mockFirebaseAuth.signOut()).thenAnswer((_) async => {});
      when(() => mockSecureTokenStorage.deleteToken()).thenAnswer((_) async => {});

      await authRepository.signOut();

      verify(() => mockFirebaseAuth.signOut()).called(1);
      verify(() => mockSecureTokenStorage.deleteToken()).called(1);
    });
  });
}
