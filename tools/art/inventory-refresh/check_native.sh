#!/bin/sh
set -eu
cd "$(dirname "$0")/../../.."
task_jdk=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
task_cp="$(paste -sd: build/classpath/runClient_minecraftClasspath.txt)"
mkdir -p build/maintenance/inventory-refresh-v1/classes
"$task_jdk/bin/javac" -proc:none -cp "$task_cp" -d build/maintenance/inventory-refresh-v1/classes tools/art/inventory-refresh/VerifyInventoryModels.java
"$task_jdk/bin/java" -Djava.awt.headless=true -cp "build/maintenance/inventory-refresh-v1/classes:$task_cp" VerifyInventoryModels "$HOME/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar"
