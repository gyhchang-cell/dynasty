#!/bin/bash
# 科举（界面 / 会话 / 题库校验 / 网络契约）的本地可重复测试。
#
# 做四件事（全程离线、不打包、不动整合包与启动器）：
#   1. ./gradlew --offline compileJava        先保证源码能编译
#   2. 用 Gradle 导出的完整 classpath 编译并运行 tools/keju/KejuQaTests.java
#   3. python3 tools/keju/test_verify_keju.py 用临时输入压 tools/art/verify_keju.py
#   4. python3 tools/keju/test_frozen_files.py 核对冻结文件（奖励 / 存档 / 协议）没被改
#
# 用法：bash tools/keju/run_keju_tests.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
ROOT="$(pwd)"
CP_FILE="$ROOT/build/keju-qa-classpath.txt"
OUT="$ROOT/build/keju-qa-tests"
FAIL=0

echo "== 1/4 编译源码 =="
./gradlew --offline compileJava --console=plain -q || { echo "❌ compileJava 失败"; exit 1; }

echo "== 2/4 Java 测试（生产类直调） =="
if [ ! -f "$CP_FILE" ]; then
  echo "   导出 Gradle classpath ..."
  ./gradlew --offline -I tools/keju/keju-qa.init.gradle kejuQaClasspath --console=plain -q || exit 1
fi
CP="$ROOT/build/classes/java/main:$(cat "$CP_FILE")"
rm -rf "$OUT"; mkdir -p "$OUT"
if ! javac -nowarn -proc:none -cp "$CP" -d "$OUT" tools/keju/KejuQaTests.java; then
  echo "❌ 测试编译失败"; exit 1
fi
if java -cp "$OUT:$CP" KejuQaTests; then :; else FAIL=1; fi

echo "== 3/4 Python：正式校验器 + 临时坏题库 =="
if python3 tools/keju/test_verify_keju.py; then :; else FAIL=1; fi

echo "== 4/4 冻结文件核对（奖励 / 存档 / 线协议输入） =="
if python3 tools/keju/test_frozen_files.py; then :; else FAIL=1; fi

echo
if [ "$FAIL" -ne 0 ]; then
  echo "❌ 科举测试有失败项"
  exit 1
fi
echo "✅ 科举测试全部通过"
