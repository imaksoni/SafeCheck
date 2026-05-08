import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:battery_plus/battery_plus.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../domain/snapshot.dart';
import '../data/snapshots_repository.dart';

final snapshotsControllerProvider =
    AsyncNotifierProvider<SnapshotsController, void>(() => SnapshotsController());

class SnapshotsController extends AsyncNotifier<void> {
  @override
  Future<void> build() async {
    // Initial build just ensures the provider is active
  }

  SnapshotsRepository get _repository => ref.read(snapshotsRepositoryProvider);

  Future<void> captureSnapshot({int? sessionId, String source = 'manual'}) async {
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      bool serviceEnabled;
      LocationPermission permission;

      serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location services are disabled.');
      }

      permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Location permissions are denied');
        }
      }

      if (permission == LocationPermission.deniedForever) {
        throw Exception('Location permissions are permanently denied, we cannot request permissions.');
      }

      final position = await Geolocator.getCurrentPosition();

      final battery = Battery();
      final batteryLevel = await battery.batteryLevel;

      final connectivityResult = await Connectivity().checkConnectivity();
      String networkType = 'none';
      bool isOnline = false;

      if (connectivityResult.contains(ConnectivityResult.wifi)) {
        networkType = 'wifi';
        isOnline = true;
      } else if (connectivityResult.contains(ConnectivityResult.mobile)) {
        networkType = 'cellular';
        isOnline = true;
      } else if (connectivityResult.contains(ConnectivityResult.ethernet) || connectivityResult.contains(ConnectivityResult.vpn)) {
         networkType = 'other';
         isOnline = true;
      }

      final snapshot = Snapshot(
        sessionId: sessionId,
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        batteryPercent: batteryLevel,
        isBatteryLow: batteryLevel <= 20,
        networkType: networkType,
        isOnline: isOnline,
        capturedAt: DateTime.now().toUtc(),
        source: source,
      );

      await _repository.saveSnapshot(snapshot);
    });
  }

  Future<Snapshot?> getLatestLocalSnapshot() async {
    return await _repository.getLatestLocalSnapshot();
  }

  Future<Snapshot?> getLatestSyncedSnapshot() async {
    return await _repository.getLatestSyncedSnapshot();
  }
}
