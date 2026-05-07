import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'trusted_contacts_controller.dart';
import 'contact_form_screen.dart';

class ContactsScreen extends ConsumerWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final contactsState = ref.watch(trustedContactsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Trusted Contacts'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const ContactFormScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: contactsState.when(
        data: (contacts) {
          if (contacts.isEmpty) {
            return const Center(
              child: Text('No trusted contacts yet. Add one!'),
            );
          }
          return RefreshIndicator(
            onRefresh: () => ref.read(trustedContactsProvider.notifier).refresh(),
            child: ListView.builder(
              itemCount: contacts.length,
              itemBuilder: (context, index) {
                final contact = contacts[index];
                return ListTile(
                  title: Text(contact.name),
                  subtitle: Text(contact.phone),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit),
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) => ContactFormScreen(contact: contact),
                            ),
                          );
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete),
                        onPressed: () {
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: const Text('Delete Contact'),
                              content: Text('Are you sure you want to delete ${contact.name}?'),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.of(context).pop(),
                                  child: const Text('Cancel'),
                                ),
                                TextButton(
                                  onPressed: () {
                                    if (contact.id != null) {
                                      ref.read(trustedContactsProvider.notifier).deleteContact(contact.id!);
                                    }
                                    Navigator.of(context).pop();
                                  },
                                  child: const Text('Delete', style: TextStyle(color: Colors.red)),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error loading contacts: $error'),
              ElevatedButton(
                onPressed: () => ref.read(trustedContactsProvider.notifier).refresh(),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
