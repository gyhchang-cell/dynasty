#!/usr/bin/env python3
"""王朝基础质量检查：统一入口（只读）。

一次跑三个检查脚本，输出简短汇总 + 每条问题的「文件路径 / 字段 / 原因」：

    python3 tools/maintenance/check_all.py
    python3 tools/maintenance/check_all.py --only resources,recipes
    python3 tools/maintenance/check_all.py --json /tmp/dynasty-check.json   # 可选报告
    python3 tools/maintenance/check_all.py --root /别的/仓库

规则：
  * **默认不在项目里生成任何文件**；只有显式传 `--json <路径>` 才写报告（路径由调用者决定）；
  * 任一**确定错误** → 退出码 1；只有警告/跳过 → 0；
  * 路径基于脚本所在位置解析（不依赖当前工作目录），只用 Python 标准库。
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                     # 让子脚本能 import checklib
DEFAULT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

CHECKS = (
    ("resources", "check_resources.py", "check", "资源引用"),
    ("translations", "check_translations.py", "check", "语言文件"),
    ("recipes", "check_recipes.py", "scan", "配方"),
)


def load_checker(filename):
    """按文件路径加载同目录的检查脚本（不依赖 sys.path 顺序）。"""
    spec = importlib.util.spec_from_file_location(filename[:-3], os.path.join(HERE, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checks(root, only=None):
    reports = []
    for name, filename, entry, title in CHECKS:
        if only and name not in only:
            continue
        if not os.path.isfile(os.path.join(HERE, filename)):
            from checklib import Report
            report = Report(name, title)
            report.error(filename, "(脚本)", "找不到检查脚本：%s" % os.path.join(HERE, filename))
            reports.append(report)
            continue
        module = load_checker(filename)
        reports.append(getattr(module, entry)(root))
    return reports


def print_reports(reports, stream=print):
    total = {"files": 0, "errors": 0, "warnings": 0, "skipped": 0}
    for report in reports:
        stream(report.summary_line())
        report.print_issues(stream)
        total["files"] += report.files_checked
        total["errors"] += len(report.errors)
        total["warnings"] += len(report.warnings)
        total["skipped"] += len(report.skips)
    stream("")
    stream("=== 汇总 ===")
    stream("检查文件 %d 个 · 确认错误 %d · 警告 %d · 跳过 %d"
           % (total["files"], total["errors"], total["warnings"], total["skipped"]))
    return total


def build_json_report(root, reports, total):
    return {
        "tool": "tools/maintenance/check_all.py",
        "root": root,
        "checks": [r.as_dict() for r in reports],
        "totals": total,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="王朝基础质量检查（只读，统一入口）")
    parser.add_argument("--root", default=DEFAULT_ROOT,
                        help="仓库根目录（默认脚本上两级，与当前工作目录无关）")
    parser.add_argument("--only", default="",
                        help="只跑指定检查，逗号分隔：resources,translations,recipes")
    parser.add_argument("--json", default="",
                        help="可选：把结果写成 JSON 报告到指定路径（默认不写任何文件）")
    args = parser.parse_args(argv)
    only = {name.strip() for name in args.only.split(",") if name.strip()} or None

    reports = run_checks(args.root, only)
    total = print_reports(reports)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(build_json_report(args.root, reports, total), handle,
                      ensure_ascii=False, indent=2)
        print("已写出 JSON 报告：%s" % args.json)
    return 1 if total["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
