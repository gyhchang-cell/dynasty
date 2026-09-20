#!/bin/sh
# Offscreen native GPU validation using production shaders; output is not a Minecraft screenshot.
set -eu
task_repo=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$task_repo"
task_java_dir=${DYNASTY_JAVA_HOME:-/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home}
task_java="$task_java_dir/bin/java"
task_javac="$task_java_dir/bin/javac"
if [ ! -x "$task_java" ]; then task_java=java; task_javac=javac; fi
task_cp="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
mkdir -p build/guardian-shader-preview
"$task_javac" -proc:none -cp "$task_cp" -d build/guardian-shader-preview \
  src/main/java/com/dynasty/HouyiAvatarShape.java \
  src/main/java/com/dynasty/GuanYuSculptor.java \
  src/main/java/com/dynasty/GuanYuAvatarShape.java \
  src/main/java/com/dynasty/client/ImperialMeshNormals.java \
  tools/art/GuardianShaderPreview.java
if [ "$(uname -s)" = Darwin ]; then
  "$task_java" -XstartOnFirstThread -cp "build/guardian-shader-preview:$task_cp" GuardianShaderPreview "$@"
else
  "$task_java" -cp "build/guardian-shader-preview:$task_cp" GuardianShaderPreview "$@"
fi
