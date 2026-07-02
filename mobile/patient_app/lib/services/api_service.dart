import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String _baseUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator
  static const _storage = FlutterSecureStorage();

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
        final token = await _storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final token = await _storage.read(key: 'access_token');
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
      final refresh = await _storage.read(key: 'refresh_token');
      if (refresh == null) return false;
      final response = await _dio.post('/auth/refresh/', data: {'refresh': refresh});
      await _storage.write(key: 'access_token', value: response.data['access']);
      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _dio.post('/auth/login/', data: {
      'username': username,
      'password': password,
    });
    await _storage.write(key: 'access_token',  value: response.data['access']);
    await _storage.write(key: 'refresh_token', value: response.data['refresh']);
    if (response.data['user'] != null) {
      await _storage.write(key: 'user_data', value: response.data['user'].toString());
    }
    return response.data;
  }

  Future<void> logout() async {
    await _storage.deleteAll();
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.read(key: 'access_token');
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
