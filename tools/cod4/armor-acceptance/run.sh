#!/bin/sh
set -eu
cd "$(dirname "$0")/../../.."
base="$PWD/tools/cod4/armor-acceptance/.work"
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
export GRADLE_USER_HOME="$base/gradle-home"
exec ./gradlew --offline --no-daemon --max-workers=2 --project-cache-dir "$base/project-cache" -I tools/cod4/armor-acceptance/armor.init.gradle -ParmorRun="${1:-server}" runGameTestServer
