class AuthSession {
  const AuthSession({
    required this.accessToken,
    required this.userId,
    required this.email,
    required this.expiresAt,
  });

  final String accessToken;
  final String userId;
  final String email;
  final DateTime expiresAt;

  bool get isExpired => !DateTime.now().toUtc().isBefore(expiresAt.toUtc());

  factory AuthSession.fromJson(Map<String, dynamic> json) {
    final token = json['access_token'];
    final userId = json['user_id'];
    final email = json['email'];
    final expiresAt = json['expires_at'];
    if (token is! String || token.isEmpty ||
        userId is! String || userId.isEmpty ||
        email is! String || email.isEmpty ||
        expiresAt is! String) {
      throw const FormatException('The authentication server returned an invalid session.');
    }
    return AuthSession(
      accessToken: token,
      userId: userId,
      email: email,
      expiresAt: DateTime.parse(expiresAt).toUtc(),
    );
  }

  Map<String, Object?> toJson() => {
    'access_token': accessToken,
    'user_id': userId,
    'email': email,
    'expires_at': expiresAt.toUtc().toIso8601String(),
  };
}
