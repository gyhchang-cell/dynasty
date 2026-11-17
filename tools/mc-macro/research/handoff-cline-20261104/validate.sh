#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/.build/candidates/cline-audit-20261104"
SDK="${MC_MACRO_SDK:-$(xcrun --show-sdk-path)}"
if swiftc --version 2>&1 | grep -q 'Swift version 6.1' && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk ]; then
    SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk
fi
mkdir -p "$OUT"
python3 - "$ROOT" "$OUT" <<'PY'
import json,pathlib,sys
root,out=map(pathlib.Path,sys.argv[1:])
evidence=json.loads((root/'research/combat-20261102/duel-toggle1101-no-left.json').read_text())
(out/'combat-fixture.json').write_text(json.dumps(evidence['before']))
PY
COMMON=("$ROOT/Sources/F3Model.swift" "$ROOT/Sources/Sprint.swift" "$ROOT/Sources/Anchor.swift")
swiftc -sdk "$SDK" -swift-version 5 "${COMMON[@]}" "$ROOT/Sources/Combat.swift" "$ROOT/Tests/Combat/main.swift" -o "$OUT/combat-tests"
"$OUT/combat-tests" "$OUT/combat-fixture.json" | tee "$OUT/combat-tests.log"
swiftc -sdk "$SDK" -swift-version 5 "$ROOT/Sources/Sprint.swift" "$ROOT/Tests/ForceSprint/main.swift" -o "$OUT/sprint-tests"
"$OUT/sprint-tests" | tee "$OUT/sprint-tests.log"
swiftc -sdk "$SDK" -swift-version 5 "$ROOT/Sources/InventoryPolicy.swift" "$ROOT/Tests/Inventory/main.swift" -o "$OUT/inventory-tests"
"$OUT/inventory-tests" | tee "$OUT/inventory-tests.log"
swiftc -sdk "$SDK" -swift-version 5 "$ROOT/Sources/Policy.swift" "$ROOT/Sources/F3Model.swift" "$ROOT/Sources/InventoryPolicy.swift" "$ROOT/Sources/GameTelemetry.swift" "$ROOT/Sources/TellyController.swift" "$ROOT/Tests/main.swift" -o "$OUT/core-tests"
"$OUT/core-tests" | tee "$OUT/core-tests.log"
bash "$ROOT/.build/candidates/visual-melee-20261104/test.sh" | tee "$OUT/visual-tests.log"
# Compare against the exact source saved before this handoff, not Git HEAD:
# these files were already untracked/modified by the previous agent.
BASELINE="$OUT/baseline/Sources/Combat.swift"
if [ -f "$BASELINE" ]; then
    REGRESSION="$ROOT/.build/backups/held-item-fix-1102-before/Tests/Combat/main.swift"
    if [ ! -f "$REGRESSION" ]; then REGRESSION="$ROOT/Tests/Combat/main.swift"; fi
    swiftc -sdk "$SDK" -swift-version 5 "${COMMON[@]}" "$BASELINE" "$REGRESSION" -o "$OUT/combat-before"
    if "$OUT/combat-before" "$OUT/combat-fixture.json" > "$OUT/combat-before.log" 2>&1; then
        printf 'ERROR: saved baseline unexpectedly passed the new regression tests\n' >&2
        exit 1
    fi
    grep -q 'passed 101, failed 4' "$OUT/combat-before.log"
    printf 'Saved baseline reproduces 4 new protection failures; current source passes.\n'
fi