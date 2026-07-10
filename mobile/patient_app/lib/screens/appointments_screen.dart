import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AppointmentsScreen extends StatefulWidget {
  const AppointmentsScreen({super.key});
  @override
  State<AppointmentsScreen> createState() => _AppointmentsScreenState();
}

class _AppointmentsScreenState extends State<AppointmentsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabs;
  List<dynamic> _rdvs = [];
  bool _loading = true;

  final _demo = [
    {'id': 1, 'medecin': 'Dr. Camara Alpha', 'service': 'Médecine interne', 'specialite': 'Interniste', 'date_heure': '2025-07-14T10:00:00', 'type_rdv': 'Consultation', 'statut': 'Confirmé', 'motif': 'Suivi diabète', 'salle': 'Salle 204'},
    {'id': 2, 'medecin': 'Dr. Bah Mariama', 'service': 'Cardiologie', 'specialite': 'Cardiologue', 'date_heure': '2025-07-20T14:30:00', 'type_rdv': 'Suivi', 'statut': 'En attente', 'motif': 'Contrôle TA', 'salle': 'Salle 108'},
    {'id': 3, 'medecin': 'Dr. Camara Alpha', 'service': 'Médecine interne', 'specialite': 'Interniste', 'date_heure': '2025-05-28T09:00:00', 'type_rdv': 'Consultation', 'statut': 'Terminé', 'motif': 'Bilan annuel', 'salle': 'Salle 204'},
    {'id': 4, 'medecin': 'Dr. Kouyaté Sekou', 'service': 'Neurologie', 'specialite': 'Neurologue', 'date_heure': '2025-04-15T11:00:00', 'type_rdv': 'Consultation', 'statut': 'Terminé', 'motif': 'Céphalées', 'salle': 'Salle 312'},
  ];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await apiService.getMyAppointments();
      if (mounted) setState(() { _rdvs = data.isNotEmpty ? data : _demo; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _rdvs = _demo; _loading = false; });
    }
  }

  @override
  void dispose() { _tabs.dispose(); super.dispose(); }

  List<dynamic> get _upcoming => _rdvs.where((r) => r['statut'] != 'Terminé' && r['statut'] != 'Annulé').toList();
  List<dynamic> get _past => _rdvs.where((r) => r['statut'] == 'Terminé' || r['statut'] == 'Annulé').toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      body: NestedScrollView(
        headerSliverBuilder: (_, __) => [
          SliverAppBar(
            pinned: true,
            backgroundColor: const Color(0xFF0F0C29),
            title: const Text('Mes Rendez-vous', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
            bottom: TabBar(
              controller: _tabs,
              labelColor: const Color(0xFF818CF8),
              unselectedLabelColor: Colors.white38,
              indicatorColor: const Color(0xFF818CF8),
              indicatorSize: TabBarIndicatorSize.label,
              tabs: const [Tab(text: 'À venir'), Tab(text: 'Historique')],
            ),
          ),
        ],
        body: _loading
            ? const Center(child: CircularProgressIndicator(color: Color(0xFF818CF8)))
            : TabBarView(controller: _tabs, children: [
                _RdvList(rdvs: _upcoming, onCancel: _cancelRdv, onNewRdv: _showNewRdvSheet),
                _RdvList(rdvs: _past, onCancel: null, onNewRdv: null),
              ]),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showNewRdvSheet,
        backgroundColor: const Color(0xFF6366F1),
        icon: const Icon(Icons.add_rounded, color: Colors.white),
        label: const Text('Nouveau RDV', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
      ),
    );
  }

  Future<void> _cancelRdv(int id) async {
    try { await apiService.cancelAppointment(id); _load(); } catch (_) {}
  }

  void _showNewRdvSheet() {
    showModalBottomSheet(
      context: context, isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => const _NewRdvSheet(),
    );
  }
}

class _RdvList extends StatelessWidget {
  final List<dynamic> rdvs;
  final Function(int)? onCancel;
  final VoidCallback? onNewRdv;
  const _RdvList({required this.rdvs, this.onCancel, this.onNewRdv});

