import 'package:flutter/material.dart';

class VitalsScreen extends StatelessWidget {
  const VitalsScreen({super.key});

  final _vitals = const [
    {'label': 'Tension artérielle', 'value': '128/82', 'unit': 'mmHg', 'icon': Icons.favorite, 'color': Color(0xFFDC2626), 'status': 'normal', 'trend': '↓ -2 vs hier'},
    {'label': 'Fréquence cardiaque', 'value': '74',     'unit': 'bpm',  'icon': Icons.monitor_heart, 'color': Color(0xFFDC2626), 'status': 'normal', 'trend': '→ stable'},
    {'label': 'Température',         'value': '37.2',   'unit': '°C',   'icon': Icons.thermostat, 'color': Color(0xFFD97706), 'status': 'normal', 'trend': '→ stable'},
    {'label': 'SpO₂',                'value': '98',     'unit': '%',    'icon': Icons.air, 'color': Color(0xFF2563EB), 'status': 'normal', 'trend': '→ stable'},
    {'label': 'Glycémie',            'value': '1.26',   'unit': 'g/L',  'icon': Icons.water_drop, 'color': Color(0xFFD97706), 'status': 'warning', 'trend': '↑ +0.1 vs hier'},
    {'label': 'Poids',               'value': '78.5',   'unit': 'kg',   'icon': Icons.monitor_weight, 'color': Color(0xFF7C3AED), 'status': 'normal', 'trend': '→ stable'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(title: const Text('Mes Constantes Vitales')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12)),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: Color(0xFF2563EB), size: 18),
                  const SizedBox(width: 8),
                  const Expanded(child: Text('Dernière mesure : aujourd\'hui à 08:00 par Inf. Kouyaté', style: TextStyle(fontSize: 12, color: Color(0xFF1E40AF)))),
                ],
              ),
            ),
            const SizedBox(height: 16),
            const Text('Constantes du jour', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
            const SizedBox(height: 12),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.3,
              ),
              itemCount: _vitals.length,
              itemBuilder: (_, i) => _VitalCard(vital: _vitals[i]),
            ),
            const SizedBox(height: 24),
            const Text('Tendances (7 jours)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
            const SizedBox(height: 12),
            _TrendChart(label: 'Tension systolique', values: const [130, 128, 132, 126, 129, 131, 128], unit: 'mmHg', color: const Color(0xFFDC2626)),
            const SizedBox(height: 12),
            _TrendChart(label: 'Glycémie', values: const [1.1, 1.3, 1.2, 1.4, 1.3, 1.2, 1.26], unit: 'g/L', color: const Color(0xFFD97706)),
          ],
        ),
      ),
    );
  }
}

class _VitalCard extends StatelessWidget {
  final Map<String, dynamic> vital;
  const _VitalCard({required this.vital});

  Color get _bg {
    switch (vital['status']) {
      case 'warning':  return const Color(0xFFFFFBEB);
      case 'critical': return const Color(0xFFFFF5F5);
      default:         return Colors.white;
    }
  }
  Color get _border {
    switch (vital['status']) {
      case 'warning':  return const Color(0xFFFCD34D);
      case 'critical': return const Color(0xFFFCA5A5);
      default:         return const Color(0xFFE5E7EB);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _bg, borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _border),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 6, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(vital['icon'] as IconData, color: vital['color'] as Color, size: 18),
              const Spacer(),
              if (vital['status'] == 'warning')
                const Icon(Icons.warning_amber, color: Color(0xFFD97706), size: 14),
            ],
          ),
          const Spacer(),
          RichText(
            text: TextSpan(
              text: vital['value'] as String,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF0F2044)),
              children: [
                TextSpan(text: ' ${vital['unit']}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal, color: Color(0xFF9CA3AF))),
              ],
            ),
          ),
          const SizedBox(height: 2),
          Text(vital['label'] as String, style: const TextStyle(fontSize: 11, color: Color(0xFF6B7280))),
          const SizedBox(height: 4),
          Text(vital['trend'] as String, style: TextStyle(fontSize: 10, color: vital['color'] as Color, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _TrendChart extends StatelessWidget {
  final String label;
  final List<double> values;
  final String unit;
  final Color color;
  const _TrendChart({required this.label, required this.values, required this.unit, required this.color});

  @override
  Widget build(BuildContext context) {
    final max = values.reduce((a, b) => a > b ? a : b);
    final min = values.reduce((a, b) => a < b ? a : b);
    final range = max - min == 0 ? 1.0 : max - min;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 6, offset: const Offset(0, 2))]),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F2044))),
              const Spacer(),
              Text('${values.last} $unit', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color)),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 60,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: values.asMap().entries.map((e) {
                final h = ((e.value - min) / range * 50 + 10).clamp(10.0, 60.0);
                final isLast = e.key == values.length - 1;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Container(
                          height: h,
                          decoration: BoxDecoration(
                            color: isLast ? color : color.withOpacity(0.3),
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: ['J-6','J-5','J-4','J-3','J-2','J-1','Auj.'].map((d) =>
              Text(d, style: const TextStyle(fontSize: 9, color: Color(0xFF9CA3AF)))).toList(),
          ),
        ],
      ),
    );
  }
}
