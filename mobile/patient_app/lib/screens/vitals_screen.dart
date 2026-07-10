import 'package:flutter/material.dart';

class VitalsScreen extends StatefulWidget {
  const VitalsScreen({super.key});
  @override
  State<VitalsScreen> createState() => _VitalsScreenState();
}

class _VitalsScreenState extends State<VitalsScreen> with TickerProviderStateMixin {
  late AnimationController _fadeCtrl;
  late Animation<double> _fadeAnim;
  int _selectedChart = 0;

  final _vitals = const [
    {
      'label': 'Tension artérielle',
      'value': '128/82',
      'unit': 'mmHg',
      'icon': Icons.favorite_rounded,
      'accent': Color(0xFFF87171),
      'bg': Color(0xFF3B1A1A),
      'status': 'normal',
      'trend': '↓ -2 vs hier',
      'trendUp': false,
      'normal': '< 130/85',
    },
    {
      'label': 'Fréquence cardiaque',
      'value': '74',
      'unit': 'bpm',
      'icon': Icons.monitor_heart_rounded,
      'accent': Color(0xFF818CF8),
      'bg': Color(0xFF1E1B4B),
      'status': 'normal',
      'trend': '→ stable',
      'trendUp': null,
      'normal': '60–100',
    },
    {
      'label': 'Température',
      'value': '37.2',
      'unit': '°C',
      'icon': Icons.thermostat_rounded,
      'accent': Color(0xFFFBBF24),
      'bg': Color(0xFF2D1F00),
      'status': 'normal',
      'trend': '→ stable',
      'trendUp': null,
      'normal': '36.5–37.5',
    },
    {
      'label': 'SpO₂',
      'value': '98',
      'unit': '%',
      'icon': Icons.air_rounded,
      'accent': Color(0xFF38BDF8),
      'bg': Color(0xFF0C2A3A),
      'status': 'normal',
      'trend': '→ stable',
      'trendUp': null,
      'normal': '> 95%',
    },
    {
      'label': 'Glycémie',
      'value': '1.26',
      'unit': 'g/L',
      'icon': Icons.water_drop_rounded,
      'accent': Color(0xFFFBBF24),
      'bg': Color(0xFF2D1F00),
      'status': 'warning',
      'trend': '↑ +0.1 vs hier',
      'trendUp': true,
      'normal': '0.7–1.1',
    },
    {
      'label': 'Poids',
      'value': '78.5',
      'unit': 'kg',
      'icon': Icons.monitor_weight_rounded,
      'accent': Color(0xFFA78BFA),
      'bg': Color(0xFF2D1B4E),
      'status': 'normal',
      'trend': '→ stable',
      'trendUp': null,
      'normal': 'IMC 24.1',
    },
  ];

  final _charts = [
    {
      'label': 'Tension systolique',
      'values': [130.0, 128.0, 132.0, 126.0, 129.0, 131.0, 128.0],
      'unit': 'mmHg',
      'accent': Color(0xFFF87171),
    },
    {
      'label': 'Glycémie',
      'values': [1.1, 1.3, 1.2, 1.4, 1.3, 1.2, 1.26],
      'unit': 'g/L',
      'accent': Color(0xFFFBBF24),
    },
    {
      'label': 'Fréquence cardiaque',
      'values': [72.0, 75.0, 70.0, 78.0, 74.0, 76.0, 74.0],
      'unit': 'bpm',
      'accent': Color(0xFF818CF8),
    },
  ];