  @override
  Widget build(BuildContext context) {
    if (rdvs.isEmpty) {
      return Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        Container(
          width: 80, height: 80,
          decoration: BoxDecoration(color: const Color(0xFF818CF8).withValues(alpha: 0.1), borderRadius: BorderRadius.circular(24)),
          child: const Icon(Icons.calendar_today_outlined, size: 36, color: Color(0xFF818CF8)),
        ),
        const SizedBox(height: 16),
        const Text('Aucun rendez-vous', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        Text('Prenez un rendez-vous dès maintenant', style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 13)),
        if (onNewRdv != null) ...[ const SizedBox(height: 20),
          GestureDetector(onTap: onNewRdv, child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]), borderRadius: BorderRadius.circular(14)),
            child: const Text('Prendre un RDV', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
          )),
        ],
      ]));
    }
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      itemCount: rdvs.length,
      itemBuilder: (_, i) => _RdvCard(rdv: rdvs[i], onCancel: onCancel),
    );
  }
}

class _RdvCard extends StatelessWidget {
  final Map<String, dynamic> rdv;
  final Function(int)? onCancel;
  const _RdvCard({required this.rdv, this.onCancel});

  Color get _statutColor {
    switch (rdv['statut']) {
      case 'Confirmé': return const Color(0xFF34D399);
      case 'En attente': return const Color(0xFFFBBF24);
      case 'Terminé': return Colors.white38;
      case 'Annulé': return const Color(0xFFF87171);
      default: return const Color(0xFF818CF8);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.tryParse(rdv['date_heure'] ?? '') ?? DateTime.now();
    final isUpcoming = rdv['statut'] != 'Terminé' && rdv['statut'] != 'Annulé';
    final diff = dt.difference(DateTime.now());
    final jours = diff.inDays;

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isUpcoming ? _statutColor.withValues(alpha: 0.3) : Colors.white.withValues(alpha: 0.07)),
      ),
      child: Column(children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(children: [
            Container(
              width: 56, height: 56,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [_statutColor.withValues(alpha: 0.3), _statutColor.withValues(alpha: 0.1)]),
                borderRadius: BorderRadius.circular(18),
              ),
              child: Center(child: Text(
                (() { final parts = (rdv['medecin'] as String? ?? 'Dr').split(' ').where((w) => w.isNotEmpty).toList(); return parts.length >= 2 ? '${parts[0][0]}${parts[1][0]}' : parts.isNotEmpty ? parts[0][0] : 'Dr'; })(),
                style: TextStyle(color: _statutColor, fontSize: 18, fontWeight: FontWeight.w800),
              )),
            ),
            const SizedBox(width: 14),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(rdv['medecin'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700)),
              const SizedBox(height: 2),
              Text(rdv['service'] ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 12)),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(6)),
                child: Text(rdv['motif'] ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 11)),
              ),
            ])),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(color: _statutColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(10)),
              child: Text(rdv['statut'] ?? '', style: TextStyle(color: _statutColor, fontSize: 11, fontWeight: FontWeight.w700)),
            ),
          ]),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.04),
            borderRadius: const BorderRadius.vertical(bottom: Radius.circular(20)),
          ),
          child: Row(children: [
            Icon(Icons.access_time_rounded, size: 14, color: Colors.white.withValues(alpha: 0.4)),
            const SizedBox(width: 6),
            Text(
              '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year} · ${dt.hour.toString().padLeft(2, '0')}h${dt.minute.toString().padLeft(2, '0')}',
              style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12, fontWeight: FontWeight.w600),
            ),
            if (rdv['salle'] != null) ...[ const SizedBox(width: 10),
              Icon(Icons.room_outlined, size: 13, color: Colors.white.withValues(alpha: 0.3)),
              const SizedBox(width: 3),
              Text(rdv['salle'], style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
            ],
            const Spacer(),
            if (isUpcoming && jours >= 0 && jours <= 7)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: const Color(0xFF6366F1).withValues(alpha: 0.2), borderRadius: BorderRadius.circular(8)),
                child: Text(jours == 0 ? "Aujourd'hui" : jours == 1 ? 'Demain' : 'Dans $jours j',
                    style: const TextStyle(color: Color(0xFF818CF8), fontSize: 11, fontWeight: FontWeight.w700)),
              ),
            if (onCancel != null && rdv['statut'] != 'Annulé') ...[ const SizedBox(width: 8),
              GestureDetector(
                onTap: () => onCancel!(rdv['id']),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: const Color(0xFFF87171).withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
                  child: const Text('Annuler', style: TextStyle(color: Color(0xFFF87171), fontSize: 11, fontWeight: FontWeight.w600)),
                ),
              ),
            ],
          ]),
        ),
      ]),
    );
  }
}

