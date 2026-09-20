#!/bin/sh
# Run after compileJava; only exports the currently compiled, real game meshes.
set -eu
cd "$(dirname "$0")/../.."
preview_target="${1:-build/imperial-mesh-preview/after/meshes.json}"
preview_classpath="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
mkdir -p build/imperial-mesh-preview
javac -proc:none -cp "$preview_classpath" -d build/imperial-mesh-preview src/main/java/com/dynasty/client/ImperialMeshNormals.java tools/art/ExportImperialMeshes.java
java -cp "build/imperial-mesh-preview:$preview_classpath" ExportImperialMeshes "$preview_target"
