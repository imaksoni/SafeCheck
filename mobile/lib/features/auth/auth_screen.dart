import 'package:flutter/material.dart';

class AuthScreen extends StatelessWidget {
  const AuthScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // TODO: Implement Firebase Auth
    return Scaffold(
      appBar: AppBar(title: const Text('Authentication')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pushReplacementNamed(context, '/home');
          },
          child: const Text('Login (Placeholder)'),
        ),
      ),
    );
  }
}
