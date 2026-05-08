import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'lost_phone_controller.dart';

class LostPhoneScreen extends ConsumerWidget {
  const LostPhoneScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(lostPhoneControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lost Phone Alert'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'If you have lost your phone, you can trigger a lost phone alert from this device. It will use the latest available location of your phone and notify your trusted contacts.',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: state.status == LostPhoneStatus.loading
                  ? null
                  : () {
                      ref.read(lostPhoneControllerProvider.notifier).triggerAlert();
                    },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: state.status == LostPhoneStatus.loading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('Trigger Lost Phone Alert', style: TextStyle(color: Colors.white, fontSize: 18)),
            ),
            const SizedBox(height: 24),
            if (state.status == LostPhoneStatus.error)
              Text(
                'Error: ${state.errorMessage}',
                style: const TextStyle(color: Colors.red),
              ),
            if (state.status == LostPhoneStatus.success && state.response != null) ...[
              const Divider(),
              const Text('Alert Triggered Successfully!', style: TextStyle(color: Colors.green, fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              if (state.response!.snapshot != null) ...[
                Text(
                  'Last synced at: ${DateFormat.yMd().add_jm().format(state.response!.lastSyncedAt!.toLocal())} (not live)',
                  style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text('Location: ${state.response!.snapshot!.latitude}, ${state.response!.snapshot!.longitude}'),
                Text('Battery: ${state.response!.snapshot!.batteryPercent}%'),
              ] else
                const Text('No location data available for your phone.', style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)),
              const SizedBox(height: 16),
              const Text('Notified Contacts:', style: TextStyle(fontWeight: FontWeight.bold)),
              if (state.response!.notifiedContacts.isEmpty)
                const Text('No contacts notified (none enabled for lost phone alerts).')
              else
                ...state.response!.notifiedContacts.map((contact) => Text('- $contact')),
            ],
          ],
        ),
      ),
    );
  }
}
