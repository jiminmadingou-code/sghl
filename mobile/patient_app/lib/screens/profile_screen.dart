import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  Map<String, dynamic>? _patient;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final userDataStr = await secureStorage.read(key: 'user_data');
      Map<String, dynamic>? user;
      if (userDataStr != null) {
        try {
          user = jsonDecode(userDataStr) as Map<String, dynamic>;
        } catch (_) {
          user = {'username': userDataStr};
        }
      }

      try {
        final profile = await apiService.getMyProfile();
        if (mounted) setState(() { _user = user; _patient = profile; _loading = false; });
      } catch (_) {
        if (mounted) setState(() { _user = user; _loading = false; });
      }
    } catch (e) {
      if (mounted) setState(() { _error = 'Impossible de charger le profil.'; _loading = false; });
    }
  }

  String _getFullName() {
    if (_patient != null) {
      final prenom = (_patient!['prenom'] ?? '').toString();
      final nom = (_patient!['nom'] ?? '').toString();
      if (prenom.isNotEmpty || nom.isNotEmpty) return '$prenom $nom'.trim();
    }
    if (_user != null) {
      final fn = _user!['full_name']?.toString() ?? '';
      if (fn.isNotEmpty) return fn;
      final first = _user!['first_name']?.toString() ?? '';
      final last = _user!['last_name']?.toString() ?? '';
      if (first.isNotEmpty || last.isNotEmpty) return '$first $last'.trim();
      return _user!['username']?.toString() ?? 'Patient';
    }
    return 'Patient';
  }

  String _getEmail() {
    if (_user != null && _user!['email'] != null) return _user!['email'].toString();
    return '';
  }

  String _getPatientNumber() {
    if (_patient != null && _patient!['id'] != null) return 'N° ${_patient!['id']}';
    return '';
  }

  String _getAge() {
    if (_patient != null && _patient!['date_naissance'] != null) {
      try {
        final raw = _patient!['date_naissance'].toString();
        DateTime? dob;
        if (raw.contains('-')) {
          dob = DateTime.parse(raw);
        } else if (raw.contains('/')) {
          final p = raw.split('/');
          dob = DateTime(int.parse(p[2]), int.parse(p[1]), int.parse(p[0]));
        }
        if (dob != null) {
          final age = DateTime.now().year - dob.year;
          return '$age ans';
        }
      } catch (_) {}
    }
    return '---';
  }

  String _getGender() {
    if (_patient != null) {
      final sexe = (_patient!['sexe'] ?? '').toString();
      if (sexe == 'F') return 'Féminin';
      if (sexe == 'M') return 'Masculin';
    }
    return '---';
  }

  String _getBloodType() {
    if (_patient != null && (_patient!['groupe_sanguin'] ?? '').toString().isNotEmpty) {
      return _patient!['groupe_sanguin'].toString();
    }
    return '---';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(title: const Text('Mon Profil')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  const Icon(Icons.error_outline, size: 48, color: Color(0xFFDC2626)),
                  const SizedBox(height: 16),
                  Text(_error!, style: const TextStyle(color: Color(0xFFDC2626))),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: () => setState(() { _loading = true; _error = null; _loadData(); }), child: const Text('Réessayer')),
                ]))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(children: [
                    // Carte profil
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
                      child: Column(children: [
                        CircleAvatar(
                          radius: 40,
                          backgroundColor: const Color(0xFFEFF6FF),
                          child: Text(
                            _getFullName().isNotEmpty ? _getFullName()[0].toUpperCase() : 'P',
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(_getFullName(), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
                        if (_getEmail().isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(_getEmail(), style: const TextStyle(fontSize: 13, color: Color(0xFF6B7280))),
                        ],
                        if (_getPatientNumber().isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Text(_getPatientNumber(), style: const TextStyle(fontSize: 12, color: Color(0xFF9CA3AF))),
                        ],
                        const SizedBox(height: 14),
                        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                          _InfoChip(label: _getBloodType(), icon: Icons.water_drop, color: const Color(0xFFDC2626)),
                          const SizedBox(width: 8),
                          _InfoChip(label: _getAge(), icon: Icons.cake, color: const Color(0xFF7C3AED)),
                          const SizedBox(width: 8),
                          _InfoChip(label: _getGender(), icon: Icons.person, color: const Color(0xFF2563EB)),
                        ]),
                      ]),
                    ),
                    const SizedBox(height: 16),
                    _MenuSection(title: 'Mon dossier médical', items: [
                      _MenuItem(icon: Icons.history, label: 'Historique médical', color: const Color(0xFF2563EB), onTap: () {}),
                      _MenuItem(icon: Icons.vaccines, label: 'Allergies & antécédents', color: const Color(0xFFDC2626), onTap: () {}),
                      _MenuItem(icon: Icons.local_hospital, label: 'Mes hospitalisations', color: const Color(0xFF7C3AED), onTap: () {}),
                    ]),
                    const SizedBox(height: 12),
                    _MenuSection(title: 'Paramètres', items: [
                      _MenuItem(icon: Icons.notifications, label: 'Notifications', color: const Color(0xFFD97706), onTap: () {}),
                      _MenuItem(icon: Icons.security, label: 'Sécurité & Confidentialité', color: const Color(0xFF059669), onTap: () {}),
                      _MenuItem(icon: Icons.gavel, label: 'Consentements RGPD', color: const Color(0xFF6B7280), onTap: () {}),
                      _MenuItem(icon: Icons.help_outline, label: 'Aide & Support', color: const Color(0xFF0891B2), onTap: () {}),
                    ]),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          await apiService.logout();
                          if (context.mounted) context.go('/login');
                        },
                        icon: const Icon(Icons.logout, color: Color(0xFFDC2626)),
                        label: const Text('Se déconnecter', style: TextStyle(color: Color(0xFFDC2626))),
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: Color(0xFFFCA5A5)),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text('CHU SGHL v1.0.0 · Données sécurisées HDS', style: TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
                  ]),
                ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  const _InfoChip({required this.label, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Icon(icon, size: 12, color: color),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
      ]),
    );
  }
}

class _MenuSection extends StatelessWidget {
  final String title;
  final List<_MenuItem> items;
  const _MenuSection({required this.title, required this.items});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 4),
          child: Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF6B7280), letterSpacing: 0.5)),
        ),
        ...items.map((item) => Column(children: [
          const Divider(height: 1, indent: 16),
          ListTile(
            leading: Container(
              width: 36, height: 36,
              decoration: BoxDecoration(color: item.color.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
              child: Icon(item.icon, color: item.color, size: 18),
            ),
            title: Text(item.label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
            trailing: const Icon(Icons.chevron_right, color: Color(0xFFD1D5DB), size: 18),
            onTap: item.onTap,
            dense: true,
          ),
        ])),
      ]),
    );
  }
}

class _MenuItem {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _MenuItem({required this.icon, required this.label, required this.color, required this.onTap});
}
