import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/trusted_contact.dart';
import '../data/trusted_contacts_repository.dart';

final trustedContactsProvider = AsyncNotifierProvider<TrustedContactsNotifier, List<TrustedContact>>(
  () => TrustedContactsNotifier(),
);

class TrustedContactsNotifier extends AsyncNotifier<List<TrustedContact>> {
  @override
  Future<List<TrustedContact>> build() async {
    return _fetchContacts();
  }

  Future<List<TrustedContact>> _fetchContacts() async {
    final repository = ref.read(trustedContactsRepositoryProvider);
    return repository.getContacts();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchContacts());
  }

  Future<void> addContact(TrustedContact contact) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repository = ref.read(trustedContactsRepositoryProvider);
      await repository.addContact(contact);
      return _fetchContacts();
    });
  }

  Future<void> updateContact(TrustedContact contact) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repository = ref.read(trustedContactsRepositoryProvider);
      await repository.updateContact(contact);
      return _fetchContacts();
    });
  }

  Future<void> deleteContact(int id) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repository = ref.read(trustedContactsRepositoryProvider);
      await repository.deleteContact(id);
      return _fetchContacts();
    });
  }
}
