import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  String _prenom = '';
  bool _loading = true;
  late AnimationController _fadeCtrl;
  late Animation<double> _fadeAnim;

  // Données démo enrichies
  final _stats = [
    {'label': 'RDV ce mois', 'value': '3', 'icon': Icons.calendar_today, 'color': const Color(0xFF818CF8)},
    {'label': 'Résultats', 'value': '5', 'icon': Icons.science, 'color': const Color(0xFFA78BFA)},
    {'label': 'Ordonnances', 'value': '2', 'icon': Icons.medication, 'color': const Color(0xFF34D399)},
    {'label': 'Messages', 'value': '1', 'icon': Icons.chat_bubble, 'color': const Color(0xFFFBBF24)},
  ];

  final _rappels = [
    {'med': 'Amlodipine 5mg', 'heure': '08:00', 'pris': true, 'couleur': const Color(0xFF818CF8)},
    {'med': 'Metformine 500mg', 'heure': '12:00', 'pris': false, 'couleur': const Color(0xFFFBBF24)},
    {'med': 'Metformine 500mg', 'heure': '20:00', 'pris': false, 'couleur': const Color(0xFFFBBF24)},
  ];

  final _activites = [
    {'titre': 'Résultat NFS disponible', 'sous': 'Validé par Dr. Camara', 'heure': 'Il y a 2h', 'icon': Icons.science, 'color': const Color(0xFF818CF8)},
    {'titre': 'RDV confirmé', 'sous': 'Dr. Bah Mariama — 20/06', 'heure': 'Hier', 'icon': Icons.check_circle, 'color': const Color(0xFF34D399)},
    {'titre': 'Ordonnance renouvelée', 'sous': 'Amlodipine + Metformine', 'heure': '12/06', 'icon': Icons.description, 'color': const Color(0xFFA78BFA)},
  ];

  @override
  void initState() {
    super.initState();
    _fadeCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 800));
    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);
    _load();
  }

  @override
  void dispose() { _fadeCtrl.dispose(); super.dispose(); }

  Future<void> _load() async {
    try {
      final s = await secureStorage.read(key: 'user_data');
      if (s != null) {
        final u = jsonDecode(s) as Map<String, dynamic>;
        final fn = u['first_name']?.toString() ?? '';
        final full = u['full_name']?.toString() ?? '';
        if (mounted) setState(() => _prenom = fn.isNotEmpty ? fn : full.split(' ').first);
      }
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
    _fadeCtrl.forward();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      body: FadeTransition(
        opacity: _fadeAnim,
        child: CustomScrollView(
          slivers: [
            _buildHeader(),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
              sliver: SliverList(delegate: SliverChildListDelegate([
                const SizedBox(height: 20),
                _buildStatsRow(),
                const SizedBox(height: 24),
                _buildNextRdv(),
                const SizedBox(height: 20),
                _buildQuickActions(),
                const SizedBox(height: 20),
                _buildRappels(),
                const SizedBox(height: 20),
                _buildActivites(),
                const SizedBox(height: 20),
                _buildSanteScore(),
              ])),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return SliverAppBar(
      expandedHeight: 180,
      pinned: true,
      backgroundColor: const Color(0xFF0F0C29),
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft, end: Alignment.bottomRight,
              colors: [Color(0xFF0F0C29), Color(0xFF302B63), Color(0xFF24243E)],
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Row(children: [
                    Container(
                      width: 50, height: 50,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.4), blurRadius: 12, offset: const Offset(0, 4))],
                      ),
                      child: Center(
                        child: Text(
                          _prenom.isNotEmpty ? _prenom[0].toUpperCase() : 'P',
                          style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800),
                        ),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Bonjour,', style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 13)),
                        Text(
                          _prenom.isNotEmpty ? _prenom : 'Mon Espace Santé',
                          style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800),
                        ),
                      ],
                    )),
                    _NotifBadge(),
                  ]),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
                    ),
                    child: Row(children: [
                      const Icon(Icons.shield_outlined, color: Color(0xFF818CF8), size: 16),
                      const SizedBox(width: 8),
                      Text('Dossier sécurisé · Conformité RGPD', style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 12)),
                      const Spacer(),
                      Container(
                        width: 8, height: 8,
                        decoration: const BoxDecoration(color: Color(0xFF34D399), shape: BoxShape.circle),
                      ),
                      const SizedBox(width: 6),
                      Text('En ligne', style: TextStyle(color: const Color(0xFF34D399), fontSize: 11, fontWeight: FontWeight.w600)),
                    ]),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatsRow() {
    return Row(
      children: _stats.map((s) => Expanded(
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
          decoration: BoxDecoration(
            color: const Color(0xFF1A1740),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: (s['color'] as Color).withValues(alpha: 0.2)),
          ),
          child: Column(children: [
            Icon(s['icon'] as IconData, color: s['color'] as Color, size: 22),
            const SizedBox(height: 6),
            Text(s['value'] as String, style: TextStyle(color: s['color'] as Color, fontSize: 18, fontWeight: FontWeight.w800)),
            const SizedBox(height: 2),
            Text(s['label'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 9), textAlign: TextAlign.center),
          ]),
        ),
      )).toList(),
    );
  }

  Widget _buildNextRdv() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft, end: Alignment.bottomRight,
          colors: [Color(0xFF4F46E5), Color(0xFF7C3AED)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.4), blurRadius: 20, offset: const Offset(0, 8))],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.calendar_today, color: Colors.white70, size: 14),
          const SizedBox(width: 6),
          Text('PROCHAIN RENDEZ-VOUS', style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 1)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(20)),
            child: const Text('Demain', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700)),
          ),
        ]),
        const SizedBox(height: 14),
        Row(children: [
          Container(
            width: 52, height: 52,
            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(16)),
            child: const Icon(Icons.person, color: Colors.white, size: 28),
          ),
          const SizedBox(width: 14),
          const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Dr. Camara Alpha', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w800)),
            SizedBox(height: 2),
            Text('Médecine interne · CHU SGHL', style: TextStyle(color: Colors.white70, fontSize: 12)),
            SizedBox(height: 6),
            Row(children: [
              Icon(Icons.access_time, color: Colors.white60, size: 13),
              SizedBox(width: 4),
              Text('10h00 — Salle 204', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
            ]),
          ])),
        ]),
        const SizedBox(height: 14),
        Row(children: [
          Expanded(child: GestureDetector(
            onTap: () => context.go('/appointments'),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(12)),
              child: const Center(child: Text('Voir détails', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 13))),
            ),
          )),
          const SizedBox(width: 10),
          Expanded(child: Container(
            padding: const EdgeInsets.symmetric(vertical: 10),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
            child: const Center(child: Text('Confirmer', style: TextStyle(color: Color(0xFF4F46E5), fontWeight: FontWeight.w700, fontSize: 13))),
          )),
        ]),
      ]),
    );
  }

  Widget _buildQuickActions() {
    final actions = [
      {'icon': Icons.calendar_today_rounded, 'label': 'Rendez-vous', 'color': const Color(0xFF818CF8), 'path': '/appointments',
       'image': '🗓️', 'bg': const Color(0xFF3730A3)},
      {'icon': Icons.science_rounded, 'label': 'Résultats', 'color': const Color(0xFFA78BFA), 'path': '/results',
       'image': '🔬', 'bg': const Color(0xFF5B21B6)},
      {'icon': Icons.medication_rounded, 'label': 'Ordonnances', 'color': const Color(0xFF34D399), 'path': '/prescriptions',
       'image': '💊', 'bg': const Color(0xFF065F46)},
      {'icon': Icons.receipt_long_rounded, 'label': 'Factures', 'color': const Color(0xFFFBBF24), 'path': '/invoices',
       'image': '🧾', 'bg': const Color(0xFF92400E)},
      {'icon': Icons.chat_bubble_rounded, 'label': 'Messages', 'color': const Color(0xFF38BDF8), 'path': '/chat',
       'image': '💬', 'bg': const Color(0xFF0C4A6E)},
      {'icon': Icons.monitor_heart_rounded, 'label': 'Constantes', 'color': const Color(0xFFF87171), 'path': '/vitals',
       'image': '❤️', 'bg': const Color(0xFF7F1D1D)},
    ];
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _sectionTitle('Accès rapides', Icons.grid_view_rounded),
      const SizedBox(height: 12),
      GridView.count(
        crossAxisCount: 3, shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: 0.95,
        children: actions.map((a) => GestureDetector(
          onTap: () => context.go(a['path'] as String),
          child: Container(
            decoration: BoxDecoration(
              color: const Color(0xFF1A1740),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: (a['color'] as Color).withValues(alpha: 0.25)),
              boxShadow: [BoxShadow(color: (a['color'] as Color).withValues(alpha: 0.1), blurRadius: 12, offset: const Offset(0, 4))],
            ),
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Container(
                width: 40, height: 40,
                decoration: BoxDecoration(
                  color: (a['bg'] as Color).withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: (a['color'] as Color).withValues(alpha: 0.3)),
                ),
                child: Center(child: Text(a['image'] as String, style: const TextStyle(fontSize: 18))),
              ),
              const SizedBox(height: 9),
              Text(a['label'] as String, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600), textAlign: TextAlign.center),
            ]),
          ),
        )).toList(),
      ),
    ]);
  }

  Widget _buildRappels() {
    return _DarkCard(
      title: 'Rappels médicamenteux',
      icon: Icons.alarm_rounded,
      iconColor: const Color(0xFFFBBF24),
      child: Column(children: _rappels.map((r) {
        final pris = r['pris'] as bool;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(children: [
            GestureDetector(
              onTap: () {},
              child: Container(
                width: 28, height: 28,
                decoration: BoxDecoration(
                  color: pris ? const Color(0xFF34D399).withValues(alpha: 0.2) : Colors.white.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: pris ? const Color(0xFF34D399) : Colors.white.withValues(alpha: 0.2)),
                ),
                child: pris ? const Icon(Icons.check, color: Color(0xFF34D399), size: 16) : null,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(r['med'] as String, style: TextStyle(
              color: pris ? Colors.white.withValues(alpha: 0.4) : Colors.white,
              fontSize: 13, fontWeight: FontWeight.w500,
              decoration: pris ? TextDecoration.lineThrough : null,
            ))),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: (r['couleur'] as Color).withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(r['heure'] as String, style: TextStyle(color: r['couleur'] as Color, fontSize: 12, fontWeight: FontWeight.w700)),
            ),
          ]),
        );
      }).toList()),
    );
  }

  Widget _buildActivites() {
    return _DarkCard(
      title: 'Activité récente',
      icon: Icons.history_rounded,
      iconColor: const Color(0xFF818CF8),
      child: Column(children: _activites.map((a) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(children: [
          Container(
            width: 38, height: 38,
            decoration: BoxDecoration(
              color: (a['color'] as Color).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(a['icon'] as IconData, color: a['color'] as Color, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(a['titre'] as String, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
            Text(a['sous'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
          ])),
          Text(a['heure'] as String, style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
        ]),
      )).toList()),
    );
  }

  Widget _buildSanteScore() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF34D399).withValues(alpha: 0.3)),
      ),
      child: Row(children: [
        Stack(alignment: Alignment.center, children: [
          SizedBox(
            width: 72, height: 72,
            child: CircularProgressIndicator(
              value: 0.78,
              strokeWidth: 6,
              backgroundColor: Colors.white.withValues(alpha: 0.1),
              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF34D399)),
            ),
          ),
          const Text('78', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
        ]),
        const SizedBox(width: 18),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('Score de santé', style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text('Bon état général · Suivi régulier recommandé', style: TextStyle(color: Colors.white.withValues(alpha: 0.55), fontSize: 12)),
          const SizedBox(height: 10),
          Row(children: [
            _ScorePill('TA', '120/80', const Color(0xFF34D399)),
            const SizedBox(width: 8),
            _ScorePill('IMC', '24.1', const Color(0xFF818CF8)),
            const SizedBox(width: 8),
            _ScorePill('Glyc.', '1.26', const Color(0xFFFBBF24)),
          ]),
        ])),
      ]),
    );
  }

  Widget _sectionTitle(String title, IconData icon) {
    return Row(children: [
      Icon(icon, color: const Color(0xFF818CF8), size: 18),
      const SizedBox(width: 8),
      Text(title, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700)),
    ]);
  }
}

class _ScorePill extends StatelessWidget {
  final String label, value;
  final Color color;
  const _ScorePill(this.label, this.value, this.color);
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(8)),
      child: Column(children: [
        Text(label, style: TextStyle(color: color.withValues(alpha: 0.7), fontSize: 9, fontWeight: FontWeight.w600)),
        Text(value, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w800)),
      ]),
    );
  }
}

class _NotifBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Stack(children: [
      Container(
        width: 42, height: 42,
        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(12)),
        child: const Icon(Icons.notifications_outlined, color: Colors.white, size: 22),
      ),
      Positioned(right: 8, top: 8, child: Container(
        width: 8, height: 8,
        decoration: const BoxDecoration(color: Color(0xFFF87171), shape: BoxShape.circle),
      )),
    ]);
  }
}

class _DarkCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color iconColor;
  final Widget child;
  const _DarkCard({required this.title, required this.icon, required this.iconColor, required this.child});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.07)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            width: 32, height: 32,
            decoration: BoxDecoration(color: iconColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, color: iconColor, size: 16),
          ),
          const SizedBox(width: 10),
          Text(title, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700)),
        ]),
        const SizedBox(height: 14),
        child,
      ]),
    );
  }
}
