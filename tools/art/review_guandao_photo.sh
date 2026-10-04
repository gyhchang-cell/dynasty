#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
task_java=${DYNASTY_JAVA_HOME:-/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home}/bin
task_cp="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
task_out=build/guanyu-polish-review
task_gallery=docs/art/guandao-photo-reference
mkdir -p "$task_out"
"$task_java/javac" -proc:none -cp "$task_cp" -d "$task_out" src/main/java/com/dynasty/GuanYuSculptor.java src/main/java/com/dynasty/GuanYuAvatarShape.java tools/art/GuandaoPhotoComparison.java tools/art/ExportImperialMeshes.java tools/art/RenderImperialMeshes.java
"$task_java/java" -Djava.awt.headless=true -cp "$task_out:$task_cp" GuandaoPhotoComparison "$task_gallery"
"$task_java/java" -cp "$task_out:$task_cp" ExportImperialMeshes "$task_out/photo-meshes.json" guandao
for task_part in guandaoBlade weapon; do
    "$task_java/java" -Djava.awt.headless=true -cp "$task_out:$task_cp" RenderImperialMeshes "$task_out/photo-meshes.json" "$task_gallery/$task_part.png" "$task_part" clay-profile
done
