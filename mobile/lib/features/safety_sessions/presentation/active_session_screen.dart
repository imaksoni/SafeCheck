import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/safety_session.dart';
import 'safety_sessions_controller.dart';

class ActiveSessionScreen extends ConsumerWidget {
  final SafetySession session;

  const ActiveSessionScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Active Session'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Title: ${session.title}', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text('Destination: ${session.destination ?? 'None'}'),
            const SizedBox(height: 8),
            Text('Companion: ${session.companionName ?? 'None'}'),
            const SizedBox(height: 8),
            Text('Deadline: ${session.deadlineAt}'),
            const Spacer(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () async {
                    await ref.read(safetySessionsControllerProvider.notifier).completeSession(session);
                    if (context.mounted) Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                  child: const Text('Complete'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    await ref.read(safetySessionsControllerProvider.notifier).cancelSession(session);
                    if (context.mounted) Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                  child: const Text('Cancel'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
