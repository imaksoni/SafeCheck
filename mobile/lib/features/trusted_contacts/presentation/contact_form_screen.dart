import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/trusted_contact.dart';
import 'trusted_contacts_controller.dart';

class ContactFormScreen extends ConsumerStatefulWidget {
  final TrustedContact? contact;
  const ContactFormScreen({super.key, this.contact});

  @override
  ConsumerState<ContactFormScreen> createState() => _ContactFormScreenState();
}

class _ContactFormScreenState extends ConsumerState<ContactFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _relationController;
  bool _allowSessionAlerts = false;
  bool _allowLostPhoneAlerts = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.contact?.name ?? '');
    _phoneController = TextEditingController(text: widget.contact?.phone ?? '');
    _relationController = TextEditingController(text: widget.contact?.relation ?? '');
    _allowSessionAlerts = widget.contact?.allowSessionAlerts ?? false;
    _allowLostPhoneAlerts = widget.contact?.allowLostPhoneAlerts ?? false;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _relationController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);
      try {
        final contact = TrustedContact(
          id: widget.contact?.id,
          name: _nameController.text,
          phone: _phoneController.text,
          relation: _relationController.text.isNotEmpty ? _relationController.text : null,
          allowSessionAlerts: _allowSessionAlerts,
          allowLostPhoneAlerts: _allowLostPhoneAlerts,
        );

        if (widget.contact == null) {
          await ref.read(trustedContactsProvider.notifier).addContact(contact);
        } else {
          await ref.read(trustedContactsProvider.notifier).updateContact(contact);
        }

        if (mounted) {
          Navigator.of(context).pop();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e')),
          );
        }
      } finally {
        if (mounted) setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.contact == null ? 'Add Contact' : 'Edit Contact'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(labelText: 'Name'),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter a name';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _phoneController,
                      decoration: const InputDecoration(labelText: 'Phone'),
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter a phone number';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _relationController,
                      decoration: const InputDecoration(labelText: 'Relation (Optional)'),
                    ),
                    const SizedBox(height: 24),
                    const Text('Alert Preferences', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    SwitchListTile(
                      title: const Text('Session Alerts'),
                      subtitle: const Text('Notify this contact if a session ends unexpectedly'),
                      value: _allowSessionAlerts,
                      onChanged: (value) => setState(() => _allowSessionAlerts = value),
                    ),
                    SwitchListTile(
                      title: const Text('Lost Phone Alerts'),
                      subtitle: const Text('Notify this contact if your phone is marked as lost'),
                      value: _allowLostPhoneAlerts,
                      onChanged: (value) => setState(() => _allowLostPhoneAlerts = value),
                    ),
                    const SizedBox(height: 32),
                    ElevatedButton(
                      onPressed: _submit,
                      child: Text(widget.contact == null ? 'Add Contact' : 'Save Changes'),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
