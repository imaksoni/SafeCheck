import 'package:flutter/material.dart';
import 'app/router.dart';

void main() {
  // TODO: Initialize Firebase configuration here when available
  runApp(const SafeCheckApp());
}

class SafeCheckApp extends StatelessWidget {
  const SafeCheckApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SafeCheck',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      initialRoute: '/',
      onGenerateRoute: AppRouter.generateRoute,
    );
  }
}
