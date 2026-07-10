import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _loading = false;
  bool _obscure = true;
  String? _error;
  late AnimationController _animCtrl;
  late Animation<Offset> _slideAnim;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 800));
    _slideAnim = Tween<Offset>(begin: const Offset(0, 0.15), end: Offset.zero)
        .animate(CurvedAnimation(parent: _animCtrl, curve: Curves.easeOutCubic));
    _fadeAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _animCtrl.forward();
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _emailCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _error = null; });
    try {
      final dio = Dio(BaseOptions(
        baseUrl: 'https://sghl-production.up.railway.app/api/v1',
        connectTimeout: const Duration(seconds: 20),
        receiveTimeout: const Duration(seconds: 30),
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      ));

      final response = await dio.post('/auth/login/', data: {
        'username': _emailCtrl.text.trim().toLowerCase(),
        'password': _passCtrl.text,
      });

      final data = response.data as Map<String, dynamic>;
      if (data['access'] != null) {
        await secureStorage.write(key: 'access_token', value: data['access'].toString());
      }
      if (data['refresh'] != null) {
        await secureStorage.write(key: 'refresh_token', value: data['refresh'].toString());
      }
      if (data['user'] != null) {
        await secureStorage.write(key: 'user_data', value: jsonEncode(data['user']));
      }
      if (mounted) context.go('/home');

    } on DioException catch (e) {
      String msg = 'Erreur de connexion.';
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        msg = 'Délai dépassé. Vérifiez votre connexion internet.';
      } else if (e.type == DioExceptionType.connectionError) {
        msg = 'Impossible de joindre le serveur.';
      } else if (e.response != null) {
        final status = e.response!.statusCode;
        final body = e.response!.data;
        if (status == 401) {
          msg = 'Email ou mot de passe incorrect.';
        } else if (body is Map) {
          msg = body['detail']?.toString() ?? body['error']?.toString() ?? 'Erreur $status.';
        } else {
          msg = 'Erreur serveur ($status).';
        }
      }
      setState(() => _error = msg);
    } catch (e) {
      setState(() => _error = 'Erreur inattendue: ${e.toString()}');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft, end: Alignment.bottomRight,
            colors: [Color(0xFF0F0C29), Color(0xFF302B63), Color(0xFF24243E)],
          ),
        ),
        child: SafeArea(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: Column(children: [
                const SizedBox(height: 50),
                SlideTransition(
                  position: _slideAnim,
                  child: Column(children: [
                    Container(
                      width: 88, height: 88,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.5), blurRadius: 25, offset: const Offset(0, 10))],
                      ),
                      child: const Icon(Icons.local_hospital_rounded, size: 46, color: Colors.white),
                    ),
                    const SizedBox(height: 18),
                    const Text('SGHL', style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.w900, letterSpacing: 2)),
                    const SizedBox(height: 4),
                    Text('Espace Patient', style: TextStyle(color: Colors.white.withValues(alpha: 0.55), fontSize: 14, letterSpacing: 1)),
                  ]),
                ),
                const SizedBox(height: 44),
                SlideTransition(
                  position: _slideAnim,
                  child: Container(
                    padding: const EdgeInsets.all(28),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(28),
                      boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.25), blurRadius: 40, offset: const Offset(0, 15))],
                    ),
                    child: Form(
                      key: _formKey,
                      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                        const Text('Connexion', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
                        const SizedBox(height: 4),
                        const Text('Connectez-vous avec votre email', style: TextStyle(fontSize: 13, color: Color(0xFF9CA3AF))),
                        const SizedBox(height: 24),
                        TextFormField(
                          controller: _emailCtrl,
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.next,
                          decoration: _fieldDeco('Adresse email', Icons.email_outlined),
                          validator: (v) {
                            if (v == null || v.isEmpty) return 'Champ requis';
                            if (!v.contains('@')) return 'Email invalide';
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _passCtrl,
                          obscureText: _obscure,
                          textInputAction: TextInputAction.done,
                          onFieldSubmitted: (_) => _login(),
                          decoration: _fieldDeco('Mot de passe', Icons.lock_outline_rounded).copyWith(
                            suffixIcon: IconButton(
                              icon: Icon(_obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined, color: const Color(0xFF9CA3AF), size: 20),
                              onPressed: () => setState(() => _obscure = !_obscure),
                            ),
                          ),
                          validator: (v) => v == null || v.isEmpty ? 'Champ requis' : null,
                        ),
                        if (_error != null) ...[
                          const SizedBox(height: 14),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFEF2F2),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: const Color(0xFFFECACA)),
                            ),
                            child: Row(children: [
                              const Icon(Icons.error_outline_rounded, color: Color(0xFFEF4444), size: 18),
                              const SizedBox(width: 8),
                              Expanded(child: Text(_error!, style: const TextStyle(color: Color(0xFFDC2626), fontSize: 13))),
                            ]),
                          ),
                        ],
                        const SizedBox(height: 24),
                        SizedBox(
                          height: 54,
                          child: ElevatedButton(
                            onPressed: _loading ? null : _login,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF6366F1),
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                            child: _loading
                                ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                                : const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                    Text('Se connecter', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                                    SizedBox(width: 8),
                                    Icon(Icons.arrow_forward_rounded, size: 18),
                                  ]),
                          ),
                        ),
                        const SizedBox(height: 18),
                        Row(children: [
                          Expanded(child: Divider(color: Colors.grey.shade200)),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            child: Text('ou', style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
                          ),
                          Expanded(child: Divider(color: Colors.grey.shade200)),
                        ]),
                        const SizedBox(height: 16),
                        SizedBox(
                          height: 50,
                          child: OutlinedButton(
                            onPressed: () => context.go('/register'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF6366F1),
                              side: const BorderSide(color: Color(0xFF6366F1), width: 1.5),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                            child: const Text('Créer un compte patient', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                          ),
                        ),
                      ]),
                    ),
                  ),
                ),
                const SizedBox(height: 28),
                Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(Icons.verified_user_outlined, color: Colors.white.withValues(alpha: 0.35), size: 13),
                  const SizedBox(width: 6),
                  Text('Sécurisé · Confidentiel · RGPD', style: TextStyle(color: Colors.white.withValues(alpha: 0.35), fontSize: 11)),
                ]),
                const SizedBox(height: 20),
              ]),
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _fieldDeco(String label, IconData icon) => InputDecoration(
    labelText: label,
    prefixIcon: Icon(icon, color: const Color(0xFF6366F1), size: 20),
    filled: true,
    fillColor: const Color(0xFFF8F9FF),
    labelStyle: const TextStyle(color: Color(0xFF9CA3AF), fontSize: 14),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE5E7EB))),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE5E7EB))),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFF6366F1), width: 2)),
    errorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFEF4444))),
    focusedErrorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFEF4444), width: 2)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
  );
}
