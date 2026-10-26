#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
APP="$PWD/dist/mcPvPmax.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
MACRO_SDK="${MC_MACRO_SDK:-$(xcrun --show-sdk-path)}"
# This host has a newer SDK alongside its Swift 6.1 toolchain.
if swiftc --version 2>&1 | grep -q 'Swift version 6.1' && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk ]; then
    MACRO_SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk
fi
MACRO_EXTRA=()
MACRO_HEADER="$MACRO_SDK/System/Library/Frameworks/CoreServices.framework/Frameworks/CarbonCore.framework/Headers/MacErrors.h"
if [ ! -f "$MACRO_HEADER" ]; then
    mkdir -p .build/sdk-compat/CarbonCore
    MACRO_LOCAL_HEADER="$PWD/.build/sdk-compat/CarbonCore/MacErrors.h"
    if [ ! -f "$MACRO_LOCAL_HEADER" ]; then
        curl -fsSL --max-time 30 'https://raw.githubusercontent.com/phracker/MacOSX-SDKs/master/MacOSX11.3.sdk/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/CarbonCore.framework/Versions/A/Headers/MacErrors.h' -o "$MACRO_LOCAL_HEADER"
    fi
    [ "$(shasum -a 256 "$MACRO_LOCAL_HEADER" | cut -d ' ' -f 1)" = c1843d1e6719c06ee70f04f2cd086b509cf1d49fbfc4571a9b7bf71584372588 ]
    python3 - "$MACRO_SDK" "$MACRO_LOCAL_HEADER" <<'PY'
import json, pathlib, sys
sdk, header = sys.argv[1:]
paths = ['System/Library/Frameworks/CoreServices.framework/Frameworks/CarbonCore.framework/Headers/MacErrors.h', 'System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/CarbonCore.framework/Versions/A/Headers/MacErrors.h']
pathlib.Path('.build/sdk-overlay.json').write_text(json.dumps({'version': 0, 'roots': [{'type': 'file', 'name': sdk + '/' + p, 'external-contents': header} for p in paths]}))
PY
    MACRO_EXTRA=(-vfsoverlay "$PWD/.build/sdk-overlay.json")
fi
bash telemetry/build.sh
MACRO_AGENT_VERSION="v$(shasum -a 256 telemetry/src/local/mcmacro/StateAgent.java | cut -c1-12)"
mkdir -p "$APP/Contents/Resources/telemetry/attach/local/mcmacro"
cp .build/telemetry/state-agent.jar "$APP/Contents/Resources/telemetry/state-agent-$MACRO_AGENT_VERSION.jar"
cp .build/telemetry/attach/local/mcmacro/Attach.class "$APP/Contents/Resources/telemetry/attach/local/mcmacro/Attach.class"
printf '{"agentJar":"state-agent-%s.jar"}\n' "$MACRO_AGENT_VERSION" > "$APP/Contents/Resources/telemetry/runtime.json"
swiftc -sdk "$MACRO_SDK" "${MACRO_EXTRA[@]}" -O -swift-version 5 -target arm64-apple-macosx13.0 Sources/Policy.swift Sources/HardwareMouse.swift Sources/F3Model.swift Sources/GameTelemetry.swift Sources/F3PixelReader.swift Sources/F3Capture.swift Sources/TellyController.swift Sources/BridgeIntegration.swift Sources/main.swift -o "$APP/Contents/MacOS/MCMacro" -framework AppKit -framework ApplicationServices -framework Carbon -framework IOKit -framework Vision -framework ScreenCaptureKit
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>MCMacro</string>
<key>CFBundleIdentifier</key><string>local.mc-macro.assistant</string>
<key>CFBundleName</key><string>MC连点助手</string>
<key>CFBundleDisplayName</key><string>MC连点助手</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.8.9</string>
<key>CFBundleVersion</key><string>19</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
<key>NSHighResolutionCapable</key><true/>
<key>NSHumanReadableCopyright</key><string>本地构建的 Minecraft 输入助手</string>
</dict></plist>
PLIST
codesign --force --sign - "$APP"
ditto -c -k --keepParent "$APP" "$PWD/dist/mcPvPmax-macOS-arm64.zip"
printf '已生成：%s\n' "$APP"
