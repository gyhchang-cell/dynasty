#!/usr/bin/env python3
"""王朝语言文件自检（只读，只报告不修复）。

检查项：
  1. JSON 能否解析；
  2. **重复键**（Python 默认静默覆盖，这里用 object_pairs_hook 抓出来）；
  3. 空白译文（空串 / 只有空白）；
  4. 中英**键集合差异**（两边各自列出对方缺的键）；
  5. 占位符兼容性：`%s` / `%d` / `%1$s` / `%%`；参数**顺序允许不同**（中文常把 `%2$s` 提前），
     但个数与类型必须一致；混用带序号/不带序号 → 警告（Java Formatter 会抛异常）。

判定：ERROR = 解析失败 / 重复键 / 空白译文 / 键集合差异 / 占位符个数或类型不一致；
      WARNING = 混合占位符风格、译文不是字符串等可疑但无法确定的情况。
退出码：有 ERROR → 1；否则 0。

用法：
    python3 tools/maintenance/check_translations.py
    python3 tools/maintenance/check_translations.py --root <路径> --lang-dir <相对路径>
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklib  # noqa: E402  （同目录，路径基于脚本位置）

DEFAULT_LANG_DIR = "src/main/resources/assets/dynasty/lang"
LANGUAGES = ("zh_cn", "en_us")
PLACEHOLDER = re.compile(r"%(?:(\d+)\$)?([sdf])|%%")


def load_language(root, path, report):
    """返回 (data, duplicates)。重复键单独收集，不能被解析器悄悄覆盖。"""
    duplicates = []

    def hook(pairs):
        seen = {}
        for key, value in pairs:
            if key in seen:
                duplicates.append(key)
            seen[key] = value
        return seen

    rel = checklib.relpath(root, path)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle, object_pairs_hook=hook)
    except json.JSONDecodeError as exc:
        report.error(rel, "(根)", "JSON 解析失败：%s" % exc)
        return None, duplicates
    except OSError as exc:
        report.error(rel, "(根)", "读不到文件：%s" % exc)
        return None, duplicates
    if not isinstance(data, dict):
        report.error(rel, "(根)", "顶层必须是对象（key → 译文），这里是 %s" % type(data).__name__)
        return None, duplicates
    return data, duplicates


def placeholders_of(text):
    """把占位符规范成 (position, kind) 列表；`%%` 是转义百分号，跳过。"""
    specs = []
    sequential = 0
    indexed = plain = False
    for match in PLACEHOLDER.finditer(text):
        if match.group(0) == "%%":
            continue
        kind = match.group(2)
        if match.group(1):
            indexed = True
            specs.append((int(match.group(1)), kind))
        else:
            plain = True
            sequential += 1
            specs.append((sequential, kind))
    return specs, (indexed and plain)


def compare_placeholders(path, key, zh_text, en_text, report):
    zh_specs, zh_mixed = placeholders_of(zh_text)
    en_specs, en_mixed = placeholders_of(en_text)
    if zh_mixed:
        report.warning(path, "zh_cn/%s" % key, "混用了带序号与不带序号的占位符（Java Formatter 会报错）")
    if en_mixed:
        report.warning(path, "en_us/%s" % key, "混用了带序号与不带序号的占位符（Java Formatter 会报错）")
    if not zh_specs and not en_specs:
        return False
    report.bump("带占位符的键")
    if sorted(zh_specs) != sorted(en_specs):
        report.error(path, "zh_cn+en_us/%s" % key,
                     "占位符不兼容：zh=%s / en=%s（个数或类型不一致）" % (zh_specs, en_specs))
    return True



def check(root, lang_dir=DEFAULT_LANG_DIR):
    report = checklib.Report("translations", "语言")
    base = os.path.join(root, lang_dir)
    if not os.path.isdir(base):
        report.error(lang_dir, "(目录)", "找不到语言目录：%s" % base)
        return report
    data = {}
    for language in LANGUAGES:
        path = os.path.join(base, language + ".json")
        if not os.path.isfile(path):
            report.error("%s/%s.json" % (lang_dir, language), "(文件)", "语言文件不存在")
            continue
        report.files_checked += 1
        loaded, duplicates = load_language(root, path, report)
        if loaded is None:
            continue
        data[language] = loaded
        report.bump("%s 键" % language, len(loaded))
        for key in sorted(set(duplicates)):
            report.error("%s/%s.json" % (lang_dir, language), key,
                         "重复键：解析器会静默覆盖，玩家可能看到错的那条")

    for language, entries in data.items():
        path = "%s/%s.json" % (lang_dir, language)
        for key, value in entries.items():
            if not isinstance(value, str):
                report.error(path, key, "译文必须是字符串，这里是 %s（%r）" % (type(value).__name__, value))
            elif not value.strip():
                report.error(path, key, "空白译文（玩家会看到空名字）")

    if len(data) == len(LANGUAGES):
        zh, en = data["zh_cn"], data["en_us"]
        zh_path = "%s/zh_cn.json" % lang_dir
        en_path = "%s/en_us.json" % lang_dir
        for key in sorted(set(zh) - set(en)):
            report.error(en_path, key, "缺少键（zh 有：%s）" % zh[key])
        for key in sorted(set(en) - set(zh)):
            report.error(zh_path, key, "缺少键（en 有：%s）" % en[key])
        for key in sorted(set(zh) & set(en)):
            if isinstance(zh[key], str) and isinstance(en[key], str):
                compare_placeholders("%s + %s" % (zh_path, en_path), key, zh[key], en[key], report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="王朝语言文件自检（只读，只报告）")
    parser.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
                        help="仓库根目录（默认脚本上两级）")
    parser.add_argument("--lang-dir", default=DEFAULT_LANG_DIR, help="语言目录（相对仓库根）")
    args = parser.parse_args(argv)
    report = check(args.root, args.lang_dir)
    print(report.summary_line())
    report.print_issues()
    if report.errors:
        print("语言自检：发现 %d 个错误、%d 个警告 ❌（退出码 1）"
              % (len(report.errors), len(report.warnings)))
        return 1
    print("语言自检：通过 ✅（无重复键、无空译文、中英键集合一致、占位符兼容）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
