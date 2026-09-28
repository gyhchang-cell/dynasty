#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
task_jdk=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
task_cp="$(paste -sd: build/classpath/runClient_minecraftClasspath.txt)"
mkdir -p build/handheld-mesh-qa
"$task_jdk/bin/javac" -proc:none -cp "$task_cp" -d build/handheld-mesh-qa tools/art/HandheldMeshPreview.java tools/art/VerifyHandheldParents.java
"$task_jdk/bin/java" -cp "build/handheld-mesh-qa:$task_cp" VerifyHandheldParents
"$task_jdk/bin/java" -XstartOnFirstThread -Djava.awt.headless=true -cp "build/handheld-mesh-qa:$task_cp" HandheldMeshPreview
