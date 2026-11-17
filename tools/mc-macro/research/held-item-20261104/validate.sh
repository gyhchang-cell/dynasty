#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/.build/candidates/held-item-1102"
SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk
FIXTURE="$ROOT/.build/candidates/cline-audit-20261104/combat-fixture.json"
RESOURCES="$ROOT/.build/candidates/cline-audit-20261104/app/mcPvPmax.app/Contents/Resources"
mkdir -p "$OUT"
COMMON=("$ROOT/Sources/F3Model.swift" "$ROOT/Sources/Sprint.swift" "$ROOT/Sources/Anchor.swift" "$ROOT/Sources/Combat.swift")
for SUITE in Combat HeldItem; do
    swiftc -sdk "$SDK" -swift-version 5 "${COMMON[@]}" "$ROOT/Tests/$SUITE/main.swift" -o "$OUT/$SUITE-tests"
    "$OUT/$SUITE-tests" "$FIXTURE" | tee "$OUT/$SUITE-tests.log"
done
swiftc -sdk "$SDK" -swift-version 5 "${COMMON[@]}" "$ROOT/Sources/ModernTelemetry.swift" "$ROOT/Tests/ModernTelemetry/main.swift" -o "$OUT/telemetry-tests"
"$OUT/telemetry-tests" "$FIXTURE" "$RESOURCES" | tee "$OUT/telemetry-tests.log"
swiftc -sdk "$SDK" -swift-version 5 "$ROOT/Sources/Sprint.swift" "$ROOT/Tests/ForceSprint/main.swift" -o "$OUT/sprint-tests"
"$OUT/sprint-tests" | tee "$OUT/sprint-tests.log"
swiftc -sdk "$SDK" -swift-version 5 "$ROOT/Sources/InventoryPolicy.swift" "$ROOT/Tests/Inventory/main.swift" -o "$OUT/inventory-tests"
"$OUT/inventory-tests" | tee "$OUT/inventory-tests.log"
swiftc -sdk "$SDK" -swift-version 5 "$ROOT/Sources/Policy.swift" "$ROOT/Sources/F3Model.swift" "$ROOT/Sources/InventoryPolicy.swift" "$ROOT/Sources/GameTelemetry.swift" "$ROOT/Sources/TellyController.swift" "$ROOT/Tests/main.swift" -o "$OUT/core-tests"
"$OUT/core-tests" | tee "$OUT/core-tests.log"