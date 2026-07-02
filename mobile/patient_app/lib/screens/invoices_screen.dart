import 'package:flutter/material.dart';
import '../services/api_service.dart';

class InvoicesScreen extends StatefulWidget {
  const InvoicesScreen({super.key});
  @override
  State<InvoicesScreen> createState() => _InvoicesScreenState();
}

class _InvoicesScreenState extends State<InvoicesScreen> {
  List<dynamic> _factures = [];
  bool _loading = true;

  final _demo = [
    {'id': 'F-2025-001', 'type_facture': 'Consultation', 'montant_total': 450000, 'montant_paye': 450000, 'statut': 'Payée', 'date_emission': '2025-06-12'},
    {'id': 'F-2025-002', 'type_facture': 'Hospitalisation', 'montant_total': 2800000, 'montant_paye': 1400000, 'statut': 'Partielle', 'date_emission': '2025-06-10'},
    {'id': 'F-2025-003', 'type_facture': 'Examens', 'montant_total': 180000, 'montant_paye': 0, 'statut': 'En attente', 'date_emission': '2025-06-11'},
  ];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await apiService.getMyInvoices();
      if (mounted) setState(() { _factures = data.isNotEmpty ? data : _demo; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _factures = _demo; _loading = false; });
    }
  }

  double get _totalDu => _factures.fold(0, (s, f) => s + ((f['montant_total'] ?? 0) - (f['montant_paye'] ?? 0)));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(title: const Text('Mes Factures')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                if (_totalDu > 0)
                  Container(
                    margin: const EdgeInsets.all(16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(colors: [Color(0xFFDC2626), Color(0xFFB91C1C)]),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.warning_amber, color: Colors.white, size: 28),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Solde restant dû', style: TextStyle(color: Colors.white70, fontSize: 12)),
                              Text('${_totalDu.toStringAsFixed(0)} GNF', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
                            ],
                          ),
                        ),
                        ElevatedButton(
                          onPressed: () {},
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: const Color(0xFFDC2626)),
                          child: const Text('Payer'),
                        ),
                      ],
                    ),
                  ),
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: _factures.length,
                    itemBuilder: (_, i) => _FactureCard(facture: _factures[i]),
                  ),
                ),
              ],
            ),
    );
  }
}

class _FactureCard extends StatelessWidget {
  final Map<String, dynamic> facture;
  const _FactureCard({required this.facture});

  Color get _color {
    switch (facture['statut']) {
      case 'Payée':      return const Color(0xFF16A34A);
      case 'Partielle':  return const Color(0xFFD97706);
      case 'En attente': return const Color(0xFFDC2626);
      default:           return const Color(0xFF6B7280);
    }
  }

  @override
  Widget build(BuildContext context) {
    final total = (facture['montant_total'] ?? 0).toDouble();
    final paye  = (facture['montant_paye']  ?? 0).toDouble();
    final pct   = total > 0 ? (paye / total).clamp(0.0, 1.0) : 0.0;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white, borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(6)),
                child: Text(facture['id']?.toString() ?? '', style: const TextStyle(fontFamily: 'monospace', fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
              ),
              const SizedBox(width: 8),
              Text(facture['type_facture'] ?? '', style: const TextStyle(fontSize: 13, color: Color(0xFF6B7280))),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: _color.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
                child: Text(facture['statut'] ?? '', style: TextStyle(color: _color, fontSize: 11, fontWeight: FontWeight.w700)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Total', style: TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
                Text('${total.toStringAsFixed(0)} GNF', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
              ]),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                const Text('Payé', style: TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
                Text('${paye.toStringAsFixed(0)} GNF', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: _color)),
              ]),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: pct, minHeight: 6,
              backgroundColor: const Color(0xFFE5E7EB),
              valueColor: AlwaysStoppedAnimation<Color>(_color),
            ),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(facture['date_emission'] ?? '', style: const TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
              TextButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.download, size: 14),
                label: const Text('PDF', style: TextStyle(fontSize: 12)),
                style: TextButton.styleFrom(foregroundColor: const Color(0xFF2563EB), padding: EdgeInsets.zero),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
