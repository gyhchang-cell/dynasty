#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
TELEMETRY_JDK="${MC_TELEMETRY_JDK:-/Users/a15356015027/Library/Java/JavaVirtualMachines/ms-21.0.12.1/Contents/Home}"
VERSION="v$(shasum -a 256 src/local/mcmacro/StateAgent.java | cut -c1-12)"
AGENT_DIR="../.build/telemetry/$VERSION"
mkdir -p "$AGENT_DIR/src" "$AGENT_DIR/classes" ../.build/telemetry/attach
# Version the namespace: a running JVM retains an already loaded agent class.
sed "s/package local.mcmacro;/package local.mcmacro.$VERSION;/" src/local/mcmacro/StateAgent.java > "$AGENT_DIR/src/StateAgent.java"
"$TELEMETRY_JDK/bin/javac" --release 8 -d "$AGENT_DIR/classes" "$AGENT_DIR/src/StateAgent.java"
"$TELEMETRY_JDK/bin/javac" --release 9 --add-modules jdk.attach -d ../.build/telemetry/attach src/local/mcmacro/Attach.java
printf 'Manifest-Version: 1.0\nAgent-Class: local.mcmacro.%s.StateAgent\nCan-Redefine-Classes: false\nCan-Retransform-Classes: false\n\n' "$VERSION" > ../.build/telemetry/MANIFEST.MF
"$TELEMETRY_JDK/bin/jar" cfm ../.build/telemetry/state-agent.jar ../.build/telemetry/MANIFEST.MF -C "$AGENT_DIR/classes" .
