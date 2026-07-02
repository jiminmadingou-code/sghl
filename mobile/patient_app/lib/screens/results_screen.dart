import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({super.key});
  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  List<dynamic> _results = [];
  bool _loading = true;

  final _demo = [
    {'id': 1, 'type_examen': 'NFS (Numération Formule Sanguine)', 'statut': 'Publié', 'priorite': 'Normal', 'date_prescription': '2025-06-12T08:30:00', 'resultat': 'Hémoglobine: 12.5 g/dL\nGlobules blancs: 7200/mm³\nPlaquettes: 245000/mm³', 'resultat_immutable': true},
    {'id': 2, 'type_examen': 'Glycémie à jeun', 'statut': 'Validé', 'priorite': 'Normal', 'date_prescription': '2025-06-10T09:00:00', 'resultat': '1.26 g/L (Norme: 0.70-1.10 g/L)', 'resultat_immutable': true},
    {'id': 3, 'type_examen': 'ECG 12 dérivations', 'statut': 'Saisie résultats', 'priorite': 'Urgent', 'date_prescription': '2025-06-11T14:00:00', 'resultat': '', 'resultat_immutable': false},
    {'id': 4, 'type_examen': 'Créatininémie', 'statut': 'Commande', 'priorite': 'Normal', 'date_prescription': '2025-06-13T10:00:00', 'resultat': '', 'resultat_immutable': false},
  ];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await apiService.getMyLabResults();
      if (mounted) setState(() { _results = data.isNotEmpty ? data : _demo; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _results = _demo; _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(title: const Text('Mes Résultats')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _results.length,
              itemBuilder: (_, i) => _ResultCard(result: _results[i]),
            ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  final Map<String, dynamic> result;
  const _ResultCard({required this.result});

  Color get _statutColor {
    switch (result['statut']) {
      case 'Publié': case 'Validé': return const Color(0xFF16A34A);
      case 'Saisie résultats':      return const Color(0xFF7C3AED);
      case 'Commande':              return const Color(0xFF2563EB);
      default:                      return const Color(0xFFD97706);
    }
  }

  bool get _disponible => result['statut'] == 'Publié' || result['statut'] == 'Validé';

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.tryParse(result['date_prescription'] ?? '') ?? DateTime.now();
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white, borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
        border: result['priorite'] == 'Urgent' ? Border.all(color: const Color(0xFFFCA5A5), width: 1.5) : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 44, height: 44,
                  decoration: BoxDecoration(color: const Color(0xFFF3F4F6), borderRadius: BorderRadius.circular(10)),
                  child: const Icon(Icons.science, color: Color(0xFF7C3AED), size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(result['type_examen'] ?? '', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F2044))),
                      const SizedBox(height: 2),
                      Text('${dt.day.toString().padLeft(2,'0')}/${dt.month.toString().padLeft(2,'0')}/${dt.year}',
                          style: const TextStyle(fontSize: 12, color: Color(0xFF9CA3AF))),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: _statutColor.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
                      child: Text(result['statut'] ?? '', style: TextStyle(color: _statutColor, fontSize: 10, fontWeight: FontWeight.w700)),
                    ),
                    if (result['priorite'] == 'Urgent') ...[
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(color: const Color(0xFFFEE2E2), borderRadius: BorderRadius.circular(4)),
                        child: const Text('URGENT', style: TextStyle(color: Color(0xFFDC2626), fontSize: 9, fontWeight: FontWeight.w800)),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          if (_disponible && result['resultat'] != null && result['resultat'].toString().isNotEmpty) ...[
            const Divider(height: 1),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Résultat', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF6B7280), letterSpacing: 0.5)),
                  const SizedBox(height: 6),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: const Color(0xFFF0FDF4), borderRadius: BorderRadius.circular(8)),
                    child: Text(result['resultat'] ?? '', style: const TextStyle(fontSize: 13, color: Color(0xFF166534), fontFamily: 'monospace')),
                  ),
                ],
              ),
            ),
          ],
          if (_disponible)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              child: SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () async {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('📄 Téléchargement du PDF...')));
                    try {
                      await apiService.downloadLabResultPdf(result['id']);
                    } catch (_) {}
                  },
                  icon: const Icon(Icons.download, size: 16),
                  label: const Text('Télécharger le PDF'),
                  style: OutlinedButton.styleFrom(foregroundColor: const Color(0xFF7C3AED), side: const BorderSide(color: Color(0xFF7C3AED))),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
