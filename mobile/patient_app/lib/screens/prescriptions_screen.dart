import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PrescriptionsScreen extends StatefulWidget {
  const PrescriptionsScreen({super.key});
  @override
  State<PrescriptionsScreen> createState() => _PrescriptionsScreenState();
}

class _PrescriptionsScreenState extends State<PrescriptionsScreen> {
  List<dynamic> _prescriptions = [];
  bool _loading = true;

  final _demo = [
    {'id': 1, 'statut': 'Validée', 'medecin': 'Dr. Camara Alpha', 'date_prescription': '2025-06-12T10:00:00', 'verrouille': true,
     'lignes': [
       {'medicament': 'Amlodipine 5mg', 'posologie': '1 comprimé le matin', 'duree_jours': 30, 'quantite': 30, 'pris_auj': true},
       {'medicament': 'Metformine 500mg', 'posologie': '1 comprimé matin et soir', 'duree_jours': 30, 'quantite': 60, 'pris_auj': false},
     ]},
    {'id': 2, 'statut': 'Dispensée', 'medecin': 'Dr. Bah Mariama', 'date_prescription': '2025-06-05T09:00:00', 'verrouille': true,
     'lignes': [
       {'medicament': 'Paracétamol 500mg', 'posologie': '2 comprimés toutes les 6h si douleur', 'duree_jours': 5, 'quantite': 20, 'pris_auj': false},
       {'medicament': 'Ibuprofène 400mg', 'posologie': '1 comprimé 3x/jour pendant les repas', 'duree_jours': 5, 'quantite': 15, 'pris_auj': false},
     ]},
  ];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await apiService.getMyPrescriptions();
      if (mounted) setState(() { _prescriptions = data.isNotEmpty ? data : _demo; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _prescriptions = _demo; _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0C29),
        title: const Text('Mes Ordonnances', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
        elevation: 0,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF818CF8)))
          : _prescriptions.isEmpty
              ? _buildEmpty()
              : ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
                  itemCount: _prescriptions.length,
                  itemBuilder: (_, i) => _PrescCard(prescription: _prescriptions[i]),
                ),
    );
  }

  Widget _buildEmpty() {
    return Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      Container(
        width: 80, height: 80,
        decoration: BoxDecoration(color: const Color(0xFF34D399).withValues(alpha: 0.1), borderRadius: BorderRadius.circular(24)),
        child: const Icon(Icons.medication_outlined, size: 36, color: Color(0xFF34D399)),
      ),
      const SizedBox(height: 16),
      const Text('Aucune ordonnance', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
      const SizedBox(height: 8),
      Text('Vos ordonnances apparaîtront ici', style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 13)),
    ]));
  }
}

class _PrescCard extends StatefulWidget {
  final Map<String, dynamic> prescription;
  const _PrescCard({required this.prescription});
  @override
  State<_PrescCard> createState() => _PrescCardState();
}

class _PrescCardState extends State<_PrescCard> {
  bool _expanded = true;

  Color get _statutColor {
    switch (widget.prescription['statut']) {
      case 'Validée': return const Color(0xFF818CF8);
      case 'Dispensée': return const Color(0xFF34D399);
      default: return const Color(0xFFFBBF24);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.tryParse(widget.prescription['date_prescription'] ?? '') ?? DateTime.now();
    final lignes = (widget.prescription['lignes'] as List?) ?? [];
    final statut = widget.prescription['statut'] ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _statutColor.withValues(alpha: 0.25)),
      ),
      child: Column(children: [
        GestureDetector(
          onTap: () => setState(() => _expanded = !_expanded),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _statutColor.withValues(alpha: 0.08),
              borderRadius: BorderRadius.vertical(top: const Radius.circular(20), bottom: Radius.circular(_expanded ? 0 : 20)),
            ),
            child: Row(children: [
              Container(
                width: 44, height: 44,
                decoration: BoxDecoration(color: _statutColor.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(14)),
                child: Icon(Icons.description_rounded, color: _statutColor, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Ordonnance #${widget.prescription['id']}', style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700)),
                const SizedBox(height: 2),
                Text('${widget.prescription['medecin'] ?? 'Médecin'} · ${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}',
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 12)),
              ])),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(color: _statutColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(10)),
                child: Text(statut, style: TextStyle(color: _statutColor, fontSize: 11, fontWeight: FontWeight.w700)),
              ),
              const SizedBox(width: 8),
              Icon(_expanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                  color: Colors.white38, size: 20),
            ]),
          ),
        ),
        if (_expanded) ...[ 
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('MÉDICAMENTS PRESCRITS', style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 1)),
              const SizedBox(height: 12),
              ...lignes.map((l) => _MedTile(ligne: l as Map<String, dynamic>)),
            ]),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: GestureDetector(
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: const Text('📄 Téléchargement de l\'ordonnance...'),
                backgroundColor: const Color(0xFF6366F1),
                behavior: SnackBarBehavior.floating,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              )),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF6366F1).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
                ),
                child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(Icons.download_rounded, color: Color(0xFF818CF8), size: 16),
                  SizedBox(width: 8),
                  Text('Télécharger l\'ordonnance PDF', style: TextStyle(color: Color(0xFF818CF8), fontSize: 13, fontWeight: FontWeight.w600)),
                ]),
              ),
            ),
          ),
        ],
      ]),
    );
  }
}

class _MedTile extends StatefulWidget {
  final Map<String, dynamic> ligne;
  const _MedTile({required this.ligne});
  @override
  State<_MedTile> createState() => _MedTileState();
}

class _MedTileState extends State<_MedTile> {
  late bool _pris;

  @override
  void initState() {
    super.initState();
    _pris = widget.ligne['pris_auj'] as bool? ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.04),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withValues(alpha: 0.07)),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(
          width: 38, height: 38,
          decoration: BoxDecoration(
            color: const Color(0xFF34D399).withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Icon(Icons.medication_rounded, color: Color(0xFF34D399), size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(widget.ligne['medicament'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700)),
          const SizedBox(height: 3),
          Text(widget.ligne['posologie'] ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.55), fontSize: 12)),
          const SizedBox(height: 4),
          Row(children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(6)),
              child: Text('${widget.ligne['duree_jours']} jours', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 10)),
            ),
            const SizedBox(width: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(6)),
              child: Text('${widget.ligne['quantite']} unités', style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 10)),
            ),
          ]),
        ])),
        GestureDetector(
          onTap: () => setState(() => _pris = !_pris),
          child: Container(
            width: 32, height: 32,
            decoration: BoxDecoration(
              color: _pris ? const Color(0xFF34D399).withValues(alpha: 0.2) : Colors.white.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: _pris ? const Color(0xFF34D399) : Colors.white.withValues(alpha: 0.2)),
            ),
            child: _pris ? const Icon(Icons.check_rounded, color: Color(0xFF34D399), size: 18) : null,
          ),
        ),
      ]),
    );
  }
}
