#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
: "${TELLY_FORGE_JAR:?Set TELLY_FORGE_JAR to the installed Forge 1.8.9 jar}"
mkdir -p .build/classes .build/test dist
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$TELLY_FORGE_JAR" -d .build/classes src/local/mcmacro/*.java
javac --release 8 -encoding UTF-8 -Xlint:-options -d .build/test src/local/mcmacro/TellyPlan.java src/local/mcmacro/Reflect.java test/local/mcmacro/TellyPlanTest.java
java -cp .build/test local.mcmacro.TellyPlanTest
cat > .build/classes/mcmod.info <<'EOF'
[{"modid":"mcmacro_telly","name":"MC Telly Assistant (Experimental)","version":"0.1.0","mcversion":"1.8.9","description":"Hold V for experimental straight-line Telly. Release V to stop. Reads live sensitivity. Requires standing at a full-block edge and facing a cardinal direction. Not game-tested.","clientSideOnly":true}]
EOF
jar cf dist/mcmacro-telly-1.8.9-0.1.0.jar -C .build/classes .
printf 'Built: %s\n' "$PWD/dist/mcmacro-telly-1.8.9-0.1.0.jar"
