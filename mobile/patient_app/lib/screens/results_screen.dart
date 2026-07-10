import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({super.key});
  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> with SingleTickerProviderStateMixin {
  List<dynamic> _results = [];
  bool _loading = true;
  String _filter = 'Tous';
  late TabController _tabs;

  final _demo = [
    {'id': 1, 'type_examen': 'NFS — Numération Formule Sanguine', 'categorie': 'Hématologie', 'statut': 'Publié', 'priorite': 'Normal', 'date_prescription': '2025-06-12T08:30:00',
     'valeurs': [
       {'nom': 'Hémoglobine', 'valeur': '12.5', 'unite': 'g/dL', 'norme': '12.0–16.0', 'ok': true},
       {'nom': 'Globules blancs', 'valeur': '7200', 'unite': '/mm³', 'norme': '4000–10000', 'ok': true},
       {'nom': 'Plaquettes', 'valeur': '245000', 'unite': '/mm³', 'norme': '150000–400000', 'ok': true},
     ]},
    {'id': 2, 'type_examen': 'Glycémie à jeun', 'categorie': 'Biochimie', 'statut': 'Validé', 'priorite': 'Normal', 'date_prescription': '2025-06-10T09:00:00',
     'valeurs': [
       {'nom': 'Glycémie', 'valeur': '1.26', 'unite': 'g/L', 'norme': '0.70–1.10', 'ok': false},
     ]},
    {'id': 3, 'type_examen': 'ECG 12 dérivations', 'categorie': 'Cardiologie', 'statut': 'Saisie résultats', 'priorite': 'Urgent', 'date_prescription': '2025-06-11T14:00:00', 'valeurs': []},
    {'id': 4, 'type_examen': 'Créatininémie', 'categorie': 'Biochimie', 'statut': 'Commande', 'priorite': 'Normal', 'date_prescription': '2025-06-13T10:00:00', 'valeurs': []},
  ];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _load();
  }

  @override
  void dispose() { _tabs.dispose(); super.dispose(); }

  Future<void> _load() async {
    try {
      final data = await apiService.getMyLabResults();
      if (mounted) setState(() { _results = data.isNotEmpty ? data : _demo; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _results = _demo; _loading = false; });
    }
  }

  List<dynamic> get _filtered {
    if (_filter == 'Tous') return _results;
    if (_filter == 'Disponibles') return _results.where((r) => r['statut'] == 'Publié' || r['statut'] == 'Validé').toList();
    return _results.where((r) => r['priorite'] == 'Urgent').toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      body: NestedScrollView(
        headerSliverBuilder: (_, __) => [
          SliverAppBar(
            pinned: true,
            backgroundColor: const Color(0xFF0F0C29),
            title: const Text('Mes Résultats', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
            bottom: PreferredSize(
              preferredSize: const Size.fromHeight(50),
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
                child: Row(children: ['Tous', 'Disponibles', 'Urgents'].map((f) => GestureDetector(
                  onTap: () => setState(() => _filter = f),
                  child: Container(
                    margin: const EdgeInsets.only(right: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 7),
                    decoration: BoxDecoration(
                      color: _filter == f ? const Color(0xFF6366F1) : Colors.white.withValues(alpha: 0.07),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: _filter == f ? const Color(0xFF6366F1) : Colors.white.withValues(alpha: 0.1)),
                    ),
                    child: Text(f, style: TextStyle(color: _filter == f ? Colors.white : Colors.white60, fontSize: 12, fontWeight: FontWeight.w600)),
                  ),
                )).toList()),
              ),
            ),
          ),
        ],
        body: _loading
            ? const Center(child: CircularProgressIndicator(color: Color(0xFF818CF8)))
            : ListView.builder(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
                itemCount: _filtered.length,
                itemBuilder: (_, i) => _ResultCard(result: _filtered[i]),
              ),
      ),
    );
  }
}

class _ResultCard extends StatefulWidget {
  final Map<String, dynamic> result;
  const _ResultCard({required this.result});
  @override
  State<_ResultCard> createState() => _ResultCardState();
}

class _ResultCardState extends State<_ResultCard> {
  bool _expanded = false;

