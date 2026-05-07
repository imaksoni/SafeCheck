import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'safety_sessions_controller.dart';
import 'create_session_screen.dart';
import 'active_session_screen.dart';

class SessionsScreen extends ConsumerWidget {
  const SessionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionsAsync = ref.watch(safetySessionsControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Safety Sessions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(safetySessionsControllerProvider.notifier).refresh(),
          ),
        ],
      ),
      body: sessionsAsync.when(
        data: (sessions) {
          if (sessions.isEmpty) {
            return const Center(child: Text('No safety sessions.'));
          }
          return ListView.builder(
            itemCount: sessions.length,
            itemBuilder: (context, index) {
              final session = sessions[index];
              Widget syncIcon;
              if (session.syncStatus == 'synced') {
                syncIcon = const Icon(Icons.cloud_done, color: Colors.green);
              } else if (session.syncStatus == 'failed') {
                syncIcon = const Icon(Icons.error, color: Colors.red);
              } else {
                syncIcon = const Icon(Icons.cloud_upload, color: Colors.orange);
              }

              return ListTile(
                title: Text(session.title),
                subtitle: Text('Status: ${session.status} - Sync: ${session.syncStatus}'),
                trailing: syncIcon,
                onTap: () {
                  if (session.status == 'active') {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ActiveSessionScreen(session: session),
                      ),
                    );
                  }
                },
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const CreateSessionScreen()),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
