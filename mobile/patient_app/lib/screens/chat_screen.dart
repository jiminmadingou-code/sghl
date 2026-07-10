import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  List<dynamic> _conversations = [];
  bool _loading = true;

  final _demo = [
    {'id': 1, 'medecin': 'Dr. Camara Alpha', 'service': 'Médecine interne', 'initiales': 'CA',
     'dernier_message': 'Vos résultats sont bons. Continuez le traitement.', 'date': '2025-06-12T14:30:00', 'non_lus': 2, 'en_ligne': true},
    {'id': 2, 'medecin': 'Dr. Bah Mariama', 'service': 'Cardiologie', 'initiales': 'BM',
     'dernier_message': 'N\'oubliez pas votre RDV de demain à 14h30.', 'date': '2025-06-11T09:00:00', 'non_lus': 0, 'en_ligne': false},
    {'id': 3, 'medecin': 'Dr. Kouyaté Sekou', 'service': 'Neurologie', 'initiales': 'KS',
     'dernier_message': 'Bonjour, comment vous sentez-vous aujourd\'hui ?', 'date': '2025-06-09T16:00:00', 'non_lus': 1, 'en_ligne': false},
  ];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await apiService.getMyConversations();
      if (mounted) setState(() { _conversations = data.isNotEmpty ? data : _demo; _loading = false; });
    } catch (_) {
      if (mounted) setState(() { _conversations = _demo; _loading = false; });
    }
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    final dt = DateTime.tryParse(dateStr);
    if (dt == null) return '';
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inDays == 0) return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    if (diff.inDays == 1) return 'Hier';
    if (diff.inDays < 7) return '${diff.inDays}j';
    return '${dt.day}/${dt.month}';
  }

  @override
  Widget build(BuildContext context) {
    final totalNonLus = _conversations.fold<int>(0, (sum, c) => sum + ((c['non_lus'] ?? 0) as int));
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0C29),
        elevation: 0,
        title: Row(children: [
          const Text('Messagerie', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 20)),
          if (totalNonLus > 0) ...[ const SizedBox(width: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(color: const Color(0xFF6366F1), borderRadius: BorderRadius.circular(10)),
              child: Text('$totalNonLus', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700)),
            ),
          ],
        ]),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF818CF8)))
          : _conversations.isEmpty
              ? _buildEmpty()
              : ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
                  itemCount: _conversations.length,
                  itemBuilder: (_, i) => _ConvTile(
                    conv: _conversations[i],
                    dateStr: _formatDate(_conversations[i]['date']),
                    onTap: () => Navigator.push(context, MaterialPageRoute(
                      builder: (_) => _ChatDetailScreen(conv: _conversations[i]),
                    )).then((_) => setState(() => _conversations[i]['non_lus'] = 0)),
                  ),
                ),
    );
  }

  Widget _buildEmpty() {
    return Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      Container(
        width: 80, height: 80,
        decoration: BoxDecoration(color: const Color(0xFF818CF8).withValues(alpha: 0.1), borderRadius: BorderRadius.circular(24)),
        child: const Icon(Icons.chat_bubble_outline_rounded, size: 36, color: Color(0xFF818CF8)),
      ),
      const SizedBox(height: 16),
      const Text('Aucune conversation', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
      const SizedBox(height: 8),
      Text('Vos échanges avec les médecins apparaîtront ici', style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 13), textAlign: TextAlign.center),
    ]));
  }
}

class _ConvTile extends StatelessWidget {
  final Map<String, dynamic> conv;
  final String dateStr;
  final VoidCallback onTap;
  const _ConvTile({required this.conv, required this.dateStr, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final nonLus = (conv['non_lus'] ?? 0) as int;
    final enLigne = conv['en_ligne'] as bool? ?? false;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1740),
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: nonLus > 0 ? const Color(0xFF6366F1).withValues(alpha: 0.3) : Colors.white.withValues(alpha: 0.06)),
        ),
        child: Row(children: [
          Stack(children: [
            Container(
              width: 52, height: 52,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(child: Text(
                conv['initiales'] ?? (conv['medecin'] ?? 'Dr').split(' ').map((w) => w.isNotEmpty ? w[0] : '').take(2).join(),
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 16),
              )),
            ),
            if (enLigne) Positioned(right: 2, bottom: 2, child: Container(
              width: 12, height: 12,
              decoration: BoxDecoration(color: const Color(0xFF34D399), shape: BoxShape.circle, border: Border.all(color: const Color(0xFF1A1740), width: 2)),
            )),
          ]),
          const SizedBox(width: 14),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Expanded(child: Text(conv['medecin'] ?? '', style: TextStyle(
                color: Colors.white, fontSize: 14,
                fontWeight: nonLus > 0 ? FontWeight.w700 : FontWeight.w600,
              ))),
              Text(dateStr, style: TextStyle(color: nonLus > 0 ? const Color(0xFF818CF8) : Colors.white.withValues(alpha: 0.35), fontSize: 11, fontWeight: nonLus > 0 ? FontWeight.w700 : FontWeight.normal)),
            ]),
            const SizedBox(height: 2),
            Text(conv['service'] ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 11)),
            const SizedBox(height: 5),
            Row(children: [
              Expanded(child: Text(conv['dernier_message'] ?? '', maxLines: 1, overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 12, color: nonLus > 0 ? Colors.white.withValues(alpha: 0.8) : Colors.white.withValues(alpha: 0.4),
                      fontWeight: nonLus > 0 ? FontWeight.w600 : FontWeight.normal))),
              if (nonLus > 0) Container(
                width: 20, height: 20,
                decoration: const BoxDecoration(color: Color(0xFF6366F1), shape: BoxShape.circle),
                child: Center(child: Text('$nonLus', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w800))),
              ),
            ]),
          ])),
        ]),
        _ReplyBar(conv: conv),
      ),
    );
  }
}

