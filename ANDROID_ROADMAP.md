# Personelise Gym — Android App Roadmap

## Product boundary
This is a personal fitness and workout app. It is not a gym membership, billing, admission, invoice, or payment-management system.

## Product requirements
- Independent accounts for each person (initially the owner, spouse, and one companion; no hard-coded user count).
- Private profile, workouts, body measurements, goals, weekly tracker, exercise checklist, preferences, and AI Coach history per account.
- Google Sheets remains the requested cloud data store.
- Offline-first: write locally first, then sync safely when connectivity returns.
- Keep the existing Streamlit app and its data untouched during the Android migration.

## Critical architecture decision
The Android APK must never contain a Google service-account private key, Groq API key, or privileged spreadsheet credential. A mobile client is not a safe place for shared secrets.

Use a Google Apps Script Web App as a thin authenticated API in front of the owner's Google Spreadsheet:
- Apps Script owns the spreadsheet access and server-side secrets in Script Properties.
- Registration/login returns a short-lived signed session token.
- Every API request validates the token and derives the user ID on the server; never trust a client-supplied user ID for authorization.
- Every row is partitioned by server-verified user ID.
- Passwords are salted/hashed server-side; never store plaintext passwords.
- Add rate limiting, token expiry/revocation, input validation, and audit fields.
- The app stores only the user's session token in Android secure storage.
- AI requests must go through a server-side proxy; never embed Groq keys in the APK.

This design must be threat-reviewed before real personal data is used. Google Sheets is not a high-security database; if stronger isolation or scale becomes necessary, migrate the backend to Supabase/Postgres with RLS.

## Planned Google Spreadsheet tabs
- Users: account metadata and password hashes (never plaintext).
- WorkoutLog: per-user workout and set records.
- BodyStats: per-user height, weight, measurements, BMI inputs, and history.
- WeeklyTracker: per-user weekly targets and completion.
- Settings: per-user goals, units, theme, and preferences.
- ExerciseChecklist: per-user checklist state.
- AIHistory: optional per-user AI conversation history.
- SyncMeta: per-user cursor/version and server-side sync metadata.

Every user-owned tab must include a stable user_id and record_id. Server-generated timestamps and updated_at values are authoritative.

## Phases and acceptance gates

### Phase 0 — Repository audit and safe workspace
- Inspect current Streamlit app, requirements, tests, current branches, and prior profile/login implementation.
- Create a separate Android development branch; do not rewrite main.
- Preserve current app and Google Sheet data.
- Gate: audit notes and isolated branch exist.

### Phase 1 — Flutter foundation
- Create a Flutter project under mobile_app/.
- Add app theme, responsive navigation shell, app metadata, linting, and widget smoke test.
- Add Flutter CI (dependency resolution, analyze, tests).
- Gate: Flutter CI passes; no Streamlit files changed.

### Phase 2 — Data model and local-first storage
- Define typed entities and migrations.
- Add SQLite/Drift local database, repository interfaces, secure session storage.
- Add schema tests and per-user local partitioning.
- Gate: create/read/update/delete tests pass with two isolated users.

### Phase 3 — Accounts and profile privacy
- Implement sign-up, login, logout, token refresh/expiry, profile setup.
- Implement Apps Script API and server-side validation.
- Gate: account A cannot read or mutate account B data, including forged user_id requests.

### Phase 4 — Google Sheets API and synchronization
- Build authenticated Apps Script endpoints and spreadsheet schema setup/migration.
- Implement queued writes, retries, idempotency keys, conflict handling, pull cursor, and sync status.
- Gate: online/offline/reconnect tests pass; duplicate writes are prevented.

### Phase 5 — Workout experience
- Exercise library and muscle groups.
- Multi-set logging (weight/reps), checklist, workout completion, stopwatch, rest timer.
- Gate: workout survives app restart and syncs once.

### Phase 6 — Progress and dashboard
- Weekly tracker, streaks, workout history, exercise trends, body stats, user-specific height/BMI, goals, charts.
- Gate: analytics are computed only from the signed-in user's records.

### Phase 7 — AI Coach
- Context-aware plans, Quick Ask, fat-loss/strength/diet guidance, optional AI history.
- Server-side AI proxy and quota/error handling.
- Gate: no API key in APK/repository; user context is isolated.

### Phase 8 — Remaining features and export
- Music links, preferences, CSV export, JSON backup/restore, data portability.
- Gate: backup/restore round-trip tests pass and never mix users.

### Phase 9 — QA and security
- Unit, widget, integration, API authorization, offline, sync, accessibility, small-screen, and regression tests.
- Compare feature inventory against Streamlit app.
- Gate: all critical checks pass and known limitations are documented.

### Phase 10 — Android release
- Configure app ID, icon, version, signing instructions, release build.
- Build APK where a verified Android SDK/build environment is available; otherwise provide a complete FlutLab-importable Flutter project and exact build steps.
- Gate: APK installs, launches, login works, data isolation and sync smoke tests pass.

## Working rules
1. Work only on android/flutter-foundation until a phase is complete; keep main unchanged.
2. Never delete or overwrite the original Streamlit app or existing spreadsheet data.
3. At each phase, run available tests and report exactly what passed, failed, or remains unverified.
4. Do not claim an APK is built unless the APK file exists and installation/build validation has actually succeeded.
5. Do not use production personal data during early tests; use synthetic accounts and rows.