  @override
  void initState() {
    super.initState();
    _fadeCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);
    _fadeCtrl.forward();
  }

  @override
  void dispose() { _fadeCtrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      body: FadeTransition(
        opacity: _fadeAnim,
        child: CustomScrollView(
          slivers: [
            _buildAppBar(),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
              sliver: SliverList(delegate: SliverChildListDelegate([
                const SizedBox(height: 16),
                _buildLastMeasure(),
                const SizedBox(height: 20),
                _buildSectionTitle('Constantes du jour', Icons.grid_view_rounded),
                const SizedBox(height: 12),
                _buildGrid(),
                const SizedBox(height: 24),
                _buildSectionTitle('Tendances 7 jours', Icons.show_chart_rounded),
                const SizedBox(height: 12),
                _buildChartTabs(),
                const SizedBox(height: 12),
                _buildChart(),
                const SizedBox(height: 20),
                _buildSummaryCard(),
              ])),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      pinned: true,
      backgroundColor: const Color(0xFF0F0C29),
      elevation: 0,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 18),
        onPressed: () => Navigator.of(context).maybePop(),
      ),
      title: const Text('Mes Constantes Vitales',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 18)),
      actions: [
        Container(
          margin: const EdgeInsets.only(right: 16),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: const Color(0xFF6366F1).withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.4)),
          ),
          child: const Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(Icons.add_rounded, color: Color(0xFF818CF8), size: 14),
            SizedBox(width: 4),
            Text('Saisir', style: TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.w700)),
          ]),
        ),
      ],
    );
  }

  Widget _buildLastMeasure() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.25)),
      ),
      child: Row(children: [
        Container(
          width: 36, height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFF6366F1).withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(Icons.access_time_rounded, color: Color(0xFF818CF8), size: 18),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text("Dernière mesure", style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
          Text("Aujourd'hui à 08:00 · Inf. Kouyaté",
              style: TextStyle(color: Colors.white.withValues(alpha: 0.5), fontSize: 11)),
        ])),
        Container(
          width: 8, height: 8,
          decoration: const BoxDecoration(color: Color(0xFF34D399), shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        const Text('À jour', style: TextStyle(color: Color(0xFF34D399), fontSize: 11, fontWeight: FontWeight.w600)),
      ]),
    );
  }

  Widget _buildGrid() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.25,
      ),
      itemCount: _vitals.length,
      itemBuilder: (_, i) => _VitalCard(vital: _vitals[i]),
    );
  }

  Widget _buildChartTabs() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: List.generate(_charts.length, (i) {
          final selected = i == _selectedChart;
          final accent = _charts[i]['accent'] as Color;
          return GestureDetector(
            onTap: () => setState(() => _selectedChart = i),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: selected ? accent.withValues(alpha: 0.2) : const Color(0xFF1A1740),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: selected ? accent.withValues(alpha: 0.6) : Colors.white.withValues(alpha: 0.08)),
              ),
              child: Text(_charts[i]['label'] as String,
                  style: TextStyle(
                    color: selected ? accent : Colors.white.withValues(alpha: 0.5),
                    fontSize: 12, fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                  )),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildChart() {
    final chart = _charts[_selectedChart];
    return _TrendChart(
      label: chart['label'] as String,
      values: chart['values'] as List<double>,
      unit: chart['unit'] as String,
      accent: chart['accent'] as Color,
    );
  }

  Widget _buildSummaryCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft, end: Alignment.bottomRight,
          colors: [Color(0xFF1E1B4B), Color(0xFF2D1B4E)],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            width: 36, height: 36,
            decoration: BoxDecoration(
              color: const Color(0xFF6366F1).withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.health_and_safety_rounded, color: Color(0xFF818CF8), size: 18),
          ),
          const SizedBox(width: 12),
          const Text('Bilan de santé', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF34D399).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text('Bon', style: TextStyle(color: Color(0xFF34D399), fontSize: 11, fontWeight: FontWeight.w700)),
          ),
        ]),
        const SizedBox(height: 14),
        _SummaryRow(Icons.check_circle_rounded, 'Tension et fréquence cardiaque normales', const Color(0xFF34D399)),
        const SizedBox(height: 8),
        _SummaryRow(Icons.warning_amber_rounded, 'Glycémie légèrement élevée — surveiller', const Color(0xFFFBBF24)),
        const SizedBox(height: 8),
        _SummaryRow(Icons.info_rounded, 'Prochain bilan recommandé dans 7 jours', const Color(0xFF818CF8)),
      ]),
    );
  }

  Widget _buildSectionTitle(String title, IconData icon) {
    return Row(children: [
      Icon(icon, color: const Color(0xFF818CF8), size: 18),
      const SizedBox(width: 8),
      Text(title, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700)),
    ]);
  }
}

class _SummaryRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color color;
  const _SummaryRow(this.icon, this.text, this.color);
  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Icon(icon, color: color, size: 15),
      const SizedBox(width: 8),
      Expanded(child: Text(text, style: TextStyle(color: Colors.white.withValues(alpha: 0.75), fontSize: 12))),
    ]);
  }
}

class _VitalCard extends StatelessWidget {
  final Map<String, dynamic> vital;
  const _VitalCard({required this.vital});

