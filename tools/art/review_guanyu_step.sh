#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
step=${1:?step name required}
task_java=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin
task_cp="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
task_out=build/guanyu-polish-review
mkdir -p "$task_out"
"$task_java/javac" -proc:none -cp "$task_cp" -d "$task_out" src/main/java/com/dynasty/GuanYuSculptor.java src/main/java/com/dynasty/GuanYuAvatarShape.java tools/art/ExportImperialMeshes.java tools/art/RenderImperialMeshes.java
"$task_java/java" -cp "$task_out:$task_cp" ExportImperialMeshes "$task_out/meshes.json" guanyu
"$task_java/java" -Djava.awt.headless=true -cp "$task_out:$task_cp" RenderImperialMeshes "$task_out/meshes.json" "docs/art/guanyu-polish/$step.png" guanyu six
