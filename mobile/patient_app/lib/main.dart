import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
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
import 'screens/register_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (!kIsWeb) {
    SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ));
  }
  runApp(const ProviderScope(child: SGHLPatientApp()));
}

final _router = GoRouter(
  initialLocation: '/splash',
  // Supprime le # dans l'URL sur web
  routerNeglect: false,
  routes: [
    GoRoute(path: '/splash',        builder: (_, __) => const SplashScreen()),
    GoRoute(path: '/login',         builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/register',      builder: (_, __) => const RegisterScreen()),
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
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.light,
        ),
        textTheme: GoogleFonts.interTextTheme(),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF6366F1),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF6366F1),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          color: Colors.white,
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFF6366F1), width: 2),
          ),
          filled: true,
          fillColor: const Color(0xFFF8F9FF),
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
    (path: '/home',          icon: Icons.home_outlined,           activeIcon: Icons.home_rounded,            label: 'Accueil'),
    (path: '/appointments',  icon: Icons.calendar_today_outlined,  activeIcon: Icons.calendar_today_rounded,  label: 'RDV'),
    (path: '/results',       icon: Icons.science_outlined,         activeIcon: Icons.science_rounded,         label: 'Résultats'),
    (path: '/prescriptions', icon: Icons.medication_outlined,      activeIcon: Icons.medication_rounded,      label: 'Ordonnances'),
    (path: '/chat',          icon: Icons.chat_bubble_outline,      activeIcon: Icons.chat_bubble_rounded,     label: 'Messages'),
  ];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final currentPath = GoRouterState.of(context).matchedLocation;
    final index = _tabs.indexWhere((t) => currentPath == t.path || currentPath.startsWith(t.path));
    if (index != -1 && index != _currentIndex) setState(() => _currentIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.child,
      extendBody: true,
      bottomNavigationBar: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 20),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1740),
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
          boxShadow: [
            BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.2), blurRadius: 24, offset: const Offset(0, 8)),
            BoxShadow(color: Colors.black.withValues(alpha: 0.4), blurRadius: 16, offset: const Offset(0, 4)),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: _tabs.asMap().entries.map((e) {
              final i = e.key;
              final t = e.value;
              final selected = _currentIndex == i;
              return GestureDetector(
                onTap: () { setState(() => _currentIndex = i); context.go(t.path); },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 250),
                  curve: Curves.easeInOut,
                  padding: EdgeInsets.symmetric(horizontal: selected ? 16 : 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: selected ? const Color(0xFF6366F1).withValues(alpha: 0.2) : Colors.transparent,
                    borderRadius: BorderRadius.circular(16),
                    border: selected ? Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.4)) : null,
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    Icon(selected ? t.activeIcon : t.icon,
                        color: selected ? const Color(0xFF818CF8) : Colors.white38, size: 22),
                    if (selected) ...[
                      const SizedBox(width: 6),
                      Text(t.label, style: const TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.w700)),
                    ],
                  ]),
                ),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }
}
