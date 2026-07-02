import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'screens/appointments_screen.dart';
import 'screens/results_screen.dart';
import 'screens/prescriptions_screen.dart';
import 'screens/invoices_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/vitals_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));
  runApp(const ProviderScope(child: SGHLPatientApp()));
}

final _router = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(path: '/splash',        builder: (_, __) => const SplashScreen()),
    GoRoute(path: '/login',         builder: (_, __) => const LoginScreen()),
    ShellRoute(
      builder: (context, state, child) => MainShell(child: child),
      routes: [
        GoRoute(path: '/home',          builder: (_, __) => const HomeScreen()),
        GoRoute(path: '/appointments',  builder: (_, __) => const AppointmentsScreen()),
        GoRoute(path: '/results',       builder: (_, __) => const ResultsScreen()),
        GoRoute(path: '/prescriptions', builder: (_, __) => const PrescriptionsScreen()),
        GoRoute(path: '/invoices',      builder: (_, __) => const InvoicesScreen()),
        GoRoute(path: '/chat',          builder: (_, __) => const ChatScreen()),
        GoRoute(path: '/vitals',        builder: (_, __) => const VitalsScreen()),
        GoRoute(path: '/profile',       builder: (_, __) => const ProfileScreen()),
      ],
    ),
  ],
);

class SGHLPatientApp extends StatelessWidget {
  const SGHLPatientApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'CHU — Espace Patient',
      debugShowCheckedModeBanner: false,
      routerConfig: _router,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1D4ED8),
          brightness: Brightness.light,
        ),
        textTheme: GoogleFonts.sourceCodeProTextTheme(),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1D4ED8),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF2563EB),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),
        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          color: Colors.white,
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFF2563EB), width: 2),
          ),
          filled: true,
          fillColor: const Color(0xFFF8FAFF),
        ),
      ),
    );
  }
}

class MainShell extends StatefulWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;

  final _tabs = [
    (path: '/home',          icon: Icons.home_outlined,         activeIcon: Icons.home,              label: 'Accueil'),
    (path: '/appointments',  icon: Icons.calendar_today_outlined,activeIcon: Icons.calendar_today,   label: 'RDV'),
    (path: '/results',       icon: Icons.science_outlined,       activeIcon: Icons.science,           label: 'Résultats'),
    (path: '/prescriptions', icon: Icons.medication_outlined,    activeIcon: Icons.medication,        label: 'Ordonnances'),
    (path: '/chat',          icon: Icons.chat_bubble_outline,    activeIcon: Icons.chat_bubble,       label: 'Messages'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) {
          setState(() => _currentIndex = i);
          context.go(_tabs[i].path);
        },
        backgroundColor: Colors.white,
        elevation: 8,
        destinations: _tabs.map((t) => NavigationDestination(
          icon: Icon(t.icon),
          selectedIcon: Icon(t.activeIcon, color: const Color(0xFF2563EB)),
          label: t.label,
        )).toList(),
      ),
    );
  }
}
