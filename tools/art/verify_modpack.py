"""离线模拟 Forge 模组解析：检查 mandatory 依赖与「不兼容」声明。

要点（前面两次崩溃都属于这个阶段）：
  * `${file.jarVersion}` 由 Forge 运行时解析，跳过版本比较
  * JarJar 内嵌的前置（PuzzlesLib→puzzlesaccessapi、Xaero→xaerolib）算作已满足
  * `[[dependencies.X]]` 只有在 X 本身安装了才需要检查
"""
import io
import json
import os
import re
import sys
import zipfile


def parse_version(text):
    out = []
    for part in re.split(r"[.\-+]", text.strip()):
        number = re.match(r"^(\d+)", part)
        out.append(int(number.group(1)) if number else part.lower())
    return out


def cmp_key(value):
    return (1, value, "") if isinstance(value, int) else (0, 0, value)


def compare(a, b):
    left, right = parse_version(a), parse_version(b)
    for i in range(max(len(left), len(right))):
        l = left[i] if i < len(left) else 0
        r = right[i] if i < len(right) else 0
        if cmp_key(l) != cmp_key(r):
            return -1 if cmp_key(l) < cmp_key(r) else 1
    return 0


def in_range(version, rng):
    rng = rng.strip().strip('"')
    if rng in ("*", "[0,)", "[0.0,)", "[0.0.0,)"):
        return True
    m = re.match(r"^([\[\(])\s*([^,\]\)]*)\s*,\s*([^\]\)]*)\s*([\]\)])$", rng)
    if not m:
        return True
    low_bracket, low, high, high_bracket = m.groups()
    if low and compare(version, low) < 0:
        return False
    if low and compare(version, low) == 0 and low_bracket == "(":
        return False
    if high and compare(version, high) > 0:
        return False
    if high and compare(version, high) == 0 and high_bracket == ")":
        return False
    return True


def embedded_mod_ids(jar):
    """JarJar 内嵌的模组 id（Forge 视作已安装）"""
    ids = set()
    try:
        meta = json.loads(jar.read("META-INF/jarjar/metadata.json"))
    except Exception:
        return ids
    for item in meta.get("jars", []):
        path = (item.get("path") or "").lstrip("/")
        if not path.startswith("META-INF/"):
            path = "META-INF/jarjar/" + path
        try:
            inner_bytes = jar.read(path)
        except Exception:
            continue
        try:
            with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                text = inner.read("META-INF/mods.toml").decode("utf-8", "replace")
                ids.update(re.findall(r'modId\s*=\s*"([^"]+)"', text))
        except Exception:
            continue
    return ids


def load(folder):
    mods, embedded = {}, set()
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".jar"):
            continue
        with zipfile.ZipFile(os.path.join(folder, name)) as jar:
            embedded |= embedded_mod_ids(jar)
            try:
                text = jar.read("META-INF/mods.toml").decode("utf-8", "replace")
            except Exception:
                continue
        ids = re.findall(r'modId\s*=\s*"([^"]+)"', text)
        if not ids:
            continue
        version = re.search(r'version\s*=\s*"([^"]+)"', text)
        mods[ids[0]] = (version.group(1) if version else "0", name, text)
    return mods, embedded



def check(folder):
    mods, embedded = load(folder)
    print("目录: %s" % folder)
    print("  已安装 %d 个；JarJar 内嵌 %d 个：%s"
          % (len(mods), len(embedded), sorted(embedded) if embedded else "无"))
    problems = []
    for mod_id, (version, name, text) in sorted(mods.items()):
        for block in re.finditer(r"\[\[dependencies\.([^\]]+)\]\](.*?)(?=\[\[|\Z)", text, re.S):
            section = block.group(1)
            body = block.group(2)
            dep = re.search(r'modId\s*=\s*"([^"]+)"', body)
            rng = re.search(r'versionRange\s*=\s*"([^"]+)"', body)
            man = re.search(r"mandatory\s*=\s*(true|false)", body)
            if not dep or not rng or section not in mods:
                continue
            dep_id, dep_range = dep.group(1), rng.group(1)
            mandatory = (man.group(1) == "true") if man else False
            if "NOT-COMPATIBLE" in dep_range:
                if dep_id in mods:
                    problems.append("%s 明确不兼容 %s（%s 已安装）"
                                    % (section, dep_id, mods[dep_id][1]))
                continue
            if dep_id in ("minecraft", "forge", "neoforge", "fml"):
                continue
            if dep_id not in mods:
                if dep_id in embedded:
                    continue
                if mandatory:
                    problems.append("%s 必须安装 %s（缺失且未内嵌）" % (section, dep_id))
                continue
            installed = mods[dep_id][0]
            if "${" in installed:
                continue
            if mandatory and not in_range(installed, dep_range):
                problems.append("%s 需要 %s %s，但装的是 %s"
                                % (section, dep_id, dep_range, installed))
    print("  依赖/兼容性检查：%s" % ("通过 ✅" if not problems else "有问题 ❌"))
    for line in problems:
        print("   -", line)
    return not problems


if __name__ == "__main__":
    ok = True
    for target in sys.argv[1:]:
        if os.path.isdir(target):
            ok = check(target) and ok
            print()
    print("总体：%s" % ("全部通过 ✅ 模组解析不会失败" if ok else "仍有问题 ❌"))
