class AppConfig {
  // ── PRODUCTION (remplace par ton URL Railway après déploiement) ──
  static const String apiBaseUrl = 'https://TON-BACKEND.railway.app/api/v1';

  // ── DEV LOCAL ──
  // Android emulator  : 'http://10.0.2.2:8000/api/v1'
  // iOS simulator     : 'http://127.0.0.1:8000/api/v1'
  // Appareil physique : 'http://TON_IP_LOCAL:8000/api/v1'

  static const String appName = 'CHU — Espace Patient';
  static const String version = '1.0.0';
}
