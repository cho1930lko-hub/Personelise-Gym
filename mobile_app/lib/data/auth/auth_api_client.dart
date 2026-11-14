import 'dart:convert';

import 'package:http/http.dart' as http;

import 'auth_session.dart';

class AuthApiException implements Exception {
  const AuthApiException(this.message, {this.statusCode});
  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

/// Talks only to the authenticated Apps Script API. The endpoint must be
/// supplied at build/runtime; no spreadsheet or privileged key is shipped.
class AuthApiClient {
  AuthApiClient({
    required this.baseUri,
    http.Client? client,
  }) : _client = client ?? http.Client();

  final Uri baseUri;
  final http.Client _client;

  Future<AuthSession> signUp({
    required String email,
    required String password,
    required String displayName,
  }) => _sendAuth('signup', {
    'email': email.trim().toLowerCase(),
    'password': password,
    'display_name': displayName.trim(),
  });

  Future<AuthSession> signIn({
    required String email,
    required String password,
  }) => _sendAuth('login', {
    'email': email.trim().toLowerCase(),
    'password': password,
  });

  Future<AuthSession> _sendAuth(String action, Map<String, Object?> body) async {
    final response = await _client.post(
      baseUri.resolve(action),
      headers: const {'content-type': 'application/json', 'accept': 'application/json'},
      body: jsonEncode(body),
    );
    final decoded = _decode(response);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw AuthApiException(
        decoded['error'] is String ? decoded['error'] as String : 'Authentication failed.',
        statusCode: response.statusCode,
      );
    }
    return AuthSession.fromJson(decoded);
  }

  Future<Map<String, dynamic>> getProfile(AuthSession session) async {
    final response = await _client.get(
      baseUri.resolve('profile'),
      headers: {'authorization': 'Bearer ${session.accessToken}', 'accept': 'application/json'},
    );
    final decoded = _decode(response);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw AuthApiException(
        decoded['error'] is String ? decoded['error'] as String : 'Profile request failed.',
        statusCode: response.statusCode,
      );
    }
    return decoded;
  }

  Future<void> logout(AuthSession session) async {
    final response = await _client.post(
      baseUri.resolve('logout'),
      headers: {'authorization': 'Bearer ${session.accessToken}'},
    );
    if (response.statusCode < 200 || response.statusCode >= 300) {
      final decoded = _decode(response);
      throw AuthApiException(
        decoded['error'] is String ? decoded['error'] as String : 'Logout failed.',
        statusCode: response.statusCode,
      );
    }
  }

  Map<String, dynamic> _decode(http.Response response) {
    try {
      final value = jsonDecode(response.body);
      if (value is Map<String, dynamic>) return value;
    } on FormatException {
      // Report a stable API error below.
    }
    throw AuthApiException('The authentication server returned an invalid response.',
        statusCode: response.statusCode);
  }

  void close() => _client.close();
}
