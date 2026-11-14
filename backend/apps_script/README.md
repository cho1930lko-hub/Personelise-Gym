# Apps Script account API deployment

This is a source-only backend. It has **not** been deployed and must not be pointed at the existing Streamlit spreadsheet.

## Safe setup (use a new test spreadsheet)

1. Create a brand-new, empty Google Spreadsheet dedicated to Android test accounts.
2. Open Extensions → Apps Script, paste `backend/apps_script/Code.gs`.
3. In Project Settings → Script Properties, add:
   - `SPREADSHEET_ID`: ID of the new test spreadsheet.
   - `TOKEN_SECRET`: at least 32 random bytes encoded as hex/base64url.
   - `PASSWORD_PEPPER`: a different, independently generated 32+ random byte secret.
4. Keep the Apps Script project restricted to its owner/editors. Never commit these values to Git.
5. Deploy → New deployment → Web app; execute as the owner. Access must allow the Android app to call it. Copy the `/exec` URL.
6. Build Flutter with `--dart-define=AUTH_API_BASE_URL=https://script.google.com/macros/s/DEPLOYMENT_ID/exec`.
7. Test only with synthetic accounts. Verify signup, login, profile, logout, expired token, revoked token, repeated wrong passwords, and two-account separation before using any real data.

## API contract

Every call is POST JSON to the exact Web App URL:
- `{action:"signup", email, password, display_name}`
- `{action:"login", email, password}`
- `{action:"profile", access_token}`
- `{action:"logout", access_token}`

Signup/login return `access_token`, `user_id`, `email`, `display_name`, and `expires_at`. Profile identity is derived from the signed token; the client does not send a user ID. Tokens are HMAC-SHA256 signed, expire after 12 hours, and are checked against a server-side revocation/session table. Passwords use salted PBKDF2-HMAC-SHA256 plus a server-only pepper. Login attempts are rate-limited by normalized email. The exact PBKDF2 helper is parameterized for known-answer testing; run `node backend/apps_script/tests/pbkdf2.test.cjs` from the repository root to compare it against Node/OpenSSL PBKDF2 vectors.

## Important limitations and security gate

- Apps Script ContentService does not let this web app set arbitrary HTTP response status codes; API errors are JSON `{error: "..."}` envelopes and the Flutter client checks the envelope.
- Login attempts are reserved atomically per normalized email before password verification, preventing concurrent requests from bypassing the configured ceiling. The limit is still per email, not per IP/device, so it does not stop distributed attacks or targeted account lockout. Apps Script is not a hardened identity platform and Google Sheets is not a high-security datastore.
- This initial backend only implements account creation, login, profile identity, and logout. It does not yet implement the per-user fitness-data sync API, email verification, password reset, account recovery, or refresh tokens.
- Signup now neutralizes formula-leading display names before writing them to Sheets, validates existing tab headers, and rejects malformed/overlong token claims.
- The Apps Script PBKDF2 helper has a local Node/OpenSSL known-answer test, but this does not execute the Apps Script runtime or benchmark 210,000 rounds. The code has not been executed against a deployed Apps Script project. Before production, run an independent security review and end-to-end tests with two synthetic users, including tampered/forged user IDs, modified tokens, token replay after logout, and cross-account read/write attempts.
- Never point this backend at the existing Streamlit production spreadsheet. Create a separate spreadsheet and keep all test records synthetic.
