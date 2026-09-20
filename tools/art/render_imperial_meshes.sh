#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
preview_classpath="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
mkdir -p build/imperial-mesh-preview
javac -proc:none -cp "$preview_classpath" -d build/imperial-mesh-preview tools/art/RenderImperialMeshes.java
java -Djava.awt.headless=true -cp "build/imperial-mesh-preview:$preview_classpath" RenderImperialMeshes "$@"
