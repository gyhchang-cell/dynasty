#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
task_java=${DYNASTY_JAVA_HOME:-/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home}/bin
task_cp="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
task_out=build/houyi-review
mkdir -p "$task_out"
"$task_java/javac" -proc:none -cp "$task_cp" -d "$task_out" \
  src/main/java/com/dynasty/HouyiAvatarShape.java src/main/java/com/dynasty/HouyiArcherSculpture.java \
  src/main/java/com/dynasty/GuanYuSculptor.java src/main/java/com/dynasty/GuanYuAvatarShape.java \
  src/main/java/com/dynasty/client/ImperialMeshNormals.java \
  tools/art/VerifyHouyiRemaster.java tools/art/ExportImperialMeshes.java tools/art/RenderImperialMeshes.java
"$task_java/java" -cp "$task_out:$task_cp" com.dynasty.VerifyHouyiRemaster
"$task_java/java" -cp "$task_out:$task_cp" ExportImperialMeshes "$task_out/meshes.json" houyi
for task_mode in six clay silhouette front45 portrait; do
  "$task_java/java" -Djava.awt.headless=true -cp "$task_out:$task_cp" RenderImperialMeshes \
    "$task_out/meshes.json" "docs/art/houyi-remaster/$task_mode.png" houyi "$task_mode"
done
