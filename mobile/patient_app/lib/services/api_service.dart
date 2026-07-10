import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Stockage sécurisé qui fonctionne aussi bien sur mobile que web
class SecureStorage {
  static FlutterSecureStorage? _secure;
  static SharedPreferences? _prefs;

  static FlutterSecureStorage get _storage =>
      _secure ??= const FlutterSecureStorage();

  static Future<void> _initPrefs() async {
    if (_prefs == null) {
      _prefs = await SharedPreferences.getInstance();
    }
  }

  /// Lecture : web utilise SharedPreferences, mobile utilise flutter_secure_storage
  Future<String?> read({required String key}) async {
    if (kIsWeb) {
      await _initPrefs();
      return _prefs?.getString(key);
    }
    return _storage.read(key: key);
  }

  /// Écriture
  Future<void> write({required String key, required String value}) async {
    if (kIsWeb) {
      await _initPrefs();
      await _prefs?.setString(key, value);
    } else {
      await _storage.write(key: key, value: value);
    }
  }

  /// Suppression
  Future<void> delete({required String key}) async {
    if (kIsWeb) {
      await _initPrefs();
      await _prefs?.remove(key);
    } else {
      await _storage.delete(key: key);
    }
  }

  /// Supprimer tout
  Future<void> deleteAll() async {
    if (kIsWeb) {
      await _initPrefs();
      final keys = _prefs?.getKeys() ?? {};
      for (final k in keys) await _prefs?.remove(k);
    } else {
      await _storage.deleteAll();
    }
  }
}

class ApiService {
  static const String _baseUrl = 'https://sghl-production.up.railway.app/api/v1';

  late final Dio _dio;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await secureStorage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final token = await secureStorage.read(key: 'access_token');
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            final response = await _dio.fetch(error.requestOptions);
            return handler.resolve(response);
          }
        }
        return handler.next(error);
      },
    ));
  }

  Future<bool> _refreshToken() async {
    try {
      final refresh = await secureStorage.read(key: 'refresh_token');
      if (refresh == null) return false;
      final response = await _dio.post('/auth/refresh/', data: {'refresh': refresh});
      await secureStorage.write(key: 'access_token', value: response.data['access']);
      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post('/auth/login/', data: {
      'username': email, // backend accepte email ou username
      'password': password,
    });
    await secureStorage.write(key: 'access_token', value: response.data['access']);
    await secureStorage.write(key: 'refresh_token', value: response.data['refresh']);
    if (response.data['user'] != null) {
      await secureStorage.write(key: 'user_data', value: jsonEncode(response.data['user']));
    }
    return response.data;
  }

  Future<void> logout() async {
    await secureStorage.deleteAll();
  }

  Future<bool> isLoggedIn() async {
    final token = await secureStorage.read(key: 'access_token');
    return token != null;
  }

  // ── Patients ──────────────────────────────────────────────────
  Future<Map<String, dynamic>> getMyProfile() async {
    final response = await _dio.get('/patients/me/');
    return response.data;
  }

  // ── Rendez-vous ───────────────────────────────────────────────
  Future<List<dynamic>> getMyAppointments() async {
    final response = await _dio.get('/rendez-vous/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  Future<Map<String, dynamic>> createAppointment(Map<String, dynamic> data) async {
    final response = await _dio.post('/rendez-vous/', data: data);
    return response.data;
  }

  Future<void> cancelAppointment(int id) async {
    await _dio.patch('/rendez-vous/$id/annuler');
  }

  // ── Résultats labo ────────────────────────────────────────────
  Future<List<dynamic>> getMyLabResults() async {
    final response = await _dio.get('/laboratoire/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  Future<List<int>> downloadLabResultPdf(int examenId) async {
    final response = await _dio.get(
      '/laboratoire/$examenId/pdf',
      options: Options(responseType: ResponseType.bytes),
    );
    return List<int>.from(response.data);
  }

  // ── Prescriptions ─────────────────────────────────────────────
  Future<List<dynamic>> getMyPrescriptions() async {
    final response = await _dio.get('/prescriptions/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  Future<List<int>> downloadPrescriptionPdf(int id) async {
    final response = await _dio.get(
      '/prescriptions/$id/pdf',
      options: Options(responseType: ResponseType.bytes),
    );
    return List<int>.from(response.data);
  }

  // ── Factures ──────────────────────────────────────────────────
  Future<List<dynamic>> getMyInvoices() async {
    final response = await _dio.get('/facturation/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  // ── Chat ──────────────────────────────────────────────────────
  Future<List<dynamic>> getMyConversations() async {
    final response = await _dio.get('/chat/conversations/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  Future<List<dynamic>> getMessages(int conversationId) async {
    final response = await _dio.get('/chat/conversations/$conversationId/messages/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  Future<Map<String, dynamic>> sendMessage(int conversationId, String content) async {
    final response = await _dio.post(
      '/chat/conversations/$conversationId/messages/',
      data: {'contenu': content},
    );
    return response.data;
  }

  // ── Hospitalisations ──────────────────────────────────────────
  Future<List<dynamic>> getMyHospitalisations() async {
    final response = await _dio.get('/hospitalisations/');
    return response.data is List ? response.data : response.data['results'] ?? [];
  }

  // ── Soins / Constantes ────────────────────────────────────────
  Future<List<dynamic>> getMyVitals(int hospitalisationId) async {
    final response = await _dio.get('/soins/constantes/$hospitalisationId');
    return response.data is List ? response.data : [];
  }

  // ── Dashboard patient ─────────────────────────────────────────
  Future<Map<String, dynamic>> getDashboardSummary() async {
    final response = await _dio.get('/dashboard/summary');
    return response.data;
  }
}

final apiService = ApiService();
final secureStorage = SecureStorage();
