import 'dart:convert';

import 'package:http/http.dart' as http;

import 'auth_session.dart';

class AuthApiException implements Exception {
  const AuthApiException(this.message, {this.statusCode, this.code});
  final String message;
  final int? statusCode;
  final String? code;

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
  }) => _sendAuth({
    'action': 'signup',
    'email': email.trim().toLowerCase(),
    'password': password,
    'display_name': displayName.trim(),
  });

  Future<AuthSession> signIn({
    required String email,
    required String password,
  }) => _sendAuth({
    'action': 'login',
    'email': email.trim().toLowerCase(),
    'password': password,
  });

  /// Apps Script ContentService redirects its response to a one-time
  /// script.googleusercontent.com URL. Dart does not automatically follow
  /// 302 redirects for POST requests, so follow the response with a bounded
  /// GET. Never forward credentials or request bodies to the redirect host.
  Future<http.Response> _postJson(Map<String, Object?> body) async {
    final request = http.Request('POST', baseUri)
      ..followRedirects = false
      ..headers.addAll(const {
        'content-type': 'application/json',
        'accept': 'application/json',
      })
      ..body = jsonEncode(body);
    var response = await http.Response.fromStream(await _client.send(request));

    for (var hop = 0; hop < 5; hop++) {
      if (![301, 302, 303, 307, 308].contains(response.statusCode)) {
        return response;
      }
      final location = response.headers['location'];
      if (location == null || location.isEmpty) {
        throw AuthApiException(
          'The authentication server returned an incomplete redirect.',
          statusCode: response.statusCode,
        );
      }
      final target = baseUri.resolve(location);
      if (target.scheme != 'https' ||
          target.host != 'script.googleusercontent.com') {
        throw AuthApiException(
          'The authentication server returned an untrusted redirect.',
          statusCode: response.statusCode,
        );
      }
      final redirect = http.Request('GET', target)..followRedirects = false;
      response = await http.Response.fromStream(await _client.send(redirect));
    }
    throw const AuthApiException('The authentication server redirected too many times.');
  }

  Future<AuthSession> _sendAuth(Map<String, Object?> body) async {
    final response = await _postJson(body);
    final decoded = _decode(response);
    if (decoded['error'] is String || response.statusCode < 200 || response.statusCode >= 300) {
      throw AuthApiException(
        decoded['error'] is String ? decoded['error'] as String : 'Authentication failed.',
        statusCode: response.statusCode,
        code: decoded['code'] is String ? decoded['code'] as String : null,
      );
    }
    return AuthSession.fromJson(decoded);
  }

  Future<Map<String, dynamic>> getProfile(AuthSession session) async {
    final response = await _postJson({
      'action': 'profile',
      'access_token': session.accessToken,
    });
    final decoded = _decode(response);
    if (decoded['error'] is String || response.statusCode < 200 || response.statusCode >= 300) {
      throw AuthApiException(
        decoded['error'] is String ? decoded['error'] as String : 'Profile request failed.',
        statusCode: response.statusCode,
      );
    }
    return decoded;
  }

  Future<void> logout(AuthSession session) async {
    final response = await _postJson({
      'action': 'logout',
      'access_token': session.accessToken,
    });
    final decoded = _decode(response);
    if (decoded['error'] is String || response.statusCode < 200 || response.statusCode >= 300) {
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
