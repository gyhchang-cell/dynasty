#!/usr/bin/env python3
"""tools/maintenance 共用的报告对象与 JSON 读取小工具（只读，标准库）。

设计目标：三个检查脚本（资源 / 语言 / 配方）共用同一套「问题」结构，方便统一入口汇总：

    Issue(severity, path, field, message)
      * severity: "error"   —— 可静态确定的错误（原版会加载失败 / 玩家必然看到坏结果）
                  "warning" —— 可疑或无法静态确定（不计入退出码）
                  "skip"    —— 明确不适用本工具的规则（写明原因，不算问题）
      * path:   相对仓库根的文件路径（可定位），例如 `src/main/resources/data/dynasty/recipes/x.json`
      * field:  出问题的字段/位置，例如 `textures.layer0`、`pattern[1]`、`recipes[0].recipe`
      * message: 人话原因

约定：路径一律用 `/` 分隔，便于跨平台比对与写进 JSON 报告。
"""
import json
import os

ERROR = "error"
WARNING = "warning"
SKIP = "skip"


class Issue:
    __slots__ = ("severity", "path", "field", "message")

    def __init__(self, severity, path, field, message):
        self.severity = severity
        self.path = path.replace(os.sep, "/")
        self.field = field or ""
        self.message = message

    def as_dict(self):
        return {"severity": self.severity, "path": self.path,
                "field": self.field, "message": self.message}

    def __str__(self):
        mark = {ERROR: "❌", WARNING: "⚠", SKIP: "⏭"}.get(self.severity, "?")
        field = (" [%s]" % self.field) if self.field else ""
        return "%s %s%s: %s" % (mark, self.path, field, self.message)


class Report:
    """一个检查脚本的结果集合。"""

    def __init__(self, name, title=""):
        self.name = name
        self.title = title or name
        self.issues = []
        self.files_checked = 0
        self.details = {}          # 细节计数：{"模型": 485, "方块状态": 21}

    # ---- 记录 -------------------------------------------------------------
    def add(self, severity, path, field, message):
        self.issues.append(Issue(severity, path, field, message))

    def error(self, path, field, message):
        self.add(ERROR, path, field, message)

    def warning(self, path, field, message):
        self.add(WARNING, path, field, message)

    def skip(self, path, field, message):
        self.add(SKIP, path, field, message)

    def bump(self, key, amount=1):
        self.details[key] = self.details.get(key, 0) + amount

    def merge(self, other):
        """把另一个 Report 并进来（统一入口用）。"""
        self.issues.extend(other.issues)
        self.files_checked += other.files_checked
        for key, value in other.details.items():
            self.bump(key, value)
        return self

    # ---- 查询 -------------------------------------------------------------
    @property
    def errors(self):
        return [i for i in self.issues if i.severity == ERROR]

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == WARNING]

    @property
    def skips(self):
        return [i for i in self.issues if i.severity == SKIP]

    def summary_line(self):
        detail = ""
        if self.details:
            detail = "（%s）" % "、".join("%s %d" % (k, v) for k, v in self.details.items())
        return "[%s] 文件 %d%s · 错误 %d · 警告 %d · 跳过 %d" % (
            self.title, self.files_checked, detail,
            len(self.errors), len(self.warnings), len(self.skips))

    def print_issues(self, stream_print=print):
        """逐条打印（错误 → 警告 → 跳过），每条都带路径 / 字段 / 原因。"""
        for issue in self.errors + self.warnings + self.skips:
            stream_print("   " + str(issue))

    def as_dict(self):
        return {
            "name": self.name,
            "files_checked": self.files_checked,
            "details": self.details,
            "counts": {"errors": len(self.errors), "warnings": len(self.warnings),
                       "skipped": len(self.skips)},
            "errors": [i.as_dict() for i in self.errors],
            "warnings": [i.as_dict() for i in self.warnings],
            "skipped": [i.as_dict() for i in self.skips],
        }


def relpath(root, path):
    """相对仓库根的路径（统一 / 分隔）。"""
    return os.path.relpath(path, root).replace(os.sep, "/")


def load_json(root, path, report, field="(根)"):
    """读 JSON；解析失败 / 读不到 → 记 error 并返回 None。"""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        report.error(relpath(root, path), field, "JSON 解析失败：%s" % exc)
    except OSError as exc:
        report.error(relpath(root, path), field, "读不到文件：%s" % exc)
    return None


def iter_json_files(base_dir):
    """递归列出目录下的 .json（排序，保证输出稳定）。"""
    found = []
    for dirpath, dirnames, filenames in os.walk(base_dir):
        dirnames.sort()
        for name in sorted(filenames):
            if name.endswith(".json"):
                found.append(os.path.join(dirpath, name))
    return found
