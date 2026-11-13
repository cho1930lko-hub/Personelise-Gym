#!/usr/bin/env bash
set -euo pipefail

manifest="android/app/src/main/AndroidManifest.xml"
if [[ ! -f "$manifest" ]]; then
  echo "Android manifest not found: $manifest" >&2
  exit 1
fi

if grep -q 'android:allowBackup=' "$manifest"; then
  sed -i -E 's/android:allowBackup="[^"]*"/android:allowBackup="false"/' "$manifest"
else
  sed -i 's/<application/<application android:allowBackup="false"/' "$manifest"
fi

gradle_files=()
[[ -f android/app/build.gradle.kts ]] && gradle_files+=(android/app/build.gradle.kts)
[[ -f android/app/build.gradle ]] && gradle_files+=(android/app/build.gradle)

if [[ ${#gradle_files[@]} -eq 0 ]]; then
  echo "Android app Gradle file not found." >&2
  exit 1
fi

min_sdk_updated=false
for file in "${gradle_files[@]}"; do
  if grep -q 'minSdk = flutter.minSdkVersion' "$file"; then
    sed -i 's/minSdk = flutter.minSdkVersion/minSdk = 23/' "$file"
    min_sdk_updated=true
  elif grep -q 'minSdkVersion flutter.minSdkVersion' "$file"; then
    sed -i 's/minSdkVersion flutter.minSdkVersion/minSdkVersion 23/' "$file"
    min_sdk_updated=true
  elif grep -Eq 'minSdk(Version)?[[:space:]]*=[[:space:]]*23|^[[:space:]]*minSdkVersion[[:space:]]+23' "$file"; then
    min_sdk_updated=true
  fi
done

if [[ "$min_sdk_updated" != true ]]; then
  echo "Could not safely set Android minSdk to 23; inspect the generated Gradle file." >&2
  exit 1
fi

mkdir -p android/app
cat > android/app/proguard-rules.pro <<'RULES'
-keep class net.sqlcipher.** { *; }
RULES

echo "Android security settings applied: minSdk 23, backup disabled, SQLCipher keep rule installed."
