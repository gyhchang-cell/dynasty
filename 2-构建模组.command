#!/bin/bash
# 一键构建模组 jar（产物在 build/libs/dynasty-1.4.0.jar）
cd "$(dirname "$0")" || exit 1

export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  export JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home
fi

echo "正在构建..."
./gradlew build
status=$?

echo
if [ $status -eq 0 ]; then
  echo "✅ 构建成功，产物目录：build/libs"
  open build/libs
else
  echo "❌ 构建失败（退出码 $status），把上面的报错发给作者。"
fi
read -n 1 -s -r -p "按任意键关闭窗口..."