  @override
  Widget build(BuildContext context) {
    final accent = vital['accent'] as Color;
    final bg = vital['bg'] as Color;
    final isWarning = vital['status'] == 'warning';
    final trendUp = vital['trendUp'];

    Color trendColor;
    IconData trendIcon;
    if (trendUp == null) {
      trendColor = Colors.white38;
      trendIcon = Icons.remove_rounded;
    } else if (trendUp as bool) {
      trendColor = isWarning ? const Color(0xFFFBBF24) : const Color(0xFF34D399);
      trendIcon = Icons.arrow_upward_rounded;
    } else {
      trendColor = const Color(0xFF34D399);
      trendIcon = Icons.arrow_downward_rounded;
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isWarning ? const Color(0xFFFBBF24).withValues(alpha: 0.4) : accent.withValues(alpha: 0.2),
        ),
        boxShadow: [
          BoxShadow(color: accent.withValues(alpha: 0.08), blurRadius: 12, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            width: 36, height: 36,
            decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(10)),
            child: Icon(vital['icon'] as IconData, color: accent, size: 18),
          ),
          const Spacer(),
          if (isWarning)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: const Color(0xFFFBBF24).withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text('⚠', style: TextStyle(fontSize: 10)),
            )
          else
            Container(
              width: 8, height: 8,
              decoration: const BoxDecoration(color: Color(0xFF34D399), shape: BoxShape.circle),
            ),
        ]),
        const Spacer(),
        RichText(
          text: TextSpan(
            text: vital['value'] as String,
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: accent),
            children: [
              TextSpan(
                text: ' ${vital['unit']}',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w500, color: accent.withValues(alpha: 0.6)),
              ),
            ],
          ),
        ),
        const SizedBox(height: 2),
        Text(vital['label'] as String,
            style: TextStyle(fontSize: 11, color: Colors.white.withValues(alpha: 0.6), fontWeight: FontWeight.w500)),
        const SizedBox(height: 6),
        Row(children: [
          Icon(trendIcon, color: trendColor, size: 11),
          const SizedBox(width: 3),
          Expanded(child: Text(vital['trend'] as String,
              style: TextStyle(fontSize: 10, color: trendColor, fontWeight: FontWeight.w600))),
        ]),
        const SizedBox(height: 2),
        Text('Norme: ${vital['normal']}',
            style: TextStyle(fontSize: 9, color: Colors.white.withValues(alpha: 0.3))),
      ]),
    );
  }
}

class _TrendChart extends StatelessWidget {
  final String label;
  final List<double> values;
  final String unit;
  final Color accent;
  const _TrendChart({required this.label, required this.values, required this.unit, required this.accent});

  @override
  Widget build(BuildContext context) {
    final max = values.reduce((a, b) => a > b ? a : b);
    final min = values.reduce((a, b) => a < b ? a : b);
    final range = (max - min) == 0 ? 1.0 : max - min;
    final days = ['J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'J-1', 'Auj.'];

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1740),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: accent.withValues(alpha: 0.2)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text(label, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: accent.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text('${values.last} $unit',
                style: TextStyle(color: accent, fontSize: 12, fontWeight: FontWeight.w800)),
          ),
        ]),
        const SizedBox(height: 16),
        SizedBox(
          height: 80,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: values.asMap().entries.map((e) {
              final h = ((e.value - min) / range * 60 + 12).clamp(12.0, 80.0);
              final isLast = e.key == values.length - 1;
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 3),
                  child: Column(mainAxisAlignment: MainAxisAlignment.end, children: [
                    if (isLast)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Text('${values.last}',
                            style: TextStyle(color: accent, fontSize: 9, fontWeight: FontWeight.w700)),
                      ),
                    Container(
                      height: h,
                      decoration: BoxDecoration(
                        gradient: isLast
                            ? LinearGradient(
                                begin: Alignment.bottomCenter, end: Alignment.topCenter,
                                colors: [accent, accent.withValues(alpha: 0.6)],
                              )
                            : null,
                        color: isLast ? null : accent.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(6),
                        boxShadow: isLast
                            ? [BoxShadow(color: accent.withValues(alpha: 0.4), blurRadius: 8, offset: const Offset(0, 2))]
                            : null,
                      ),
                    ),
                  ]),
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: days.map((d) => Text(d,
              style: TextStyle(fontSize: 9, color: Colors.white.withValues(alpha: 0.35)))).toList(),
        ),
      ]),
    );
  }
}