class _ReplyBar extends StatefulWidget {
  final Map<String, dynamic> conv;
  const _ReplyBar({required this.conv});
  @override
  State<_ReplyBar> createState() => _ReplyBarState();
}

class _ReplyBarState extends State<_ReplyBar> {
  final _ctrl = TextEditingController();
  bool _open = false;

  void _send() {
    if (_ctrl.text.trim().isEmpty) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text('Message envoyé à ${widget.conv['medecin']}'),
      backgroundColor: const Color(0xFF6366F1),
      behavior: SnackBarBehavior.floating,
    ));
    _ctrl.clear();
    setState(() => _open = false);
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      GestureDetector(
        onTap: () => setState(() => _open = !_open),
        child: Container(
          margin: const EdgeInsets.only(top: 10),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFF6366F1).withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.reply_rounded, color: Color(0xFF818CF8), size: 15),
            const SizedBox(width: 6),
            Text(_open ? 'Annuler' : 'Répondre', style: const TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.w600)),
          ]),
        ),
      ),
      if (_open) Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Row(children: [
          Expanded(
            child: TextField(
              controller: _ctrl,
              autofocus: true,
              style: const TextStyle(color: Colors.white, fontSize: 13),
              decoration: InputDecoration(
                hintText: 'Votre message...',
                hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 13),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.07),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              ),
              onSubmitted: (_) => _send(),
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: _send,
            child: Container(
              width: 40, height: 40,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.send_rounded, color: Colors.white, size: 18),
            ),
          ),
        ]),
      ),
    ]);
  }
}

class _ChatDetailScreen extends StatefulWidget {
  final Map<String, dynamic> conv;
  const _ChatDetailScreen({required this.conv});
  @override
  State<_ChatDetailScreen> createState() => _ChatDetailScreenState();
}

class _ChatDetailScreenState extends State<_ChatDetailScreen> {
  final _ctrl = TextEditingController();
  final _scroll = ScrollController();
  bool _typing = false;

  List<Map<String, dynamic>> _messages = [
    {'id': 1, 'contenu': 'Bonjour Docteur, j\'ai des questions sur mon traitement.', 'moi': true, 'heure': '14:00', 'lu': true},
    {'id': 2, 'contenu': 'Bonjour ! Je vous écoute, posez vos questions.', 'moi': false, 'heure': '14:05', 'lu': true},
    {'id': 3, 'contenu': 'Dois-je prendre l\'Amlodipine le matin ou le soir ?', 'moi': true, 'heure': '14:06', 'lu': true},
    {'id': 4, 'contenu': 'Prenez-la le matin avec un verre d\'eau. Évitez le jus de pamplemousse.', 'moi': false, 'heure': '14:10', 'lu': true},
    {'id': 5, 'contenu': 'Vos résultats sont bons. Continuez le traitement.', 'moi': false, 'heure': '14:30', 'lu': false},
  ];

