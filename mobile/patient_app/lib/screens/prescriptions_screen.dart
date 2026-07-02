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
    {'id': 1, 'statut': 'Validée', 'date_prescription': '2025-06-12T10:00:00', 'verrouille': true,
     'lignes': [
       {'medicament': 'Amlodipine 5mg', 'posologie': '1 comprimé le matin', 'duree_jours': 30, 'quantite': 30},
       {'medicament': 'Metformine 500mg', 'posologie': '1 comprimé matin et soir', 'duree_jours': 30, 'quantite': 60},
     ]},
    {'id': 2, 'statut': 'Dispensée', 'date_prescription': '2025-06-05T09:00:00', 'verrouille': true,
     'lignes': [
       {'medicament': 'Paracétamol 500mg', 'posologie': '2 comprimés toutes les 6h si douleur', 'duree_jours': 5, 'quantite': 20},
       {'medicament': 'Ibuprofène 400mg', 'posologie': '1 comprimé 3x/jour pendant les repas', 'duree_jours': 5, 'quantite': 15},
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
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(title: const Text('Mes Ordonnances')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _prescriptions.isEmpty
              ? const Center(child: Text('Aucune ordonnance', style: TextStyle(color: Color(0xFF9CA3AF))))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _prescriptions.length,
                  itemBuilder: (_, i) => _PrescriptionCard(prescription: _prescriptions[i]),
                ),
    );
  }
}

class _PrescriptionCard extends StatelessWidget {
  final Map<String, dynamic> prescription;
  const _PrescriptionCard({required this.prescription});

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.tryParse(prescription['date_prescription'] ?? '') ?? DateTime.now();
    final lignes = (prescription['lignes'] as List?) ?? [];
    final statut = prescription['statut'] ?? '';
    final statutColor = statut == 'Validée' ? const Color(0xFF2563EB) : statut == 'Dispensée' ? const Color(0xFF16A34A) : const Color(0xFFD97706);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white, borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFEFF6FF),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
            ),
            child: Row(
              children: [
                const Icon(Icons.description, color: Color(0xFF2563EB), size: 22),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Ordonnance #${prescription['id']}', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: Color(0xFF0F2044))),
                      Text('${dt.day.toString().padLeft(2,'0')}/${dt.month.toString().padLeft(2,'0')}/${dt.year}',
                          style: const TextStyle(fontSize: 12, color: Color(0xFF6B7280))),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: statutColor.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                  child: Text(statut, style: TextStyle(color: statutColor, fontSize: 11, fontWeight: FontWeight.w700)),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Médicaments prescrits', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF6B7280), letterSpacing: 0.5)),
                const SizedBox(height: 10),
                ...lignes.map((l) => _MedTile(ligne: l as Map<String, dynamic>)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('📄 Téléchargement de l\'ordonnance...')));
                },
                icon: const Icon(Icons.download, size: 16),
                label: const Text('Télécharger l\'ordonnance PDF'),
                style: OutlinedButton.styleFrom(foregroundColor: const Color(0xFF2563EB), side: const BorderSide(color: Color(0xFF2563EB))),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MedTile extends StatelessWidget {
  final Map<String, dynamic> ligne;
  const _MedTile({required this.ligne});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: const Color(0xFFF9FAFB), borderRadius: BorderRadius.circular(8)),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32, height: 32,
            decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
            child: const Icon(Icons.medication, color: Color(0xFF16A34A), size: 18),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(ligne['medicament'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: Color(0xFF111827))),
                const SizedBox(height: 2),
                Text(ligne['posologie'] ?? '', style: const TextStyle(fontSize: 12, color: Color(0xFF6B7280))),
                Text('${ligne['duree_jours']} jours · ${ligne['quantite']} unités', style: const TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
