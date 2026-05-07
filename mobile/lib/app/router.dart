import 'package:flutter/material.dart';
import '../features/auth/presentation/auth_gate.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/auth/presentation/signup_screen.dart';
import '../features/home/home_screen.dart';
import '../features/trusted_contacts/presentation/contacts_screen.dart';

class AppRouter {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/':
        return MaterialPageRoute(builder: (_) => const AuthGate());
      case '/login':
        return MaterialPageRoute(builder: (_) => const LoginScreen());
      case '/signup':
        return MaterialPageRoute(builder: (_) => const SignupScreen());
      case '/home':
        return MaterialPageRoute(builder: (_) => const HomeScreen());
      case '/trusted-contacts':
        return MaterialPageRoute(builder: (_) => const ContactsScreen());
      default:
        return MaterialPageRoute(
          builder: (_) => Scaffold(
            body: Center(child: Text('No route defined for ${settings.name}')),
          ),
        );
    }
  }
}
