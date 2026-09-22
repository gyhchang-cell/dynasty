"""核对本轮「冻结」的文件确实没被改：奖励 / 存档 / 官阶 / 网络注册表 / 题库 JSON / build.gradle。

基线哈希在工具/题库开工时记录在 tools/keju/frozen_baseline.json 里，
脚本用 sha256 前 16 位比对。两类文件的处理不同：

* 严格清单（科举自己的输入，别人不该碰）：questions.json —— 有变化直接判失败；
* 其余清单（奖励 / 存档 / 官阶 / 网络注册表 / 主类 / 构建脚本）：有变化打 ⚠ 并
  `git diff --stat` 提示，因为仓库里可能有并行代理在改这些共享文件，需要人工确认。

用法：python3 tools/keju/test_frozen_files.py [--strict]
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASELINE = os.path.join(ROOT, "tools/keju/frozen_baseline.json")

STRICT = [
    "src/main/resources/data/dynasty/keju/questions.json",
]


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()[:16]


def main(argv):
    strict = "--strict" in argv
    if not os.path.exists(BASELINE):
        print("缺少基线文件：%s" % BASELINE)
        return 1
    baseline = json.load(open(BASELINE, encoding="utf-8"))
    failures = []
    warnings = []
    unchanged = 0
    for path, expected in baseline["files"].items():
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            failures.append("%s 不见了" % path)
            continue
        actual = digest(full)
        if actual == expected:
            unchanged += 1
            continue
        if path in STRICT or strict:
            failures.append("%s 被改动（基线 %s → 现在 %s）" % (path, expected, actual))
        else:
            warnings.append("%s 有变化（基线 %s → 现在 %s，可能来自并行代理）"
                            % (path, expected, actual))
    print("冻结文件核对：%d 个未变，%d 个变化，%d 个丢失" % (unchanged, len(warnings), len(failures)))
    for warning in warnings:
        print("   ⚠", warning)
    if warnings:
        subprocess.run(["git", "--no-pager", "diff", "--stat", "--"] + [w.split(" ")[0] for w in warnings])
    if failures:
        print("冻结文件自检：失败 ❌")
        for failure in failures:
            print("   -", failure)
        return 1
    print("冻结文件自检：通过 ✅（奖励 / 存档 / 官阶 / 网络注册表 / 题库均为开工时内容）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