class _NewRdvSheet extends StatefulWidget {
  const _NewRdvSheet();
  @override
  State<_NewRdvSheet> createState() => _NewRdvSheetState();
}

class _NewRdvSheetState extends State<_NewRdvSheet> {
  final _motifCtrl = TextEditingController();
  String _medecin = 'Dr. Camara Alpha';
  DateTime _date = DateTime.now().add(const Duration(days: 1));
  String _heure = '09:00';
  bool _loading = false;

  final _medecins = [
    {'nom': 'Dr. Camara Alpha', 'spec': 'Médecine interne'},
    {'nom': 'Dr. Bah Mariama', 'spec': 'Cardiologie'},
    {'nom': 'Dr. Diallo Oumar', 'spec': 'Pédiatrie'},
    {'nom': 'Dr. Kouyaté Sekou', 'spec': 'Neurologie'},
  ];
  final _heures = ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Color(0xFF1A1740),
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom + 20, left: 24, right: 24, top: 20),
      child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.white24, borderRadius: BorderRadius.circular(2)))),
        const SizedBox(height: 20),
        Row(children: [
          const Text('Nouveau rendez-vous', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w800)),
          const Spacer(),
          GestureDetector(onTap: () => Navigator.pop(context), child: Container(
            width: 32, height: 32,
            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.close_rounded, color: Colors.white60, size: 18),
          )),
        ]),
        const SizedBox(height: 20),
        const Text('Médecin', style: TextStyle(color: Colors.white60, fontSize: 12, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.white.withValues(alpha: 0.1))),
          child: DropdownButtonHideUnderline(child: DropdownButton<String>(
            value: _medecin,
            dropdownColor: const Color(0xFF1A1740),
            style: const TextStyle(color: Colors.white, fontSize: 14),
            items: _medecins.map((m) => DropdownMenuItem(value: m['nom'], child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(m['nom']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                Text(m['spec']!, style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
              ],
            ))).toList(),
            onChanged: (v) => setState(() => _medecin = v!),
          )),
        ),
        const SizedBox(height: 14),
        Row(children: [
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Date', style: TextStyle(color: Colors.white60, fontSize: 12, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () async {
                final d = await showDatePicker(context: context, initialDate: _date,
                    firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 90)),
                    builder: (ctx, child) => Theme(data: ThemeData.dark().copyWith(colorScheme: const ColorScheme.dark(primary: Color(0xFF6366F1))), child: child!));
                if (d != null) setState(() => _date = d);
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.white.withValues(alpha: 0.1))),
                child: Row(children: [
                  const Icon(Icons.calendar_today_rounded, color: Color(0xFF818CF8), size: 16),
                  const SizedBox(width: 8),
                  Text('${_date.day.toString().padLeft(2, '0')}/${_date.month.toString().padLeft(2, '0')}/${_date.year}', style: const TextStyle(color: Colors.white, fontSize: 13)),
                ]),
              ),
            ),
          ])),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Heure', style: TextStyle(color: Colors.white60, fontSize: 12, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.white.withValues(alpha: 0.1))),
              child: DropdownButtonHideUnderline(child: DropdownButton<String>(
                value: _heure, dropdownColor: const Color(0xFF1A1740),
                style: const TextStyle(color: Colors.white, fontSize: 13),
                items: _heures.map((h) => DropdownMenuItem(value: h, child: Text(h))).toList(),
                onChanged: (v) => setState(() => _heure = v!),
              )),
            ),
          ])),
        ]),
        const SizedBox(height: 14),
        const Text('Motif', style: TextStyle(color: Colors.white60, fontSize: 12, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        TextField(
          controller: _motifCtrl, maxLines: 2,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            hintText: 'Décrivez le motif de votre consultation...',
            hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 13),
            filled: true, fillColor: Colors.white.withValues(alpha: 0.07),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1))),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1))),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFF6366F1))),
          ),
        ),
        const SizedBox(height: 20),
        GestureDetector(
          onTap: _loading ? null : () async {
            setState(() => _loading = true);
            await Future.delayed(const Duration(seconds: 1));
            if (mounted) {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: const Text('✅ Rendez-vous demandé avec succès'),
                backgroundColor: const Color(0xFF34D399),
                behavior: SnackBarBehavior.floating,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ));
            }
          },
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.4), blurRadius: 16, offset: const Offset(0, 6))],
            ),
            child: Center(child: _loading
                ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                : const Text('Confirmer la demande', style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700))),
          ),
        ),
      ]),
    );
  }
}
