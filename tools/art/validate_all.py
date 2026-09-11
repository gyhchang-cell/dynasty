import glob, json, os, re

ROOT = os.path.expanduser("~/Desktop/dynasty")
RES = os.path.join(ROOT, "src/main/resources")
JAVA = os.path.join(ROOT, "src/main/java")

ids = set()
for f in glob.glob(os.path.join(JAVA, "**", "*.java"), recursive=True):
    src = open(f, encoding="utf-8").read()
    for m in re.finditer(r'register\(\s*"([a-z0-9_]+)"', src):
        ids.add(m.group(1))
    for m in re.finditer(r'=\s*[a-zA-Z]+\(\s*"([a-z0-9_]+)"', src):
        ids.add(m.group(1))
    for m in re.finditer(r'=\s*[a-zA-Z]+\(\s*name\s*\+\s*"([a-z0-9_]+)"', src):
        base = re.findall(r'armor\(\s*"([a-z0-9_]+)"', src)
        for b in base:
            ids.add(b + m.group(1))
print("dynasty ids:", len(ids))

# 配方校验 / recipe validation
bad = []
for f in sorted(glob.glob(os.path.join(RES, "data/dynasty/recipes/*.json"))):
    try:
        data = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        bad.append((os.path.basename(f), "bad json: %s" % e))
        continue
    refs = set(re.findall(r"dynasty:[a-z0-9_]+", json.dumps(data)))
    missing = sorted(r.split(":")[1] for r in refs if r.split(":")[1] not in ids)
    if missing:
        bad.append((os.path.basename(f), missing))
print("recipes:", len(glob.glob(os.path.join(RES, "data/dynasty/recipes/*.json"))), "broken:", len(bad))
for n, m in bad:
    print("   ", n, m)

# 物品模型贴图校验 / item model texture validation
tex = os.path.join(RES, "assets/dynasty/textures")
missing_tex = []
for f in sorted(glob.glob(os.path.join(RES, "assets/dynasty/models/**/*.json"), recursive=True)):
    try:
        data = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        missing_tex.append((os.path.basename(f), "bad json"))
        continue
    for texref in re.findall(r'"dynasty:([a-z0-9_/]+)"', json.dumps(data)):
        if not os.path.exists(os.path.join(tex, texref + ".png")):
            missing_tex.append((os.path.relpath(f, RES), texref))
print("model texture problems:", len(missing_tex))
for n, t in missing_tex[:15]:
    print("   ", n, "->", t)

# 语言校验 / lang validation
for lang in ("zh_cn", "en_us"):
    d = json.load(open(os.path.join(RES, "assets/dynasty/lang", lang + ".json"), encoding="utf-8"))
    missing = [k for k in d if k.startswith("item.dynasty.") and k[13:] not in ids]
    print("lang", lang, len(d), "keys, stale item keys:", len(missing), missing[:8])
