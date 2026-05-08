<<<<<<< SEARCH
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    return await executeBackgroundTask(task, ProviderContainer());
  });
}
=======
@pragma('vm:entry-point')
void callbackDispatcher() {
  WidgetsFlutterBinding.ensureInitialized();
  Workmanager().executeTask((task, inputData) async {
    return await executeBackgroundTask(task, ProviderContainer());
  });
}
>>>>>>> REPLACE
