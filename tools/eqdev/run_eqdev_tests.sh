#!/bin/bash
# 本轮两项改造（装备悬停说明 / 叛将血条与生成）的可重复测试。
#
# 三步：
#   1. Python 结构性契约检查（血条订阅、悬停展示、文案键）
#   2. javac + java 跑生产类的纯逻辑测试（血条判定 / 生成分档 / 数值折叠）
#   3. 提示需要最终统一执行的命令（compileJava / GameTest），本脚本不擅自开构建
#
# 用法：bash tools/eqdev/run_eqdev_tests.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT="$(pwd)"
OUT="$ROOT/build/eqdev-tests"
CP_FILE="$ROOT/build/keju-qa-classpath.txt"     # Gradle 导出的编译 classpath（通用，不含客户端代码）
FAIL=0

echo "== 1/2 Python 结构性契约 =="
if python3 tools/eqdev/test_source_contracts.py; then :; else FAIL=1; fi

echo "== 2/2 Java 逻辑测试（生产类直调） =="
if [ ! -f "$CP_FILE" ]; then
  echo "   缺少 $CP_FILE（由 Gradle 导出的 classpath）"
  echo "   先执行： ./gradlew --offline -I tools/keju/keju-qa.init.gradle kejuQaClasspath"
  exit 1
fi
CP="$ROOT/build/classes/java/main:$(cat "$CP_FILE")"
rm -rf "$OUT"; mkdir -p "$OUT"
if ! javac -nowarn -proc:none -cp "$CP" -d "$OUT" tools/eqdev/EqDevLogicTest.java; then
  echo "❌ 测试编译失败（先跑一次 ./gradlew --offline compileJava 保证 build/classes 是最新的）"
  exit 1
fi
if java -cp "$OUT:$CP" EqDevLogicTest; then :; else FAIL=1; fi

echo
if [ "$FAIL" -ne 0 ]; then
  echo "❌ 本轮测试有失败项"
  exit 1
fi
echo "✅ 本轮测试全部通过"
echo
echo "最终统一执行（避免与另一位开发者同时开 Gradle）："
echo "  ./gradlew --offline compileJava"
echo "  ./gradlew --offline runGameTestServer        # 跑 RebelGeneralBossBarGameTests（需要独立测试世界）"
