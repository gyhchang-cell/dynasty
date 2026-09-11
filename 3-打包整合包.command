#!/bin/bash
# 一键打整合包（dist/ 里生成可上传的 CF zip / mrpack / 手动包）
cd "$(dirname "$0")" || exit 1

export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  export JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home
fi

echo "1/2 构建本体 jar ..."
./gradlew build || { echo "❌ 构建失败"; read -n 1 -s -r -p "按任意键关闭"; exit 1; }

echo "2/2 生成整合包（modpack/ + dist/）..."
python3 tools/art/make_modpack.py 2>/dev/null || python3 /tmp/dyn_art/make_modpack.py 2>/dev/null || true
python3 /tmp/dyn_art/make_uploadable_packs.py 2>/dev/null || true
python3 /tmp/dyn_art/make_manual_and_guide.py 2>/dev/null || true

echo
echo "✅ 完成！可上传文件在 dist/ ："
ls -la dist 2>/dev/null || echo "（dist 为空，请联系作者）"
open dist 2>/dev/null
read -n 1 -s -r -p "按任意键关闭窗口..."
