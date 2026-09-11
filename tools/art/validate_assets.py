import glob, json, os, re

ROOT = os.path.expanduser("~/Desktop/dynasty")
RES = os.path.join(ROOT, "src/main/resources")
JAVA = os.path.join(ROOT, "src/main/java")
ASSETS = os.path.join(RES, "assets/dynasty")
tex_dir = os.path.join(ASSETS, "textures")

ids = set()
for f in glob.glob(os.path.join(JAVA, "**", "*.java"), recursive=True):
    src = open(f, encoding="utf-8").read()
    for m in re.finditer(r'register\(\s*"([a-z0-9_]+)"', src):
        ids.add(m.group(1))
    for m in re.finditer(r'=\s*[a-zA-Z]+\(\s*"([a-z0-9_]+)"', src):
        ids.add(m.group(1))
    for m in re.finditer(r'=\s*[a-zA-Z]+\(\s*name\s*\+\s*"([a-z0-9_]+)"', src):
        for b in re.findall(r'armor\(\s*"([a-z0-9_]+)"', src):
            ids.add(b + m.group(1))
print("dynasty ids:", len(ids))

# 1) 物品模型是否齐全
item_models = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ASSETS, "models/item/*.json"))}
no_model = sorted(i for i in ids if i not in item_models)
print("\nitems without model:", len(no_model), no_model[:20])

# 2) 模型贴图引用是否存在（只看 textures 段）
missing = []
for f in glob.glob(os.path.join(ASSETS, "models/**/*.json"), recursive=True):
    data = json.load(open(f, encoding="utf-8"))
    for ref in re.findall(r'"dynasty:([a-z0-9_/]+)"', json.dumps(data.get("textures", {}))):
        if not os.path.exists(os.path.join(tex_dir, ref + ".png")):
            missing.append((os.path.relpath(f, RES), ref))
print("missing textures:", len(missing))
for m in missing[:20]:
    print("   ", m)

# 3) 方块 blockstate 是否存在
blockstates = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ASSETS, "blockstates/*.json"))}
blocks = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ASSETS, "models/block/*.json"))}
print("\nblockstates:", len(blockstates), "block models:", len(blocks))

# 4) 孤立贴图（没有任何模型引用）
used = set()
for f in glob.glob(os.path.join(ASSETS, "models/**/*.json"), recursive=True):
    data = json.load(open(f, encoding="utf-8"))
    used |= set(re.findall(r'"dynasty:([a-z0-9_/]+)"', json.dumps(data)))
orphan = []
for f in glob.glob(os.path.join(tex_dir, "**/*.png"), recursive=True):
    rel = os.path.relpath(f, tex_dir)[:-4].replace(os.sep, "/")
    if rel.startswith(("entity/", "models/", "gui/", "font/")):
        continue
    if rel not in used:
        orphan.append(rel)
print("orphan textures:", len(orphan), sorted(orphan)[:20])
