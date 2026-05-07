import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/trusted_contact.dart';
import 'trusted_contacts_api_client.dart';
import 'local_database.dart';

final trustedContactsRepositoryProvider = Provider<TrustedContactsRepository>((ref) {
  final api = ref.watch(trustedContactsApiProvider);
  final db = ref.watch(localDatabaseProvider);
  return TrustedContactsRepository(api, db);
});

class TrustedContactsRepository {
  final TrustedContactsApiClient _api;
  final LocalDatabase _db;

  TrustedContactsRepository(this._api, this._db);

  Future<List<TrustedContact>> getContacts() async {
    try {
      final contacts = await _api.getContacts();
      await _db.cacheContacts(contacts);
      return contacts;
    } catch (e) {
      // If network fails, return cached contacts
      return await _db.getCachedContacts();
    }
  }

  Future<TrustedContact> addContact(TrustedContact contact) async {
    final newContact = await _api.createContact(contact);
    // Refresh cache
    await getContacts();
    return newContact;
  }

  Future<TrustedContact> updateContact(TrustedContact contact) async {
    final updatedContact = await _api.updateContact(contact);
    // Refresh cache
    await getContacts();
    return updatedContact;
  }

  Future<void> deleteContact(int id) async {
    await _api.deleteContact(id);
    // Refresh cache
    await getContacts();
  }
}
