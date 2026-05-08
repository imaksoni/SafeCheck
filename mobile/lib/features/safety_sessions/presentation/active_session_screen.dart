import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/safety_session.dart';
import 'safety_sessions_controller.dart';
import '../../snapshots/presentation/snapshots_controller.dart';

class ActiveSessionScreen extends ConsumerStatefulWidget {
  final SafetySession session;

  const ActiveSessionScreen({super.key, required this.session});

  @override
  ConsumerState<ActiveSessionScreen> createState() => _ActiveSessionScreenState();
}

class _ActiveSessionScreenState extends ConsumerState<ActiveSessionScreen> {

  @override
  Widget build(BuildContext context) {
    // Watch to rebuild when snapshots change
    ref.watch(snapshotsControllerProvider);
    final snapshotsNotifier = ref.read(snapshotsControllerProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Active Session'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Title: ${widget.session.title}', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text('Destination: ${widget.session.destination ?? 'None'}'),
            const SizedBox(height: 8),
            Text('Companion: ${widget.session.companionName ?? 'None'}'),
            const SizedBox(height: 8),
            Text('Deadline: ${widget.session.deadlineAt}'),
            const SizedBox(height: 16),

            // Snapshots info
            Consumer(
              builder: (context, ref, child) {
                final state = ref.watch(snapshotsControllerProvider);
                final notifier = ref.read(snapshotsControllerProvider.notifier);

                return FutureBuilder(
                  future: Future.wait([
                    notifier.getLatestLocalSnapshot(),
                    notifier.getLatestSyncedSnapshot(),
                  ]),
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) {
                      return const CircularProgressIndicator();
                    }
                    final data = snapshot.data;
                    final local = data?[0];
                    final synced = data?[1];

                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Last Local Snapshot: ${local?.capturedAt.toLocal() ?? 'None'}'),
                        Text('Last Synced Snapshot: ${synced?.capturedAt.toLocal() ?? 'None'}'),
                        if (state.isLoading) const CircularProgressIndicator(),
                      ],
                    );
                  },
                );
              },
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () async {
                await snapshotsNotifier.captureSnapshot(sessionId: widget.session.serverId ?? widget.session.localId);
                setState(() {}); // refresh FutureBuilder
              },
              child: const Text('Capture Manual Snapshot'),
            ),

            const Spacer(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () async {
                    await ref.read(safetySessionsControllerProvider.notifier).completeSession(widget.session);
                    if (context.mounted) Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                  child: const Text('Complete'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    await ref.read(safetySessionsControllerProvider.notifier).cancelSession(widget.session);
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
