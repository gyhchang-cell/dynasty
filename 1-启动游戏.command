#!/bin/bash
# 一键启动 Dynasty 客户端（开发环境）
# 双击本文件即可：会自动使用 JDK 17 并运行 ./gradlew runClient
cd "$(dirname "$0")" || exit 1

export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  export JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home
fi
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  echo "❌ 找不到 JDK 17，请把本文件里的 JAVA_HOME 改成你自己的 JDK 17 路径"
  read -n 1 -s -r -p "按任意键退出..."
  exit 1
fi

echo "使用 JDK: $("$JAVA_HOME/bin/java" -version 2>&1 | head -1)"
echo "正在启动 Minecraft 客户端（首次可能需要 1-3 分钟）..."
./gradlew runClient
status=$?

echo
if [ $status -eq 0 ]; then
  echo "✅ 客户端已退出"
else
  echo "❌ 启动失败（退出码 $status）。把上面的报错发给作者即可定位。"
fi
read -n 1 -s -r -p "按任意键关闭窗口..."
