import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';
import '../services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _nomCtrl = TextEditingController();
  final _prenomCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _telCtrl = TextEditingController();
  final _dateCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  String _sexe = 'M';
  bool _loading = false;
  bool _obscure = true;
  bool _obscureConfirm = true;
  String? _error;
  late AnimationController _animCtrl;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 700));
    _fadeAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _animCtrl.forward();
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _nomCtrl.dispose(); _prenomCtrl.dispose(); _emailCtrl.dispose();
    _telCtrl.dispose(); _dateCtrl.dispose(); _passCtrl.dispose(); _confirmCtrl.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _error = null; });
    try {
      final response = await Dio(BaseOptions(
        baseUrl: 'https://sghl-production.up.railway.app/api/v1',
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 20),
      )).post('/auth/register/', data: {
        'password': _passCtrl.text,
        'confirm_password': _confirmCtrl.text,
        'nom': _nomCtrl.text.trim(),
        'prenom': _prenomCtrl.text.trim(),
        'email': _emailCtrl.text.trim().toLowerCase(),
        'telephone': _telCtrl.text.trim(),
        'date_naissance': _dateCtrl.text.trim(),
        'sexe': _sexe,
      });
      if (response.statusCode == 201) {
        final data = response.data;
        if (data['access'] != null) await secureStorage.write(key: 'access_token', value: data['access']);
        if (data['refresh'] != null) await secureStorage.write(key: 'refresh_token', value: data['refresh']);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ Compte créé avec succès !'),
              backgroundColor: Color(0xFF059669),
              behavior: SnackBarBehavior.floating,
            ),
          );
          context.go('/home');
        }
      }
    } on DioException catch (e) {
      String msg = 'Erreur d\'inscription. Veuillez réessayer.';
      if (e.response?.data is Map) {
        final err = e.response!.data;
        if (err['error'] != null) msg = err['error'];
        else if (err.containsKey('email')) msg = 'Cet email est déjà utilisé.';
      } else if (e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout) {
        msg = 'Délai dépassé. Vérifiez votre connexion.';
      }
      setState(() => _error = msg);
    } catch (_) {
      setState(() => _error = 'Erreur de connexion au serveur.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  InputDecoration _inputDeco(String label, IconData icon) => InputDecoration(
    labelText: label,
    prefixIcon: Icon(icon, color: const Color(0xFF6366F1), size: 20),
    filled: true,
    fillColor: const Color(0xFFF8F9FF),
    labelStyle: const TextStyle(color: Color(0xFF6B7280), fontSize: 14),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE5E7EB))),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE5E7EB))),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFF6366F1), width: 2)),
    errorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFEF4444))),
    focusedErrorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFEF4444), width: 2)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0F0C29), Color(0xFF302B63), Color(0xFF24243E)],
          ),
        ),
        child: SafeArea(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              child: Column(
                children: [
                  // Header
                  Row(
                    children: [
                      GestureDetector(
                        onTap: () => context.go('/login'),
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 18),
                        ),
                      ),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text('Nouveau compte', style: TextStyle(color: Colors.white70, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Logo
                  Container(
                    width: 72, height: 72,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withOpacity(0.4), blurRadius: 20, offset: const Offset(0, 8))],
                    ),
                    child: const Icon(Icons.health_and_safety_rounded, size: 38, color: Colors.white),
                  ),
                  const SizedBox(height: 14),
                  const Text('Créer votre compte', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w800, letterSpacing: -0.5)),
                  const SizedBox(height: 4),
                  Text('Rejoignez votre espace santé personnel', style: TextStyle(color: Colors.white.withOpacity(0.55), fontSize: 13)),
                  const SizedBox(height: 28),

                  // Formulaire
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(24),
                      boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 30, offset: const Offset(0, 10))],
                    ),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Nom / Prénom
                          Row(children: [
                            Expanded(
                              child: TextFormField(
                                controller: _nomCtrl,
                                textCapitalization: TextCapitalization.words,
                                decoration: _inputDeco('Nom', Icons.badge_outlined),
                                validator: (v) => v == null || v.isEmpty ? 'Requis' : null,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: TextFormField(
                                controller: _prenomCtrl,
                                textCapitalization: TextCapitalization.words,
                                decoration: _inputDeco('Prénom', Icons.person_outline),
                                validator: (v) => v == null || v.isEmpty ? 'Requis' : null,
                              ),
                            ),
                          ]),
                          const SizedBox(height: 14),

                          // Email
                          TextFormField(
                            controller: _emailCtrl,
                            keyboardType: TextInputType.emailAddress,
                            decoration: _inputDeco('Adresse email', Icons.email_outlined),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Champ requis';
                              if (!RegExp(r'^[\w.-]+@[\w.-]+\.\w+$').hasMatch(v)) return 'Email invalide';
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),

                          // Téléphone
                          TextFormField(
                            controller: _telCtrl,
                            keyboardType: TextInputType.phone,
                            decoration: _inputDeco('Téléphone', Icons.phone_outlined),
                          ),
                          const SizedBox(height: 14),

                          // Date de naissance
                          TextFormField(
                            controller: _dateCtrl,
                            readOnly: true,
                            decoration: _inputDeco('Date de naissance', Icons.calendar_today_outlined),
                            validator: (v) => v == null || v.isEmpty ? 'Champ requis' : null,
                            onTap: () async {
                              final date = await showDatePicker(
                                context: context,
                                initialDate: DateTime(1990),
                                firstDate: DateTime(1920),
                                lastDate: DateTime.now(),
                                builder: (ctx, child) => Theme(
                                  data: ThemeData.light().copyWith(
                                    colorScheme: const ColorScheme.light(primary: Color(0xFF6366F1)),
                                  ),
                                  child: child!,
                                ),
                              );
                              if (date != null) {
                                _dateCtrl.text = '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
                              }
                            },
                          ),
                          const SizedBox(height: 14),

                          // Sexe
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF8F9FF),
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: const Color(0xFFE5E7EB)),
                            ),
                            child: Row(children: [
                              const Icon(Icons.wc_outlined, color: Color(0xFF6366F1), size: 20),
                              const SizedBox(width: 10),
                              const Text('Sexe', style: TextStyle(color: Color(0xFF6B7280), fontSize: 14)),
                              const Spacer(),
                              _SexeChip(label: 'Masculin', value: 'M', selected: _sexe == 'M', onTap: () => setState(() => _sexe = 'M')),
                              const SizedBox(width: 8),
                              _SexeChip(label: 'Féminin', value: 'F', selected: _sexe == 'F', onTap: () => setState(() => _sexe = 'F')),
                            ]),
                          ),
                          const SizedBox(height: 14),

                          // Mot de passe
                          TextFormField(
                            controller: _passCtrl,
                            obscureText: _obscure,
                            decoration: _inputDeco('Mot de passe', Icons.lock_outline).copyWith(
                              suffixIcon: IconButton(
                                icon: Icon(_obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined, color: const Color(0xFF9CA3AF), size: 20),
                                onPressed: () => setState(() => _obscure = !_obscure),
                              ),
                            ),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Champ requis';
                              if (v.length < 6) return 'Minimum 6 caractères';
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),

                          // Confirmer mot de passe
                          TextFormField(
                            controller: _confirmCtrl,
                            obscureText: _obscureConfirm,
                            decoration: _inputDeco('Confirmer le mot de passe', Icons.lock_outline).copyWith(
                              suffixIcon: IconButton(
                                icon: Icon(_obscureConfirm ? Icons.visibility_off_outlined : Icons.visibility_outlined, color: const Color(0xFF9CA3AF), size: 20),
                                onPressed: () => setState(() => _obscureConfirm = !_obscureConfirm),
                              ),
                            ),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Champ requis';
                              if (v != _passCtrl.text) return 'Les mots de passe ne correspondent pas';
                              return null;
                            },
                          ),

                          // Erreur
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

                          const SizedBox(height: 22),

                          // Bouton
                          SizedBox(
                            height: 52,
                            child: ElevatedButton(
                              onPressed: _loading ? null : _register,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF6366F1),
                                foregroundColor: Colors.white,
                                disabledBackgroundColor: const Color(0xFF6366F1).withOpacity(0.6),
                                elevation: 0,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                              ),
                              child: _loading
                                  ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                                  : const Text('Créer mon compte', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, letterSpacing: 0.3)),
                            ),
                          ),
                          const SizedBox(height: 14),

                          Center(
                            child: TextButton(
                              onPressed: () => context.go('/login'),
                              child: RichText(
                                text: const TextSpan(
                                  text: 'Déjà inscrit ? ',
                                  style: TextStyle(color: Color(0xFF6B7280), fontSize: 14),
                                  children: [TextSpan(text: 'Se connecter', style: TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.w700))],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.shield_outlined, color: Colors.white.withOpacity(0.4), size: 14),
                      const SizedBox(width: 6),
                      Text('Données chiffrées · Conformité RGPD', style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 11)),
                    ],
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SexeChip extends StatelessWidget {
  final String label, value;
  final bool selected;
  final VoidCallback onTap;
  const _SexeChip({required this.label, required this.value, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF6366F1) : const Color(0xFFE5E7EB),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(label, style: TextStyle(color: selected ? Colors.white : const Color(0xFF6B7280), fontSize: 12, fontWeight: FontWeight.w600)),
      ),
    );
  }
}
