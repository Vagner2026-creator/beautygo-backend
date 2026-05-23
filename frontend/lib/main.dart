import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'core/theme/app_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/category_provider.dart';
import 'providers/professional_provider.dart';
import 'providers/appointment_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/review_provider.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/home/screens/main_shell.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('pt_BR', null);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));
  runApp(const BeautyGoApp());
}

class BeautyGoApp extends StatelessWidget {
  const BeautyGoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => CategoryProvider()),
        ChangeNotifierProvider(create: (_) => ProfessionalProvider()),
        ChangeNotifierProvider(create: (_) => AppointmentProvider()),
        ChangeNotifierProvider(create: (_) => NotificationProvider()),
        ChangeNotifierProvider(create: (_) => ReviewProvider()),
      ],
      child: MaterialApp(
        title: 'BeautyGO',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light,
        home: const _AuthGate(),
      ),
    );
  }
}

class _AuthGate extends StatefulWidget {
  const _AuthGate();

  @override
  State<_AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<_AuthGate> {
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    await context.read<AuthProvider>().checkAuth();
    if (mounted) setState(() => _checking = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.auto_awesome, size: 64, color: AppTheme.primary),
              SizedBox(height: 16),
              Text('BeautyGO', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppTheme.primary)),
              SizedBox(height: 32),
              CircularProgressIndicator(color: AppTheme.primary),
            ],
          ),
        ),
      );
    }

    final isAuth = context.watch<AuthProvider>().isAuthenticated;
    return isAuth ? const MainShell() : const LoginScreen();
  }
}