  Color get _statutColor {
    switch (widget.result['statut']) {
      case 'Publié': case 'Validé': return const Color(0xFF34D399);
      case 'Saisie résultats': return const Color(0xFFA78BFA);
      case 'Commande': return const Color(0xFF818CF8);
      default: return const Color(0xFFFBBF24);
    }
  }

  bool get _disponible => widget.result['statut'] == 'Publié' || widget.result['statut'] == 'Validé';

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.tryParse(widget.result['date_prescription'] ?? '') ?? DateTime.now();
    final valeurs = (widget.result['valeurs'] as List?) ?? [];
    final urgent = widget.result['priorite'] == 'Urgent';

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: urgent ? const Color(0xFFF87171).withValues(alpha: 0.4) : Colors.white.withValues(alpha: 0.07)),
      ),
      child: Column(children: [
        GestureDetector(
          onTap: () => setState(() => _expanded = !_expanded),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(children: [
              Container(
                width: 48, height: 48,
                decoration: BoxDecoration(
                  color: _statutColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(Icons.science_rounded, color: _statutColor, size: 24),
              ),
              const SizedBox(width: 14),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(widget.result['type_examen'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700)),
                const SizedBox(height: 3),
                Row(children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                    decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(6)),
                    child: Text(widget.result['categorie'] ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 10)),
                  ),
                  const SizedBox(width: 6),
                  Text('${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}',
                      style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
                ]),
              ])),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: _statutColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(10)),
                  child: Text(widget.result['statut'] ?? '', style: TextStyle(color: _statutColor, fontSize: 10, fontWeight: FontWeight.w700)),
                ),
                if (urgent) ...[ const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                    decoration: BoxDecoration(color: const Color(0xFFF87171).withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6)),
                    child: const Text('URGENT', style: TextStyle(color: Color(0xFFF87171), fontSize: 9, fontWeight: FontWeight.w800)),
                  ),
                ],
              ]),
            ]),
          ),
        ),
        if (_disponible && valeurs.isNotEmpty) ...[ 
          Divider(height: 1, color: Colors.white.withValues(alpha: 0.07)),
          AnimatedCrossFade(
            firstChild: const SizedBox.shrink(),
            secondChild: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(children: [
                ...valeurs.map((v) => _ValeurRow(valeur: v as Map<String, dynamic>)),
              ]),
            ),
            crossFadeState: _expanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 250),
          ),
          GestureDetector(
            onTap: () => setState(() => _expanded = !_expanded),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.03),
                borderRadius: const BorderRadius.vertical(bottom: Radius.circular(20)),
              ),
              child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                Text(_expanded ? 'Masquer les valeurs' : 'Voir les valeurs',
                    style: const TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.w600)),
                const SizedBox(width: 4),
                Icon(_expanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded, color: const Color(0xFF818CF8), size: 18),
              ]),
            ),
          ),
        ],
        if (_disponible && valeurs.isEmpty)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 14),
            child: GestureDetector(
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: const Text('📄 Téléchargement du PDF...'),
                backgroundColor: const Color(0xFF6366F1),
                behavior: SnackBarBehavior.floating,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              )),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFF6366F1).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
                ),
                child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(Icons.download_rounded, color: Color(0xFF818CF8), size: 16),
                  SizedBox(width: 8),
                  Text('Télécharger le PDF', style: TextStyle(color: Color(0xFF818CF8), fontSize: 13, fontWeight: FontWeight.w600)),
                ]),
              ),
            ),
          ),
      ]),
    );
  }
}

class _ValeurRow extends StatelessWidget {
  final Map<String, dynamic> valeur;
  const _ValeurRow({required this.valeur});

  @override
  Widget build(BuildContext context) {
    final ok = valeur['ok'] as bool? ?? true;
    final color = ok ? const Color(0xFF34D399) : const Color(0xFFF87171);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(children: [
        Icon(ok ? Icons.check_circle_rounded : Icons.warning_rounded, color: color, size: 18),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(valeur['nom'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
          Text('Norme: ${valeur['norme'] ?? ''} ${valeur['unite'] ?? ''}', style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
        ])),
        Text('${valeur['valeur']} ${valeur['unite']}', style: TextStyle(color: color, fontSize: 14, fontWeight: FontWeight.w800)),
      ]),
    );
  }
}
