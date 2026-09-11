#!/usr/bin/env bash
# 下载 Dynasty 整合包所需的第三方模组（本体 jar 请自行复制进来）
set -e
cd "$(dirname "$0")"
mkdir -p mods
cd mods

echo ">> curios-forge-5.14.1+1.20.1.jar"
curl -L --retry 2 -o "curios-forge-5.14.1+1.20.1.jar" "https://cdn.modrinth.com/data/vvuO3ImH/versions/IPQlZkz1/curios-forge-5.14.1%2B1.20.1.jar"
echo ">> jei-1.20.1-forge-15.59.0.210.jar"
curl -L --retry 2 -o "jei-1.20.1-forge-15.59.0.210.jar" "https://cdn.modrinth.com/data/u6dRKJwZ/versions/4vbuxppk/jei-1.20.1-forge-15.59.0.210.jar"
echo ">> OverflowingBars-v8.0.1-1.20.1-Forge.jar"
curl -L --retry 2 -o "OverflowingBars-v8.0.1-1.20.1-Forge.jar" "https://cdn.modrinth.com/data/XD7XOrAF/versions/w90XIUWB/OverflowingBars-v8.0.1-1.20.1-Forge.jar"
echo ">> PuzzlesLib-v8.1.33-1.20.1-Forge.jar"
curl -L --retry 2 -o "PuzzlesLib-v8.1.33-1.20.1-Forge.jar" "https://cdn.modrinth.com/data/QAGBst4M/versions/mIyVGf3d/PuzzlesLib-v8.1.33-1.20.1-Forge.jar"
