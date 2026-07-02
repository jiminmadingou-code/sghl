import 'package:flutter/material.dart';
import 'package:go_router/go_router.go_router.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _summary;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await apiService.getDashboardSummary();
      if (mounted) setState(() { _summary = data; _loading = false; });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 160,
            pinned: true,
            backgroundColor: const Color(0xFF1D4ED8),
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft, end: Alignment.bottomRight,
                    colors: [Color(0xFF0A1628), Color(0xFF1D4ED8)],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 24,
                              backgroundColor: Colors.white.withOpacity(0.2),
                              child: const Icon(Icons.person, color: Colors.white, size: 28),
                            ),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Bonjour,', style: TextStyle(color: Colors.white70, fontSize: 13)),
                                const Text('Mon Espace Santé', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w700)),
                              ],
                            ),
                            const Spacer(),
                            IconButton(
                              icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                              onPressed: () {},
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Accès rapides
                const Text('Accès rapides', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
                const SizedBox(height: 12),
                GridView.count(
                  crossAxisCount: 3,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                  childAspectRatio: 0.9,
                  children: [
                    _QuickAction(icon: Icons.calendar_today, label: 'Rendez-vous', color: const Color(0xFF2563EB), onTap: () => context.go('/appointments')),
                    _QuickAction(icon: Icons.science,        label: 'Résultats',   color: const Color(0xFF7C3AED), onTap: () => context.go('/results')),
                    _QuickAction(icon: Icons.medication,     label: 'Ordonnances', color: const Color(0xFF059669), onTap: () => context.go('/prescriptions')),
                    _QuickAction(icon: Icons.receipt_long,   label: 'Factures',    color: const Color(0xFFD97706), onTap: () => context.go('/invoices')),
                    _QuickAction(icon: Icons.chat_bubble,    label: 'Messages',    color: const Color(0xFF0891B2), onTap: () => context.go('/chat')),
                    _QuickAction(icon: Icons.monitor_heart,  label: 'Constantes',  color: const Color(0xFFDC2626), onTap: () => context.go('/vitals')),
                  ],
                ),
                const SizedBox(height: 24),

                // Prochain RDV
                _SectionCard(
                  title: 'Prochain rendez-vous',
                  icon: Icons.calendar_today,
                  iconColor: const Color(0xFF2563EB),
                  child: _loading
                      ? const Center(child: CircularProgressIndicator())
                      : _NextAppointmentWidget(),
                ),
                const SizedBox(height: 16),

                // Alertes médicaments
                _SectionCard(
                  title: 'Rappels médicamenteux',
                  icon: Icons.alarm,
                  iconColor: const Color(0xFFD97706),
                  child: Column(
                    children: [
                      _ReminderTile(med: 'Amlodipine 5mg', heure: '08:00', pris: true),
                      _ReminderTile(med: 'Metformine 500mg', heure: '12:00', pris: false),
                      _ReminderTile(med: 'Metformine 500mg', heure: '20:00', pris: false),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Résultats récents
                _SectionCard(
                  title: 'Résultats récents',
                  icon: Icons.science,
                  iconColor: const Color(0xFF7C3AED),
                  child: Column(
                    children: [
                      _ResultTile(type: 'NFS', date: '12/06/2025', statut: 'Disponible', urgent: false),
                      _ResultTile(type: 'Glycémie', date: '10/06/2025', statut: 'Disponible', urgent: false),
                      _ResultTile(type: 'ECG', date: '08/06/2025', statut: 'En attente', urgent: true),
                    ],
                  ),
                ),
                const SizedBox(height: 80),
              ]),
            ),
          ),
        ],
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _QuickAction({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [BoxShadow(color: color.withOpacity(0.12), blurRadius: 8, offset: const Offset(0, 3))],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
              child: Icon(icon, color: color, size: 26),
            ),
            const SizedBox(height: 8),
            Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF374151)), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color iconColor;
  final Widget child;
  const _SectionCard({required this.title, required this.icon, required this.iconColor, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))]),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 0),
            child: Row(children: [
              Icon(icon, color: iconColor, size: 18),
              const SizedBox(width: 8),
              Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
            ]),
          ),
          const Divider(height: 16),
          Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 14), child: child),
        ],
      ),
    );
  }
}

class _NextAppointmentWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(10)),
      child: Row(
        children: [
          Container(
            width: 48, height: 48,
            decoration: BoxDecoration(color: const Color(0xFF2563EB), borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.calendar_today, color: Colors.white, size: 22),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Dr. Camara Alpha', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F2044))),
                Text('Médecine interne', style: TextStyle(fontSize: 12, color: Color(0xFF6B7280))),
                SizedBox(height: 4),
                Text('Demain — 10h00', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(color: const Color(0xFF2563EB), borderRadius: BorderRadius.circular(8)),
            child: const Text('Confirmé', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }
}

class _ReminderTile extends StatelessWidget {
  final String med, heure;
  final bool pris;
  const _ReminderTile({required this.med, required this.heure, required this.pris});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(pris ? Icons.check_circle : Icons.radio_button_unchecked,
              color: pris ? const Color(0xFF16A34A) : const Color(0xFFD97706), size: 20),
          const SizedBox(width: 10),
          Expanded(child: Text(med, style: TextStyle(fontSize: 13, color: pris ? const Color(0xFF6B7280) : const Color(0xFF111827),
              decoration: pris ? TextDecoration.lineThrough : null))),
          Text(heure, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
        ],
      ),
    );
  }
}

class _ResultTile extends StatelessWidget {
  final String type, date, statut;
  final bool urgent;
  const _ResultTile({required this.type, required this.date, required this.statut, required this.urgent});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          Container(
            width: 36, height: 36,
            decoration: BoxDecoration(color: const Color(0xFFF3F4F6), borderRadius: BorderRadius.circular(8)),
            child: const Icon(Icons.science, size: 18, color: Color(0xFF7C3AED)),
          ),
          const SizedBox(width: 10),
          Expanded(child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(type, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
              Text(date, style: const TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
            ],
          )),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: statut == 'Disponible' ? const Color(0xFFDCFCE7) : const Color(0xFFFEF9C3),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(statut, style: TextStyle(
              fontSize: 10, fontWeight: FontWeight.w600,
              color: statut == 'Disponible' ? const Color(0xFF166534) : const Color(0xFF854D0E),
            )),
          ),
        ],
      ),
    );
  }
}
