#!/bin/sh
# Independent, read-only geometry validation. Compiles current shape sources into a disposable
# tool directory without waiting on or modifying the concurrent Forge renderer build.
set -eu
cd "$(dirname "$0")/../.."
verify_output=build/imperial-mesh-preview/verification
verify_classpath="build/classes/java/main:$(paste -sd: build/classpath/runGameTestServer_minecraftClasspath.txt)"
mkdir -p "$verify_output"
javac -proc:none -cp "$verify_classpath" -d "$verify_output" \
  src/main/java/com/dynasty/HouyiAvatarShape.java \
  src/main/java/com/dynasty/GuanYuSculptor.java \
  src/main/java/com/dynasty/GuanYuAvatarShape.java \
  src/main/java/com/dynasty/client/ImperialMeshNormals.java \
  src/main/java/com/dynasty/client/ImperialDragonMesh.java \
  src/main/java/com/dynasty/client/ImperialWeaponGeometry.java \
  src/main/java/com/dynasty/client/BowSigilGeometry.java \
  tools/art/VerifyGuanYuRemaster.java tools/art/VerifyImperialDragon.java tools/art/VerifyDragonSurfaceClearance.java \
  tools/art/GuanYuPreview.java tools/art/ImperialWeaponPreview.java
verify_runtime="$verify_output:$verify_classpath"
java -Xmx2g -cp "$verify_runtime" com.dynasty.VerifyGuanYuRemaster
java -Xmx2g -cp "$verify_runtime" VerifyImperialDragon
java -Xmx2g -cp "$verify_runtime" VerifyDragonSurfaceClearance --strict
java -Xmx2g -cp "$verify_runtime" GuanYuPreview "$verify_output/guanyu-legacy.svg"
java -Xmx2g -cp "$verify_runtime" ImperialWeaponPreview "$verify_output/imperial-weapons-legacy.svg"
node --check tools/art/imperial-mesh-viewer.js
git diff --check -- tools/art
printf '%s\n' 'PASS: source geometry verifiers, both legacy diagnostics, viewer syntax and whitespace checks.'
