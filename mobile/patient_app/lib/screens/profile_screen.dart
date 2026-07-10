import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> with SingleTickerProviderStateMixin {
  Map<String, dynamic>? _user;
  Map<String, dynamic>? _patient;
  bool _loading = true;
  late AnimationController _animCtrl;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut);
    _loadData();
  }

  @override
  void dispose() { _animCtrl.dispose(); super.dispose(); }

  Future<void> _loadData() async {
    try {
      final s = await secureStorage.read(key: 'user_data');
      Map<String, dynamic>? user;
      if (s != null) {
        try { user = jsonDecode(s) as Map<String, dynamic>; } catch (_) {}
      }
      try {
        final profile = await apiService.getMyProfile();
        if (mounted) setState(() { _user = user; _patient = profile; _loading = false; });
      } catch (_) {
        if (mounted) setState(() { _user = user; _loading = false; });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
    _animCtrl.forward();
  }

  String get _fullName {
    if (_patient != null) {
      final p = '${_patient!['prenom'] ?? ''} ${_patient!['nom'] ?? ''}'.trim();
      if (p.isNotEmpty) return p;
    }
    if (_user != null) {
      final fn = _user!['full_name']?.toString() ?? '';
      if (fn.isNotEmpty) return fn;
      final p = '${_user!['first_name'] ?? ''} ${_user!['last_name'] ?? ''}'.trim();
      if (p.isNotEmpty) return p;
      return _user!['username']?.toString() ?? 'Patient';
    }
    return 'Patient';
  }

  String get _email => _user?['email']?.toString() ?? '';
  String get _initiale => _fullName.isNotEmpty ? _fullName[0].toUpperCase() : 'P';

  String get _age {
    final raw = _patient?['date_naissance']?.toString() ?? '';
    if (raw.isEmpty) return '---';
    try {
      final dob = raw.contains('-') ? DateTime.parse(raw) : DateTime(int.parse(raw.split('/')[2]), int.parse(raw.split('/')[1]), int.parse(raw.split('/')[0]));
      return '${DateTime.now().year - dob.year} ans';
    } catch (_) { return '---'; }
  }

  String get _sexe {
    final s = _patient?['sexe']?.toString() ?? '';
    return s == 'F' ? 'Féminin' : s == 'M' ? 'Masculin' : '---';
  }

  String get _bloodType => _patient?['groupe_sanguin']?.toString().isNotEmpty == true ? _patient!['groupe_sanguin'].toString() : 'A+';
  String get _patientId => _patient?['id'] != null ? 'PAT-${_patient!['id'].toString().padLeft(4, '0')}' : 'PAT-0001';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF818CF8)))
          : FadeTransition(
              opacity: _fadeAnim,
              child: CustomScrollView(slivers: [
                _buildHeader(),
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
                  sliver: SliverList(delegate: SliverChildListDelegate([
                    const SizedBox(height: 20),
                    _buildInfoCards(),
                    const SizedBox(height: 20),
                    _buildMedicalTimeline(),
                    const SizedBox(height: 20),
                    _buildMenuSection('Mon dossier médical', [
                      _ProfItem(Icons.history_rounded, 'Historique médical', const Color(0xFF818CF8), () {}),
                      _ProfItem(Icons.vaccines_rounded, 'Allergies & antécédents', const Color(0xFFF87171), () {}),
                      _ProfItem(Icons.local_hospital_rounded, 'Mes hospitalisations', const Color(0xFFA78BFA), () {}),
                      _ProfItem(Icons.monitor_heart_rounded, 'Constantes vitales', const Color(0xFF34D399), () => context.go('/vitals')),
                    ]),
                    const SizedBox(height: 14),
                    _buildMenuSection('Paramètres', [
                      _ProfItem(Icons.notifications_rounded, 'Notifications', const Color(0xFFFBBF24), () {}),
                      _ProfItem(Icons.security_rounded, 'Sécurité & Confidentialité', const Color(0xFF34D399), () {}),
                      _ProfItem(Icons.gavel_rounded, 'Consentements RGPD', const Color(0xFF818CF8), () {}),
                      _ProfItem(Icons.help_outline_rounded, 'Aide & Support', const Color(0xFF38BDF8), () {}),
                    ]),
                    const SizedBox(height: 20),
                    _buildLogoutBtn(),
                    const SizedBox(height: 16),
                    Center(child: Text('CHU SGHL v1.0.0 · Données chiffrées AES-256 · HDS',
                        style: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 10))),
                  ])),
                ),
              ]),
            ),
    );
  }

  Widget _buildHeader() {
    return SliverAppBar(
      expandedHeight: 240,
      pinned: true,
      backgroundColor: const Color(0xFF0F0C29),
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft, end: Alignment.bottomRight,
              colors: [Color(0xFF0F0C29), Color(0xFF302B63)],
            ),
          ),
          child: SafeArea(
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              const SizedBox(height: 20),
              Container(
                width: 90, height: 90,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                  borderRadius: BorderRadius.circular(28),
                  boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.5), blurRadius: 24, offset: const Offset(0, 8))],
                ),
                child: Center(child: Text(_initiale, style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.w800))),
              ),
              const SizedBox(height: 14),
              Text(_fullName, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
              const SizedBox(height: 4),
              Text(_email, style: TextStyle(color: Colors.white.withValues(alpha: 0.55), fontSize: 13)),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
                decoration: BoxDecoration(
                  color: const Color(0xFF6366F1).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.4)),
                ),
                child: Text(_patientId, style: const TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
              ),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoCards() {
    final items = [
      {'label': 'Âge', 'value': _age, 'icon': Icons.cake_rounded, 'color': const Color(0xFFA78BFA)},
      {'label': 'Sexe', 'value': _sexe, 'icon': Icons.person_rounded, 'color': const Color(0xFF818CF8)},
      {'label': 'Groupe', 'value': _bloodType, 'icon': Icons.water_drop_rounded, 'color': const Color(0xFFF87171)},
    ];
    return Row(children: items.map((item) => Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1740),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: (item['color'] as Color).withValues(alpha: 0.25)),
        ),
        child: Column(children: [
          Icon(item['icon'] as IconData, color: item['color'] as Color, size: 22),
          const SizedBox(height: 6),
          Text(item['value'] as String, style: TextStyle(color: item['color'] as Color, fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 2),
          Text(item['label'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 10)),
        ]),
      ),
    )).toList());
  }

  Widget _buildMedicalTimeline() {
    final events = [
      {'titre': 'Consultation Médecine interne', 'date': '12/06/2025', 'color': const Color(0xFF818CF8)},
      {'titre': 'Résultat NFS validé', 'date': '10/06/2025', 'color': const Color(0xFF34D399)},
      {'titre': 'Ordonnance renouvelée', 'date': '05/06/2025', 'color': const Color(0xFFA78BFA)},
    ];
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.07)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(width: 32, height: 32, decoration: BoxDecoration(color: const Color(0xFF818CF8).withValues(alpha: 0.15), borderRadius: BorderRadius.circular(10)),
              child: const Icon(Icons.timeline_rounded, color: Color(0xFF818CF8), size: 16)),
          const SizedBox(width: 10),
          const Text('Historique récent', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700)),
        ]),
        const SizedBox(height: 16),
        ...events.asMap().entries.map((e) => Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Column(children: [
            Container(width: 12, height: 12, decoration: BoxDecoration(color: e.value['color'] as Color, shape: BoxShape.circle)),
            if (e.key < events.length - 1) Container(width: 2, height: 32, color: Colors.white.withValues(alpha: 0.1)),
          ]),
          const SizedBox(width: 14),
          Expanded(child: Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(e.value['titre'] as String, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
              const SizedBox(height: 2),
              Text(e.value['date'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
            ]),
          )),
        ])),
      ]),
    );
  }

  Widget _buildMenuSection(String title, List<_ProfItem> items) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.07)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(18, 16, 18, 8),
          child: Text(title, style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.8)),
        ),
        ...items.map((item) => Column(children: [
          Divider(height: 1, color: Colors.white.withValues(alpha: 0.06), indent: 18),
          ListTile(
            leading: Container(
              width: 38, height: 38,
              decoration: BoxDecoration(color: item.color.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(12)),
              child: Icon(item.icon, color: item.color, size: 18),
            ),
            title: Text(item.label, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w500)),
            trailing: Icon(Icons.chevron_right_rounded, color: Colors.white.withValues(alpha: 0.3), size: 20),
            onTap: item.onTap,
            dense: true,
          ),
        ])),
      ]),
    );
  }

  Widget _buildLogoutBtn() {
    return GestureDetector(
      onTap: () async {
        await apiService.logout();
        if (mounted) context.go('/login');
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: const Color(0xFFF87171).withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFF87171).withValues(alpha: 0.3)),
        ),
        child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.logout_rounded, color: Color(0xFFF87171), size: 18),
          SizedBox(width: 10),
          Text('Se déconnecter', style: TextStyle(color: Color(0xFFF87171), fontSize: 15, fontWeight: FontWeight.w700)),
        ]),
      ),
    );
  }
}

class _ProfItem {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _ProfItem(this.icon, this.label, this.color, this.onTap);
}
