#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/emulator-acceptance
APK="$GITHUB_WORKSPACE/build/app/outputs/flutter-apk/app-debug.apk"
test -s "$APK"
adb install -r "$APK"
AAPT="$(find "$ANDROID_HOME/build-tools" -type f -name aapt | sort -V | tail -n 1)"
test -n "$AAPT"
PKG="$("$AAPT" dump badging "$APK" | sed -n "s/^package: name='\\([^']*\\)'.*/\\1/p" | head -1)"
test -n "$PKG"
printf 'package=%s\n' "$PKG" | tee build/emulator-acceptance/identity.txt
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1
sleep 12
adb shell pidof "$PKG"
adb exec-out screencap -p > build/emulator-acceptance/launch.png
adb shell uiautomator dump /sdcard/window.xml || true
adb pull /sdcard/window.xml build/emulator-acceptance/window.xml || true
adb shell am force-stop "$PKG"
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1
sleep 6
adb shell pidof "$PKG"
adb exec-out screencap -p > build/emulator-acceptance/relaunch.png
test -s build/emulator-acceptance/launch.png
test -s build/emulator-acceptance/relaunch.png
echo "EMULATOR_ACCEPTANCE_PASS package=$PKG"