  void _send() {
    final text = _ctrl.text.trim();
    if (text.isEmpty) return;
    final now = DateTime.now();
    setState(() {
      _messages.add({'id': _messages.length + 1, 'contenu': text, 'moi': true,
          'heure': '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}', 'lu': false});
      _ctrl.clear();
      _typing = false;
    });
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
    });
    // Simuler réponse médecin
    Future.delayed(const Duration(seconds: 2), () {
      if (!mounted) return;
      setState(() => _typing = true);
      Future.delayed(const Duration(seconds: 2), () {
        if (!mounted) return;
        setState(() {
          _typing = false;
          _messages.add({'id': _messages.length + 1, 'contenu': 'Merci pour votre message. Je vous réponds dès que possible.', 'moi': false,
              'heure': '${DateTime.now().hour.toString().padLeft(2, '0')}:${DateTime.now().minute.toString().padLeft(2, '0')}', 'lu': false});
        });
        Future.delayed(const Duration(milliseconds: 100), () {
          if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
        });
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final enLigne = widget.conv['en_ligne'] as bool? ?? false;
    return Scaffold(
      backgroundColor: const Color(0xFF0F0C29),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1740),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(children: [
          Container(
            width: 38, height: 38,
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(child: Text(
              widget.conv['initiales'] ?? 'Dr',
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 13),
            )),
          ),
          const SizedBox(width: 10),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(widget.conv['medecin'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700)),
            Row(children: [
              Container(width: 6, height: 6, decoration: BoxDecoration(color: enLigne ? const Color(0xFF34D399) : Colors.white38, shape: BoxShape.circle)),
              const SizedBox(width: 5),
              Text(enLigne ? 'En ligne' : widget.conv['service'] ?? '', style: TextStyle(color: enLigne ? const Color(0xFF34D399) : Colors.white38, fontSize: 11)),
            ]),
          ])),
        ]),
        actions: [
          IconButton(icon: const Icon(Icons.videocam_outlined, color: Colors.white70), onPressed: () {}),
          IconButton(icon: const Icon(Icons.phone_outlined, color: Colors.white70), onPressed: () {}),
        ],
      ),
      body: Column(children: [
        Expanded(
          child: ListView.builder(
            controller: _scroll,
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length + (_typing ? 1 : 0),
            itemBuilder: (_, i) {
              if (_typing && i == _messages.length) return _TypingIndicator();
              final m = _messages[i];
              final moi = m['moi'] as bool;
              return _MessageBubble(message: m, moi: moi);
            },
          ),
        ),
        Container(
          padding: const EdgeInsets.fromLTRB(12, 10, 12, 20),
          decoration: BoxDecoration(
            color: const Color(0xFF1A1740),
            border: Border(top: BorderSide(color: Colors.white.withValues(alpha: 0.07))),
          ),
          child: Row(children: [
            IconButton(
              icon: Icon(Icons.attach_file_rounded, color: Colors.white.withValues(alpha: 0.4)),
              onPressed: () {},
            ),
            Expanded(
              child: TextField(
                controller: _ctrl,
                style: const TextStyle(color: Colors.white, fontSize: 14),
                onChanged: (_) {},
                decoration: InputDecoration(
                  hintText: 'Votre message...',
                  hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 14),
                  filled: true,
                  fillColor: Colors.white.withValues(alpha: 0.07),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                ),
                onSubmitted: (_) => _send(),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: _send,
              child: Container(
                width: 46, height: 46,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [BoxShadow(color: const Color(0xFF6366F1).withValues(alpha: 0.4), blurRadius: 10, offset: const Offset(0, 4))],
                ),
                child: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
              ),
            ),
          ]),
        ),
      ]),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final Map<String, dynamic> message;
  final bool moi;
  const _MessageBubble({required this.message, required this.moi});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: moi ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.72),
        child: Column(crossAxisAlignment: moi ? CrossAxisAlignment.end : CrossAxisAlignment.start, children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
            decoration: BoxDecoration(
              gradient: moi ? const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]) : null,
              color: moi ? null : const Color(0xFF1A1740),
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(18),
                topRight: const Radius.circular(18),
                bottomLeft: Radius.circular(moi ? 18 : 4),
                bottomRight: Radius.circular(moi ? 4 : 18),
              ),
              border: moi ? null : Border.all(color: Colors.white.withValues(alpha: 0.08)),
              boxShadow: [BoxShadow(color: moi ? const Color(0xFF6366F1).withValues(alpha: 0.3) : Colors.black.withValues(alpha: 0.2), blurRadius: 8, offset: const Offset(0, 3))],
            ),
            child: Text(message['contenu'] ?? '', style: TextStyle(color: moi ? Colors.white : Colors.white.withValues(alpha: 0.9), fontSize: 14, height: 1.4)),
          ),
          const SizedBox(height: 4),
          Row(mainAxisSize: MainAxisSize.min, children: [
            Text(message['heure'] ?? '', style: TextStyle(color: Colors.white.withValues(alpha: 0.35), fontSize: 10)),
            if (moi) ...[ const SizedBox(width: 4),
              Icon(message['lu'] == true ? Icons.done_all_rounded : Icons.done_rounded,
                  size: 14, color: message['lu'] == true ? const Color(0xFF818CF8) : Colors.white38),
            ],
          ]),
        ]),
      ),
    );
  }
}

class _TypingIndicator extends StatefulWidget {
  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator> with TickerProviderStateMixin {
  late List<AnimationController> _ctrls;
  late List<Animation<double>> _anims;

  @override
  void initState() {
    super.initState();
    _ctrls = List.generate(3, (i) => AnimationController(vsync: this, duration: const Duration(milliseconds: 600))..repeat(reverse: true, period: Duration(milliseconds: 600 + i * 150)));
    _anims = _ctrls.map((c) => CurvedAnimation(parent: c, curve: Curves.easeInOut)).toList();
  }

  @override
  void dispose() { for (final c in _ctrls) c.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1740),
          borderRadius: const BorderRadius.only(topLeft: Radius.circular(18), topRight: Radius.circular(18), bottomRight: Radius.circular(18), bottomLeft: Radius.circular(4)),
          border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: List.generate(3, (i) => AnimatedBuilder(
          animation: _anims[i],
          builder: (_, __) => Container(
            margin: EdgeInsets.only(right: i < 2 ? 4 : 0),
            width: 7, height: 7 + _anims[i].value * 5,
            decoration: BoxDecoration(color: const Color(0xFF818CF8).withValues(alpha: 0.5 + _anims[i].value * 0.5), borderRadius: BorderRadius.circular(4)),
          ),
        ))),
      ),
    );
  }
}
