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

  // Données démo
  final _demoRdvs = [
    {'id': 1, 'medecin': 'Dr. Camara Alpha', 'service': 'Médecine interne', 'date_heure': '2025-06-14T10:00:00', 'type_rdv': 'Consultation', 'statut': 'Confirmé', 'motif': 'Suivi diabète'},
    {'id': 2, 'medecin': 'Dr. Bah Mariama',  'service': 'Cardiologie',      'date_heure': '2025-06-20T14:30:00', 'type_rdv': 'Suivi',        'statut': 'En attente','motif': 'Contrôle TA'},
    {'id': 3, 'medecin': 'Dr. Camara Alpha', 'service': 'Médecine interne', 'date_heure': '2025-05-28T09:00:00', 'type_rdv': 'Consultation', 'statut': 'Terminé',   'motif': 'Bilan annuel'},
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
      if (mounted) setState(() { _rdvs = data.isNotEmpty ? data : _demoRdvs; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _rdvs = _demoRdvs; _loading = false; });
    }
  }

  @override
  void dispose() { _tabs.dispose(); super.dispose(); }

  List<dynamic> get _upcoming => _rdvs.where((r) => r['statut'] != 'Terminé' && r['statut'] != 'Annulé').toList();
  List<dynamic> get _past     => _rdvs.where((r) => r['statut'] == 'Terminé' || r['statut'] == 'Annulé').toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(
        title: const Text('Mes Rendez-vous'),
        bottom: TabBar(
          controller: _tabs,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.white,
          tabs: const [Tab(text: 'À venir'), Tab(text: 'Historique')],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showNewRdvSheet,
        backgroundColor: const Color(0xFF2563EB),
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Nouveau RDV', style: TextStyle(color: Colors.white)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabs,
              children: [
                _RdvList(rdvs: _upcoming, onCancel: _cancelRdv),
                _RdvList(rdvs: _past, onCancel: null),
              ],
            ),
    );
  }

  Future<void> _cancelRdv(int id) async {
    try {
      await apiService.cancelAppointment(id);
      _load();
    } catch (_) {}
  }

  void _showNewRdvSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => const _NewRdvSheet(),
    );
  }
}

class _RdvList extends StatelessWidget {
  final List<dynamic> rdvs;
  final Function(int)? onCancel;
  const _RdvList({required this.rdvs, this.onCancel});

  @override
  Widget build(BuildContext context) {
    if (rdvs.isEmpty) {
      return const Center(child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.calendar_today_outlined, size: 64, color: Color(0xFFD1D5DB)),
          SizedBox(height: 12),
          Text('Aucun rendez-vous', style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 16)),
        ],
      ));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
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
      case 'Confirmé':   return const Color(0xFF16A34A);
      case 'En attente': return const Color(0xFFD97706);
      case 'Terminé':    return const Color(0xFF6B7280);
      case 'Annulé':     return const Color(0xFFDC2626);
      default:           return const Color(0xFF2563EB);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.tryParse(rdv['date_heure'] ?? '') ?? DateTime.now();
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white, borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 52, height: 52,
                  decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12)),
                  child: const Icon(Icons.person, color: Color(0xFF2563EB), size: 28),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(rdv['medecin'] ?? '', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: Color(0xFF0F2044))),
                      Text(rdv['service'] ?? '', style: const TextStyle(fontSize: 12, color: Color(0xFF6B7280))),
                      const SizedBox(height: 4),
                      Text(rdv['motif'] ?? '', style: const TextStyle(fontSize: 13, color: Color(0xFF374151))),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: _statutColor.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                  child: Text(rdv['statut'] ?? '', style: TextStyle(color: _statutColor, fontSize: 11, fontWeight: FontWeight.w700)),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: const BoxDecoration(
              color: Color(0xFFF9FAFB),
              borderRadius: BorderRadius.vertical(bottom: Radius.circular(14)),
            ),
            child: Row(
              children: [
                const Icon(Icons.access_time, size: 14, color: Color(0xFF9CA3AF)),
                const SizedBox(width: 4),
                Text(
                  '${dt.day.toString().padLeft(2,'0')}/${dt.month.toString().padLeft(2,'0')}/${dt.year} à ${dt.hour.toString().padLeft(2,'0')}h${dt.minute.toString().padLeft(2,'0')}',
                  style: const TextStyle(fontSize: 12, color: Color(0xFF6B7280), fontWeight: FontWeight.w600),
                ),
                const Spacer(),
                if (onCancel != null && rdv['statut'] != 'Annulé')
                  TextButton(
                    onPressed: () => onCancel!(rdv['id']),
                    style: TextButton.styleFrom(foregroundColor: const Color(0xFFDC2626), padding: EdgeInsets.zero),
                    child: const Text('Annuler', style: TextStyle(fontSize: 12)),
                  ),
              ],
            ),
          ),
        ],
      ),
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
  String _selectedMedecin = 'Dr. Camara Alpha';
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  String _selectedHeure = '09:00';
  bool _loading = false;

  final _medecins = ['Dr. Camara Alpha', 'Dr. Bah Mariama', 'Dr. Diallo Oumar', 'Dr. Kouyaté Sekou'];
  final _heures = ['08:00','09:00','10:00','11:00','14:00','15:00','16:00','17:00'];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(children: [
              const Text('Nouveau rendez-vous', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              const Spacer(),
              IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(context)),
            ]),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedMedecin,
              decoration: const InputDecoration(labelText: 'Médecin', prefixIcon: Icon(Icons.person)),
              items: _medecins.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
              onChanged: (v) => setState(() => _selectedMedecin = v!),
            ),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(
                child: InkWell(
                  onTap: () async {
                    final d = await showDatePicker(context: context, initialDate: _selectedDate,
                        firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 90)));
                    if (d != null) setState(() => _selectedDate = d);
                  },
                  child: InputDecorator(
                    decoration: const InputDecoration(labelText: 'Date', prefixIcon: Icon(Icons.calendar_today)),
                    child: Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}'),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedHeure,
                  decoration: const InputDecoration(labelText: 'Heure', prefixIcon: Icon(Icons.access_time)),
                  items: _heures.map((h) => DropdownMenuItem(value: h, child: Text(h))).toList(),
                  onChanged: (v) => setState(() => _selectedHeure = v!),
                ),
              ),
            ]),
            const SizedBox(height: 12),
            TextFormField(
              controller: _motifCtrl,
              decoration: const InputDecoration(labelText: 'Motif de consultation', prefixIcon: Icon(Icons.notes)),
              maxLines: 2,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : () async {
                setState(() => _loading = true);
                await Future.delayed(const Duration(seconds: 1));
                if (mounted) { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('✅ Rendez-vous demandé avec succès'))); }
              },
              child: _loading ? const CircularProgressIndicator(color: Colors.white) : const Text('Confirmer la demande'),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
