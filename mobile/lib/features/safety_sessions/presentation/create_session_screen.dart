import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/safety_session.dart';
import 'safety_sessions_controller.dart';

class CreateSessionScreen extends ConsumerStatefulWidget {
  const CreateSessionScreen({super.key});

  @override
  ConsumerState<CreateSessionScreen> createState() => _CreateSessionScreenState();
}

class _CreateSessionScreenState extends ConsumerState<CreateSessionScreen> {
  final _formKey = GlobalKey<FormState>();
  String _title = '';
  String _destination = '';
  int _durationMinutes = 30;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Safety Session')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                decoration: const InputDecoration(labelText: 'Title'),
                validator: (value) => value == null || value.isEmpty ? 'Required' : null,
                onSaved: (value) => _title = value!,
              ),
              TextFormField(
                decoration: const InputDecoration(labelText: 'Destination (Optional)'),
                onSaved: (value) => _destination = value ?? '',
              ),
              DropdownButtonFormField<int>(
                value: _durationMinutes,
                decoration: const InputDecoration(labelText: 'Duration (Minutes)'),
                items: [15, 30, 45, 60, 120].map((int value) {
                  return DropdownMenuItem<int>(
                    value: value,
                    child: Text(value.toString()),
                  );
                }).toList(),
                onChanged: (newValue) {
                  setState(() {
                    _durationMinutes = newValue!;
                  });
                },
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () async {
                  if (_formKey.currentState!.validate()) {
                    _formKey.currentState!.save();
                    final startAt = DateTime.now();
                    final deadlineAt = startAt.add(Duration(minutes: _durationMinutes));

                    final session = SafetySession(
                      title: _title,
                      destination: _destination.isEmpty ? null : _destination,
                      startAt: startAt,
                      deadlineAt: deadlineAt,
                    );

                    await ref.read(safetySessionsControllerProvider.notifier).createSession(session);
                    if (context.mounted) Navigator.pop(context);
                  }
                },
                child: const Text('Start Session'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
