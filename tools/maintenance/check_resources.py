#!/usr/bin/env python3
"""王朝资源引用自检（只读）：模型 parent / 贴图 / overrides / 方块状态 + 父链循环。

检查内容：
  1. 模型 JSON 能否解析；
  2. `parent` 指向的**本地**（dynasty 命名空间）模型是否存在；
  3. `textures` 里 `dynasty:...` 指向的贴图 PNG 是否存在；
  4. `overrides[].model` 指向的**本地**模型是否存在；
  5. `blockstates/*.json` 的 `variants` / `multipart` 引用的**本地**模型是否存在；
  6. **父模型循环引用**（A→B→A）→ 确定错误；
  7. `#贴图变量`（继承贴图）沿父链解析；解析不掉的按情况区分错误/警告。

判定规则（不误报）：
  * ERROR   —— 只在本工具能静态确定时给出：引用的是本地命名空间却找不到文件、
               `#变量` 在**本地父链走到底**仍无定义、父链成环、JSON 坏了；
  * WARNING —— 无法静态判定：父链接到 `minecraft:`/其他模组就断了、贴图来自外部命名空间、
               同一个变量在父链上被重定义为另一个 `#变量` 等；
  * 外部命名空间（minecraft / 其他模组）**一律不按本地缺失处理**。

**不检查「资源有没有被引用」**：未使用的贴图/模型是素材库存，不算问题，更不会删。
退出码：有 ERROR → 1；否则 0。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklib  # noqa: E402  （同目录，路径基于脚本位置）

NAMESPACE = "dynasty"
MODELS_PREFIX = "src/main/resources/assets/%s/models" % NAMESPACE


class ResourceIndex:
    """本地 assets/<ns>/ 资源索引（只索引真实存在的文件）。"""

    def __init__(self, assets_root, namespace=NAMESPACE):
        self.assets_root = assets_root
        self.namespace = namespace
        self.namespace_root = os.path.join(assets_root, namespace)
        self.models = {}
        self.textures = set()
        self._index()

    def _index(self):
        models_root = os.path.join(self.namespace_root, "models")
        for dirpath, _, files in os.walk(models_root):
            for name in files:
                if name.endswith(".json"):
                    rel = os.path.relpath(os.path.join(dirpath, name), models_root)
                    self.models[rel[:-5].replace(os.sep, "/")] = os.path.join(dirpath, name)
        textures_root = os.path.join(self.namespace_root, "textures")
        for dirpath, _, files in os.walk(textures_root):
            for name in files:
                if name.lower().endswith(".png"):
                    rel = os.path.relpath(os.path.join(dirpath, name), textures_root)
                    self.textures.add(rel[:-4].replace(os.sep, "/"))

    def model_path(self, ref, namespace):
        if namespace != self.namespace:
            return None                      # 外部命名空间：不归我们管
        return self.models.get(ref)

    def has_texture(self, ref, namespace):
        if namespace != self.namespace:
            return None                      # 外部命名空间：无法静态判定
        return ref in self.textures


def split_ref(value):
    """`dynasty:item/foo` → ("dynasty", "item/foo")；无冒号按 minecraft 处理。"""
    if ":" in value:
        namespace, path = value.split(":", 1)
        return namespace, path
    return "minecraft", value


def model_label(rel):
    return "%s/%s.json" % (MODELS_PREFIX, rel)


def read_model(root, index, report, ref):
    """读一个本地模型；不是本地或读不到返回 None。"""
    namespace, path = split_ref(ref)
    local = index.model_path(path, namespace)
    if not local:
        return None
    data = checklib.load_json(root, local, report, "parent")
    return data if isinstance(data, dict) else None


def check_parent_cycles(root, index, report):
    """沿 parent 走链；本地链成环 → 确定错误（原版加载该模型会失败）。"""
    for rel in sorted(index.models):
        seen = []
        current = "%s:%s" % (NAMESPACE, rel)
        while current:
            if current in seen:
                cycle = seen[seen.index(current):] + [current]
                report.error(model_label(rel), "parent", "父模型循环引用：%s" % " → ".join(cycle))
                break
            seen.append(current)
            data = read_model(root, index, report, current)
            if data is None:
                break
            parent = data.get("parent")
            if not isinstance(parent, str) or not parent or parent.startswith("#"):
                break
            namespace, _ = split_ref(parent)
            if namespace != NAMESPACE:
                break                        # 外部父模型：不追
            current = parent if ":" in parent else "%s:%s" % (NAMESPACE, parent)



def resolve_texture_variable(root, index, model_ref, variable, seen=None):
    """沿父链找 `#variable` 的定义。

    返回 (state, detail)：
      "found"     -> detail 是具体贴图引用（如 `dynasty:item/foo`）
      "external"  -> 父链走到外部命名空间就断了，无法判定（WARNING）
      "missing"   -> 本地父链走到底仍没有定义（ERROR）
      "cycle"     -> 父链成环（成环本身已由 check_parent_cycles 报错，这里不再重复）
    """
    seen = seen or set()
    if model_ref in seen:
        return "cycle", model_ref
    seen.add(model_ref)
    namespace, path = split_ref(model_ref)
    local = index.model_path(path, namespace)
    if not local:
        return "external", model_ref
    data = checklib.load_json(root, local, checklib.Report("silent"), "parent")
    if not isinstance(data, dict):
        return "external", model_ref
    textures = data.get("textures") or {}
    if variable in textures:
        value = textures[variable]
        if isinstance(value, str) and not value.startswith("#"):
            return "found", value
        if isinstance(value, str) and value.startswith("#"):
            return resolve_texture_variable(root, index, model_ref, value[1:], seen)
    parent = data.get("parent")
    if not isinstance(parent, str) or not parent or parent.startswith("#"):
        return "missing", model_ref
    return resolve_texture_variable(root, index, parent, variable, seen)


def check_textures(root, index, report, rel, data):
    for name, value in (data.get("textures") or {}).items():
        field = "textures.%s" % name
        if not isinstance(value, str):
            report.error(model_label(rel), field, "必须是字符串，这里是 %r" % (value,))
            continue
        if value.startswith("#"):
            state, detail = resolve_texture_variable(root, index, "%s:%s" % (NAMESPACE, rel), value[1:])
            if state == "missing":
                report.error(model_label(rel), field,
                             "贴图变量 %s 在本地父链上找不到定义（父链末端：%s）" % (value, detail))
            elif state == "external":
                report.warning(model_label(rel), field,
                               "贴图变量 %s 定义在外部父模型里（%s），无法静态判定" % (value, detail))
            elif state == "cycle":
                report.warning(model_label(rel), field,
                               "贴图变量 %s 因父链成环无法解析（成环本身已在上方报错）" % value)
            continue
        namespace, ref = split_ref(value)
        report.bump("贴图引用")
        if index.has_texture(ref, namespace) is False:
            report.error(model_label(rel), field,
                         "贴图不存在：%s（缺 assets/%s/textures/%s.png）" % (value, NAMESPACE, ref))
        elif namespace != NAMESPACE:
            report.bump("外部贴图引用")


def check_model(root, index, report, rel, path):
    report.files_checked += 1
    data = checklib.load_json(root, path, report, "(根)")
    if data is None:
        return
    if not isinstance(data, dict):
        report.error(model_label(rel), "(根)", "模型必须是对象，这里是 %s" % type(data).__name__)
        return

    parent = data.get("parent")
    if isinstance(parent, str) and parent and not parent.startswith("#"):
        namespace, ref = split_ref(parent)
        report.bump("parent 引用")
        if namespace == NAMESPACE and index.model_path(ref, namespace) is None:
            report.error(model_label(rel), "parent", "parent 指向的本地模型不存在：%s" % parent)

    check_textures(root, index, report, rel, data)

    overrides = data.get("overrides") or []
    if overrides and not isinstance(overrides, list):
        report.error(model_label(rel), "overrides", "必须是数组")
        overrides = []
    for i, override in enumerate(overrides):
        field = "overrides[%d]" % i
        if not isinstance(override, dict):
            report.error(model_label(rel), field, "必须是对象")
            continue
        model = override.get("model")
        if not isinstance(model, str) or not model:
            report.error(model_label(rel), field + ".model", "缺少 model 字段")
            continue
        namespace, ref = split_ref(model)
        if namespace == NAMESPACE:
            report.bump("本地 overrides 引用")
            if index.model_path(ref, namespace) is None:
                report.error(model_label(rel), field + ".model", "指向的本地模型不存在：%s" % model)
        else:
            report.bump("外部 overrides 引用")


def check_blockstates(root, index, report):
    blockstates_root = os.path.join(index.namespace_root, "blockstates")
    if not os.path.isdir(blockstates_root):
        return
    for name in sorted(os.listdir(blockstates_root)):
        if not name.endswith(".json"):
            continue
        report.files_checked += 1
        label = "src/main/resources/assets/%s/blockstates/%s" % (NAMESPACE, name)
        data = checklib.load_json(root, os.path.join(blockstates_root, name), report, "(根)")
        if data is None:
            continue
        if not isinstance(data, dict):
            report.error(label, "(根)", "blockstate 必须是对象，这里是 %s" % type(data).__name__)
            continue
        variants = data.get("variants") or {}
        if not isinstance(variants, dict):
            report.error(label, "variants", "必须是对象")
            variants = {}
        refs = []
        for variant_key, variant in variants.items():
            for entry in (variant if isinstance(variant, list) else [variant]):
                if isinstance(entry, dict) and entry.get("model"):
                    refs.append(("variants['%s'].model" % variant_key, entry["model"]))
        for i, part in enumerate(data.get("multipart") or []):
            apply = (part or {}).get("apply")
            entries = apply if isinstance(apply, list) else ([apply] if apply else [])
            for entry in entries:
                if isinstance(entry, dict) and entry.get("model"):
                    refs.append(("multipart[%d].apply.model" % i, entry["model"]))
        for field, model in refs:
            namespace, ref = split_ref(model)
            if namespace != NAMESPACE:
                report.bump("外部 blockstate 引用")
                continue
            report.bump("本地 blockstate 引用")
            if index.model_path(ref, namespace) is None:
                report.error(label, field, "引用的本地模型不存在：%s" % model)


def check(root):
    report = checklib.Report("resources", "资源引用")
    assets_root = os.path.join(root, "src/main/resources/assets")
    if not os.path.isdir(assets_root):
        report.error("src/main/resources/assets", "(目录)", "找不到资源目录：%s" % assets_root)
        return report
    index = ResourceIndex(assets_root, NAMESPACE)
    report.bump("模型", len(index.models))
    report.bump("本地贴图", len(index.textures))
    check_parent_cycles(root, index, report)
    for rel in sorted(index.models):
        check_model(root, index, report, rel, index.models[rel])
    check_blockstates(root, index, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="王朝资源引用自检（只读）")
    parser.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
                        help="仓库根目录（默认脚本上两级）")
    args = parser.parse_args(argv)
    report = check(args.root)
    print(report.summary_line())
    report.print_issues()
    if report.errors:
        print("资源自检：发现 %d 个确定错误、%d 个警告 ❌（退出码 1）"
              % (len(report.errors), len(report.warnings)))
        return 1
    print("资源自检：通过 ✅（%d 个警告属于外部命名空间，无法静态判定）" % len(report.warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
