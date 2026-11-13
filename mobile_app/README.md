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

## FlutLab
Import the repository's `mobile_app` Flutter project (or upload this folder as a Flutter project). If the environment reports missing Android platform files, run the platform-generation command above if the FlutLab terminal supports it, then build the APK. Keep generated platform files in the project when exporting/downloading the source.

## Development status
This is the initial Flutter shell only. Workout, account, Google Sheets sync, offline storage, analytics, and AI Coach are implemented in later roadmap phases. Do not use it for real personal data yet.

See the repository-root [ANDROID_ROADMAP.md](../ANDROID_ROADMAP.md) for phases, architecture decisions, and acceptance checks.
