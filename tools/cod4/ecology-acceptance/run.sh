#!/bin/sh
set -eu
cd "$(dirname "$0")/../../.."
base="$PWD/tools/cod4/ecology-acceptance/.work"
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
export GRADLE_USER_HOME="$base/gradle-home"
./gradlew --offline --no-daemon --max-workers=2 --project-cache-dir "$base/project-cache" -I tools/cod4/ecology-acceptance/qa.init.gradle -PecologyRun="${1:-normal-run1}" runServer
