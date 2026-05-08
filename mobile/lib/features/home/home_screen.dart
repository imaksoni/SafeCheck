import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/presentation/auth_controller.dart';
import '../alerts/presentation/alerts_controller.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AlertsState>(alertsControllerProvider, (previous, next) {
      if (next.hasShownSnackbar) return;

      if (next.sosState == SosState.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('SOS Alert sent successfully!'), backgroundColor: Colors.green),
        );
        ref.read(alertsControllerProvider.notifier).markSnackbarShown();
      } else if (next.sosState == SosState.pending) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Offline: SOS Alert queued for delivery'), backgroundColor: Colors.orange),
        );
        ref.read(alertsControllerProvider.notifier).markSnackbarShown();
      } else if (next.sosState == SosState.error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send SOS: ${next.errorMessage}'), backgroundColor: Colors.red),
        );
        ref.read(alertsControllerProvider.notifier).markSnackbarShown();
      }
    });

    final alertsState = ref.watch(alertsControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('SafeCheck Home'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              ref.read(authControllerProvider.notifier).signOut();
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Welcome to SafeCheck!'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pushNamed('/trusted-contacts');
              },
              child: const Text('Manage Trusted Contacts'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pushNamed('/safety-sessions');
              },
              child: const Text('Safety Sessions'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pushNamed('/lost-phone');
              },
              child: const Text('Lost Phone?'),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: alertsState.sosState == SosState.loading
            ? null
            : () {
                ref.read(alertsControllerProvider.notifier).triggerSos();
              },
        backgroundColor: Colors.red,
        icon: alertsState.sosState == SosState.loading
            ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white))
            : const Icon(Icons.warning, color: Colors.white),
        label: const Text('SOS', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }
}
