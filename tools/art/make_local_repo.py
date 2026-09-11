#!/usr/bin/env python3
"""把下载好的第三方模组 jar 摆成本地 Maven 仓库，供 ForgeGradle fg.deobf 使用。"""
import os, shutil

ROOT = os.path.expanduser("~/Desktop/dynasty")
REPO = os.path.join(ROOT, "libs", "repo")
SRC = "/tmp/dyn_mods"

ARTEFACTS = [
    ("top.theillusivec4.curios", "curios-forge", "5.14.1+1.20.1", os.path.join(SRC, "curios.jar")),
    ("mezz.jei", "jei-1.20.1-forge", "15.59.0.210", os.path.join(SRC, "jei.jar")),
    ("com.dynpacks", "overflowingbars", "8.0.1", os.path.join(SRC, "overflow.jar")),
    ("com.dynpacks", "puzzleslib", "8.1.33", os.path.join(SRC, "puzzleslib.jar")),
]

POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>{g}</groupId>
  <artifactId>{a}</artifactId>
  <version>{v}</version>
  <packaging>jar</packaging>
</project>
"""

for group, art, ver, jar in ARTEFACTS:
    folder = os.path.join(REPO, *group.split("."), art, ver)
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, "%s-%s.jar" % (art, ver))
    shutil.copy2(jar, target)
    with open(os.path.join(folder, "%s-%s.pom" % (art, ver)), "w", encoding="utf-8") as f:
        f.write(POM.format(g=group, a=art, v=ver))
    print("installed", group, art, ver, os.path.getsize(target), "bytes")
