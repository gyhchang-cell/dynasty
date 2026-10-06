#!/bin/bash
# ============================================================================
# 一键「构建 + 导出」Dynasty：出模组 jar 与三种整合包，并同步进 HMCL 实例。
#
# 双击本文件即可（也可以在 VS Code / 终端里跑：./打包整合包.command）。
# 脚本自己会做四件事，避免之前踩过的坑：
#   ① 强制用 JDK 17（Forge 1.20.1 必须 17；你机器默认 JAVA_HOME 是 21）；
#   ② 清掉可能「挂起」的旧 Gradle 进程（挂起进程会占住项目锁 → 看起来像卡死）；
#   ③ 用 --offline 构建（避免 ForgeGradle 联网检查卡在 socket 上）；
#   ④ 跑完自动打开 ~/Desktop/导出 文件夹，失败时明确告诉你去哪找报错。
# ============================================================================
set -euo pipefail
PROJECT="$(cd "$(dirname "$0")" && pwd)"
JDK17="/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home"
LOG="/tmp/dynasty_export.log"

cd "$PROJECT" 2>/dev/null || {
  echo "❌ 找不到工程目录：$PROJECT"
  read -n 1 -s -r -p "按任意键关闭…"
  exit 1
}

echo "==================== Dynasty 一键导出 ===================="
echo "工程目录：$PROJECT"

# ① JDK 17
export JAVA_HOME="$JDK17"
if [ ! -x "$JAVA_HOME/bin/java" ]; then
  echo "⚠️ 没找到 $JDK17，尝试自动选一个 JDK 17…"
  export JAVA_HOME="$(/usr/libexec/java_home -v 17 2>/dev/null || true)"
fi
if [ -z "${JAVA_HOME:-}" ] || [ ! -x "$JAVA_HOME/bin/java" ]; then
  echo "❌ 没找到 JDK 17。装一个再跑：brew install --cask temurin@17"
  read -n 1 -s -r -p "按任意键关闭…"
  exit 1
fi
echo "Java：$("$JAVA_HOME/bin/java" -version 2>&1 | head -1)"

# ② 清理挂起的旧 Gradle（只清本项目相关的，不动别的项目）
./gradlew --stop >/dev/null 2>&1 || true
pkill -f "dynasty/gradle/wrapper" >/dev/null 2>&1 || true
sleep 1

# ③ 构建 + 导出（exportMod = 本体 jar；exportModpack = 三份整合包）
echo
echo "开始构建 + 导出（首次或清缓存后要几分钟，这个窗口会一直刷日志，别关）…"
echo "完整日志：$LOG"
echo "-----------------------------------------------------------------"
if ./gradlew exportMod exportModpack --offline --console=plain 2>&1 | tee "$LOG"; then
  echo "-----------------------------------------------------------------"
  echo "✅ 导出完成，产物如下："
  ls -lh "$HOME/Desktop/导出/Dynasty模组/" 2>/dev/null | tail -3
  ls -lh "$HOME/Desktop/导出/Dynasty整合包/" 2>/dev/null | tail -4
  echo
  echo "（这三份包可以直接上传：CF 用 dynasty-modpack-1.4.0.zip，Modrinth 用 .mrpack，"
  echo "  自己玩请导入 dynasty-1.4.0-complete.zip（含全部 FTB + 任务配置，无需补装）；manual.zip 为手动安装包）"
  open "$HOME/Desktop/导出" 2>/dev/null || true
else
  echo "-----------------------------------------------------------------"
  echo "若只是后续平台发布校验失败，已生成的完整 FTB 包仍在桌面「导出/Dynasty整合包」和工程 dist 中。"
  echo "❌ 导出失败。请把上面最后 30 行（或 $LOG）发给 AI 排查。"
  echo "   常见原因：① 网络不稳 → 去掉脚本里的 --offline 再试；② 磁盘空间不足；"
  echo "   ③ JDK 不是 17（照上面打印的 Java 版本确认）。"
  read -n 1 -s -r -p "按任意键关闭这个窗口…" || true
  exit 1
fi
echo
read -n 1 -s -r -p "按任意键关闭这个窗口…"

