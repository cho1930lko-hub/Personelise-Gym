/// Apps Script Web App URL supplied using --dart-define=AUTH_API_BASE_URL=...
/// Keep this as a public endpoint only; never place API secrets here.
class AuthConfig {
  static const baseUrl = String.fromEnvironment('AUTH_API_BASE_URL');

  static Uri? get baseUri {
    final value = baseUrl.trim();
    if (value.isEmpty) return null;
    final uri = Uri.tryParse(value);
    if (uri == null || uri.scheme != 'https' || uri.host.isEmpty) return null;
    return uri;
  }
}
