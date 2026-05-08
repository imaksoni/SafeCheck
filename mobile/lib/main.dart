import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:firebase_core/firebase_core.dart';
import 'app/router.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'dart:async';
import 'features/safety_sessions/data/safety_sessions_repository.dart';
import 'features/snapshots/data/snapshots_repository.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // TODO: Initialize Firebase configuration here when available using flutterfire configure
  // await Firebase.initializeApp(
  //   options: DefaultFirebaseOptions.currentPlatform,
  // );
  runApp(
    const ProviderScope(
      child: SafeCheckApp(),
    ),
  );
}

class SafeCheckApp extends ConsumerStatefulWidget {
  const SafeCheckApp({super.key});

  @override
  ConsumerState<SafeCheckApp> createState() => _SafeCheckAppState();
}

class _SafeCheckAppState extends ConsumerState<SafeCheckApp> with WidgetsBindingObserver {
  late StreamSubscription<List<ConnectivityResult>> _connectivitySubscription;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    _connectivitySubscription = Connectivity().onConnectivityChanged.listen((List<ConnectivityResult> results) {
      if (results.contains(ConnectivityResult.wifi) || results.contains(ConnectivityResult.mobile)) {
        _triggerSync();
      }
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _connectivitySubscription.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _triggerSync();
    }
  }

  void _triggerSync() {
    ref.read(safetySessionsRepositoryProvider).syncOutbox();
    ref.read(snapshotsRepositoryProvider).syncOutbox();
  }

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
