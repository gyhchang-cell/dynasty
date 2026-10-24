#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
APP="$PWD/dist/MC连点助手.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
MACRO_SDK="${MC_MACRO_SDK:-$(xcrun --show-sdk-path)}"
# This host has a newer SDK alongside its Swift 6.1 toolchain.
if swiftc --version | head -1 | grep -q '6.1' && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk ]; then
    MACRO_SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk
fi
swiftc -sdk "$MACRO_SDK" -O -swift-version 5 -target arm64-apple-macosx13.0 Sources/Policy.swift Sources/main.swift -o "$APP/Contents/MacOS/MCMacro" -framework AppKit -framework ApplicationServices -framework Carbon
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>MCMacro</string>
<key>CFBundleIdentifier</key><string>local.mc-macro.assistant</string>
<key>CFBundleName</key><string>MC连点助手</string>
<key>CFBundleDisplayName</key><string>MC连点助手</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.0.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
<key>NSHighResolutionCapable</key><true/>
<key>NSHumanReadableCopyright</key><string>本地构建的 Minecraft 输入助手</string>
</dict></plist>
PLIST
codesign --force --sign - "$APP"
ditto -c -k --keepParent "$APP" "$PWD/dist/MC连点助手-macOS-arm64.zip"
printf '已生成：%s\n' "$APP"
