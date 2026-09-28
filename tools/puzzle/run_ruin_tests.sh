#!/bin/bash
# 自然生成解谜遗迹（v2）的可重复测试。
#   1. Python：数据 / 注册 / 奖励表 / 指南针 / 文案片段契约
#   2. javac + java：生产类几何、朝向、索引对齐、九档可解性、连通性
# 不跑 Gradle（避免与另一位开发者的 runClient 抢锁）；编译与 GameTest 命令在结尾提示。
#
# 用法：bash tools/puzzle/run_ruin_tests.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT="$(pwd)"
OUT="$ROOT/build/ruin-tests"
FAIL=0

echo "== 1/2 Python 数据与注册契约 =="
if python3 tools/puzzle/test_ruin_data.py; then :; else FAIL=1; fi

echo "== 2/2 Java 几何 / 索引 / 九档可解性 =="
CP="$ROOT/build/classes/java/main"
rm -rf "$OUT"; mkdir -p "$OUT"
# 关键：把用到的生产源码一起重编进 OUT，避免用 build/classes 里的旧 class
if ! javac -nowarn -proc:none -cp "$CP" -sourcepath src/main/java -d "$OUT" \
        src/main/java/com/dynasty/puzzle/RuinLayout.java \
        src/main/java/com/dynasty/puzzle/PuzzleRules.java \
        tools/puzzle/RuinLayoutTest.java tools/puzzle/TreasuryLayoutTest.java; then
  echo "❌ 测试编译失败"; exit 1
fi
if java -cp "$OUT:$CP" RuinLayoutTest; then :; else FAIL=1; fi
if java -cp "$OUT:$CP" TreasuryLayoutTest; then :; else FAIL=1; fi

echo
if [ "$FAIL" -ne 0 ]; then
  echo "❌ 遗迹测试有失败项"
  exit 1
fi
echo "✅ 遗迹测试全部通过"
echo
echo "最终统一执行（等另一位开发者退出 runClient 之后）："
echo "  ./gradlew --offline compileJava"
echo "  ./gradlew --offline runGameTestServer     # 跑 PuzzleRuinGameTests：真实生成一遍三种遗迹"
