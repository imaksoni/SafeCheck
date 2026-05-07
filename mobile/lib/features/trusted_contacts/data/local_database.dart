import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/trusted_contact.dart';

final localDatabaseProvider = Provider<LocalDatabase>((ref) {
  return LocalDatabase();
});

class LocalDatabase {
  static Database? _database;
  static const String tableName = 'trusted_contacts';

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('safecheck.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE $tableName (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        relation TEXT,
        allow_session_alerts INTEGER NOT NULL DEFAULT 0,
        allow_lost_phone_alerts INTEGER NOT NULL DEFAULT 0,
        is_synced INTEGER NOT NULL DEFAULT 1,
        is_deleted INTEGER NOT NULL DEFAULT 0
      )
    ''');
  }

  Future<void> cacheContacts(List<TrustedContact> contacts) async {
    final db = await database;
    await db.transaction((txn) async {
      // Clear existing cached (synced) contacts
      await txn.delete(tableName, where: 'is_synced = ?', whereArgs: [1]);

      // Insert new contacts
      for (final contact in contacts) {
        await txn.insert(tableName, {
          'server_id': contact.id,
          'name': contact.name,
          'phone': contact.phone,
          'relation': contact.relation,
          'allow_session_alerts': contact.allowSessionAlerts ? 1 : 0,
          'allow_lost_phone_alerts': contact.allowLostPhoneAlerts ? 1 : 0,
          'is_synced': 1,
        });
      }
    });
  }

  Future<List<TrustedContact>> getCachedContacts() async {
    final db = await database;
    final maps = await db.query(tableName, where: 'is_deleted = ?', whereArgs: [0]);

    return maps.map((map) {
      return TrustedContact(
        id: map['server_id'] as int?,
        name: map['name'] as String,
        phone: map['phone'] as String,
        relation: map['relation'] as String?,
        allowSessionAlerts: (map['allow_session_alerts'] as int) == 1,
        allowLostPhoneAlerts: (map['allow_lost_phone_alerts'] as int) == 1,
      );
    }).toList();
  }
}
