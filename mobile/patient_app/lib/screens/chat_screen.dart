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
    {'id': 1, 'medecin': 'Dr. Camara Alpha', 'service': 'Médecine interne', 'dernier_message': 'Vos résultats sont bons. Continuez le traitement.', 'date': '2025-06-12T14:30:00', 'non_lus': 1},
    {'id': 2, 'medecin': 'Dr. Bah Mariama',  'service': 'Cardiologie',      'dernier_message': 'N\'oubliez pas votre RDV de demain à 14h30.', 'date': '2025-06-11T09:00:00', 'non_lus': 0},
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(title: const Text('Messagerie')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _conversations.isEmpty
              ? const Center(child: Text('Aucune conversation', style: TextStyle(color: Color(0xFF9CA3AF))))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _conversations.length,
                  itemBuilder: (_, i) => _ConvTile(
                    conv: _conversations[i],
                    onTap: () => Navigator.push(context, MaterialPageRoute(
                      builder: (_) => _ChatDetailScreen(conv: _conversations[i]),
                    )),
                  ),
                ),
    );
  }
}

class _ConvTile extends StatelessWidget {
  final Map<String, dynamic> conv;
  final VoidCallback onTap;
  const _ConvTile({required this.conv, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final nonLus = conv['non_lus'] ?? 0;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white, borderRadius: BorderRadius.circular(14),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 6, offset: const Offset(0, 2))],
        ),
        child: Row(
          children: [
            Stack(
              children: [
                CircleAvatar(
                  radius: 26,
                  backgroundColor: const Color(0xFFEFF6FF),
                  child: Text(
                    (conv['medecin'] ?? 'Dr').split(' ').map((w) => w.isNotEmpty ? w[0] : '').take(2).join(),
                    style: const TextStyle(color: Color(0xFF2563EB), fontWeight: FontWeight.w700, fontSize: 16),
                  ),
                ),
                if (nonLus > 0)
                  Positioned(
                    right: 0, top: 0,
                    child: Container(
                      width: 18, height: 18,
                      decoration: const BoxDecoration(color: Color(0xFFDC2626), shape: BoxShape.circle),
                      child: Center(child: Text('$nonLus', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w700))),
                    ),
                  ),
              ],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(conv['medecin'] ?? '', style: TextStyle(fontWeight: nonLus > 0 ? FontWeight.w700 : FontWeight.w600, fontSize: 14, color: const Color(0xFF0F2044))),
                  Text(conv['service'] ?? '', style: const TextStyle(fontSize: 11, color: Color(0xFF9CA3AF))),
                  const SizedBox(height: 3),
                  Text(conv['dernier_message'] ?? '', maxLines: 1, overflow: TextOverflow.ellipsis,
                      style: TextStyle(fontSize: 12, color: nonLus > 0 ? const Color(0xFF111827) : const Color(0xFF6B7280),
                          fontWeight: nonLus > 0 ? FontWeight.w600 : FontWeight.normal)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Color(0xFFD1D5DB)),
          ],
        ),
      ),
    );
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
  List<Map<String, dynamic>> _messages = [
    {'id': 1, 'contenu': 'Bonjour Docteur, j\'ai des questions sur mon traitement.', 'moi': true,  'heure': '14:00'},
    {'id': 2, 'contenu': 'Bonjour ! Je vous écoute, posez vos questions.', 'moi': false, 'heure': '14:05'},
    {'id': 3, 'contenu': 'Dois-je prendre l\'Amlodipine le matin ou le soir ?', 'moi': true,  'heure': '14:06'},
    {'id': 4, 'contenu': 'Prenez-la le matin avec un verre d\'eau. Évitez le jus de pamplemousse.', 'moi': false, 'heure': '14:10'},
    {'id': 5, 'contenu': 'Vos résultats sont bons. Continuez le traitement.', 'moi': false, 'heure': '14:30'},
  ];

  void _send() {
    final text = _ctrl.text.trim();
    if (text.isEmpty) return;
    setState(() {
      _messages.add({'id': _messages.length + 1, 'contenu': text, 'moi': true, 'heure': '${DateTime.now().hour}:${DateTime.now().minute.toString().padLeft(2,'0')}'});
      _ctrl.clear();
    });
    Future.delayed(const Duration(milliseconds: 100), () {
      _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.conv['medecin'] ?? '', style: const TextStyle(fontSize: 15)),
            Text(widget.conv['service'] ?? '', style: const TextStyle(fontSize: 11, color: Colors.white70)),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.videocam_outlined), onPressed: () {}),
          IconButton(icon: const Icon(Icons.phone_outlined), onPressed: () {}),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scroll,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (_, i) {
                final m = _messages[i];
                final moi = m['moi'] as bool;
                return Align(
                  alignment: moi ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                    decoration: BoxDecoration(
                      color: moi ? const Color(0xFF2563EB) : Colors.white,
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(16),
                        topRight: const Radius.circular(16),
                        bottomLeft: Radius.circular(moi ? 16 : 4),
                        bottomRight: Radius.circular(moi ? 4 : 16),
                      ),
                      boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 4, offset: const Offset(0, 2))],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(m['contenu'] ?? '', style: TextStyle(color: moi ? Colors.white : const Color(0xFF111827), fontSize: 14)),
                        const SizedBox(height: 4),
                        Text(m['heure'] ?? '', style: TextStyle(color: moi ? Colors.white60 : const Color(0xFF9CA3AF), fontSize: 10)),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Color(0x0F000000), blurRadius: 8, offset: Offset(0, -2))]),
            child: Row(
              children: [
                IconButton(icon: const Icon(Icons.attach_file, color: Color(0xFF9CA3AF)), onPressed: () {}),
                Expanded(
                  child: TextField(
                    controller: _ctrl,
                    decoration: InputDecoration(
                      hintText: 'Votre message...',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
                      filled: true, fillColor: const Color(0xFFF3F4F6),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    ),
                    onSubmitted: (_) => _send(),
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: _send,
                  child: Container(
                    width: 44, height: 44,
                    decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
                    child: const Icon(Icons.send, color: Colors.white, size: 20),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
