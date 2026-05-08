import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'secure_token_storage.dart';

final firebaseAuthProvider = Provider<FirebaseAuth>((ref) {
  return FirebaseAuth.instance;
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final firebaseAuth = ref.watch(firebaseAuthProvider);
  final secureTokenStorage = ref.watch(secureTokenStorageProvider);
  return AuthRepository(firebaseAuth, secureTokenStorage);
});

final authStateChangesProvider = StreamProvider<User?>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return authRepository.authStateChanges;
});

class AuthRepository {
  final FirebaseAuth _firebaseAuth;
  final SecureTokenStorage _secureTokenStorage;

  AuthRepository(this._firebaseAuth, this._secureTokenStorage);

  Stream<User?> get authStateChanges => _firebaseAuth.authStateChanges();
  User? get currentUser => _firebaseAuth.currentUser;

  Future<UserCredential> signInWithEmailAndPassword(String email, String password) async {
    final userCredential = await _firebaseAuth.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
    await _updateToken(userCredential.user);
    return userCredential;
  }

  Future<UserCredential> signUpWithEmailAndPassword(String email, String password) async {
    final userCredential = await _firebaseAuth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
    await _updateToken(userCredential.user);
    return userCredential;
  }

  Future<void> signOut() async {
    await _firebaseAuth.signOut();
    await _secureTokenStorage.deleteToken();
  }

  Future<void> _updateToken(User? user) async {
    if (user != null) {
      final token = await user.getIdToken();
      if (token != null) {
        await _secureTokenStorage.saveToken(token);
      }
    }
  }

  Future<String?> getIdToken() async {
    if (currentUser != null) {
      return await currentUser!.getIdToken();
    }
    return null;
  }
}
