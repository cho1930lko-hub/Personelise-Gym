# Personelise Gym — Flutter Android app

This folder contains the Flutter/Dart Android application. The existing Streamlit app remains at the repository root and is not replaced.

## Requirements
- Flutter stable (Dart 3.3+)
- Android SDK and Java 17 for local APK builds

## Run locally
From this directory:

```bash
flutter pub get
flutter run
```

If this source checkout does not contain Android platform files yet, generate them once:

```bash
flutter create --platforms=android --project-name personelise_gym .
```

Then build a debug APK:

```bash
flutter build apk --debug
```

The APK is written to `build/app/outputs/flutter-apk/app-debug.apk`.

## Local database security
- Production Android/iOS database access uses SQLCipher 4 through `sqflite_sqlcipher`.
- A 256-bit random database key is generated once and stored through `flutter_secure_storage`; storage errors are not silently reset.
- Unit tests inject SQLite FFI and an in-memory secure store. FFI tests verify repository behavior, not SQLCipher encryption itself.
- Keep Android `minSdk` at 23 or higher for the selected secure-storage package.
- In `android/app/src/main/AndroidManifest.xml`, set `android:allowBackup="false"` on the `<application>` element. This avoids restoring encrypted preferences without the matching Android Keystore key.
- In `android/app/proguard-rules.pro`, include `-keep class net.sqlcipher.** { *; }` for release builds with code shrinking.

Do not delete the secure database key to troubleshoot a database-open error. The existing encrypted database becomes unreadable without its original key. A future explicit backup/restore flow must handle key recovery separately.

## FlutLab
Import the repository's `mobile_app` Flutter project (or upload this folder as a Flutter project). If the environment reports missing Android platform files, run the platform-generation command above if the FlutLab terminal supports it, then build the APK. Keep generated platform files in the project when exporting/downloading the source. Confirm FlutLab's Android minSdk is 23 or higher and apply the Android backup and ProGuard settings above before release builds.

## Development status
The Flutter shell and encrypted local database foundation are in progress. Accounts, Google Sheets sync, workout screens, analytics, and AI Coach are not implemented yet. Do not use it for real personal data until authentication, backup/recovery, sync authorization, and device-level SQLCipher tests have passed.

See the repository-root [ANDROID_ROADMAP.md](../ANDROID_ROADMAP.md) for phases, architecture decisions, and acceptance checks.
