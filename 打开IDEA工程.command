#!/bin/bash
# 双击 = 用 IDEA 打开本工程（工程根就是这个文件夹）
cd "$(dirname "$0")" || exit 1
PROJECT="$(pwd)"

echo "正在用 IDEA 打开：$PROJECT"
if [ -d "/Applications/IntelliJ IDEA.app" ]; then
  open -a "IntelliJ IDEA" "$PROJECT"
else
  open "$PROJECT"
fi

echo
echo "校验：IDEA 左侧项目树最顶层必须叫 dynasty（不是 Desktop）"
echo "然后等 Gradle 同步完 → 右上角选「① Dynasty 模组（开发客户端）」→ ▶"
sleep 3
