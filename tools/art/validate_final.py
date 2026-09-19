import glob, json, os, re

ROOT = os.path.expanduser("~/Desktop/dynasty")
RES = os.path.join(ROOT, "src/main/resources")
JAVA = os.path.join(ROOT, "src/main/java")
ASSETS = os.path.join(RES, "assets/dynasty")
TEXDIR = os.path.join(ASSETS, "textures")

# ---- 1) 收集 dynasty 物品 id：java 注册名 + 语言键 + 模型文件名 ----
ids = set()
for f in glob.glob(os.path.join(JAVA, "**", "*.java"), recursive=True):
    src = open(f, encoding="utf-8").read()
    for m in re.finditer(r'register\(\s*"([a-z0-9_]+)"', src):
        ids.add(m.group(1))
    for m in re.finditer(r'=\s*[a-zA-Z]+\(\s*"([a-z0-9_]+)"', src):
        ids.add(m.group(1))
for lang in ("zh_cn", "en_us"):
    data = json.load(open(os.path.join(ASSETS, "lang", lang + ".json"), encoding="utf-8"))
    for key in data:
        if key.startswith("item.dynasty.") and key.count(".") == 2:
            ids.add(key[len("item.dynasty."):])
models = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ASSETS, "models/item/*.json"))}
ids |= models
print("dynasty item ids:", len(ids))

# ---- 2) 配方校验 ----
bad = []
recipes = glob.glob(os.path.join(RES, "data/dynasty/recipes/*.json"))
for f in recipes:
    data = json.load(open(f, encoding="utf-8"))
    refs = set(re.findall(r"dynasty:[a-z0-9_]+", json.dumps(data)))
    missing = sorted(r.split(":")[1] for r in refs if r.split(":")[1] not in ids)
    if missing:
        bad.append((os.path.basename(f), missing))
print("recipes:", len(recipes), "broken:", len(bad))
for b in bad:
    print("   ", b)

# ---- 3) 图鉴校验 ----
codex = ""
for f in glob.glob(os.path.join(JAVA, "com/dynasty/DynastyCodex*.java")):
    codex += open(f, encoding="utf-8").read()
# 两种写法都要认：手写的 `new DynastyCodex.Entry("id", ...)` 和生成器产出的 `entry(l, "id", ...)`
entries = set(re.findall(r'new DynastyCodex\.Entry\("([a-z0-9_]+)"', codex))
entries |= set(re.findall(r'entry\(l, "([a-z0-9_]+)"', codex))
ingredients = set()
for m in re.finditer(r'new DynastyCodex\.Entry\("([a-z0-9_]+)".*?\)\)', codex, re.S):
    ingredients |= set(re.findall(r'"(dynasty:[a-z0-9_]+)"', m.group(0)))
for m in re.finditer(r'entry\(l, "([a-z0-9_]+)".*?\);', codex, re.S):
    ingredients |= set(re.findall(r'"(dynasty:[a-z0-9_]+)"', m.group(0)))
print("codex entries:", len(entries),
      "unknown:", sorted(e for e in entries if e not in ids),
      "bad ingredients:", sorted(i.split(":")[1] for i in ingredients if i.split(":")[1] not in ids))

# ---- 4) 模型贴图校验 ----
missing_tex = []
for f in glob.glob(os.path.join(ASSETS, "models/**/*.json"), recursive=True):
    data = json.load(open(f, encoding="utf-8"))
    for ref in re.findall(r'"dynasty:([a-z0-9_/]+)"', json.dumps(data.get("textures", {}))):
        if not os.path.exists(os.path.join(TEXDIR, ref + ".png")):
            missing_tex.append((os.path.relpath(f, RES), ref))
print("missing textures:", len(missing_tex), missing_tex[:5])

# ---- 5) 新物品清单（本次新增） ----
new = ["tang_dao", "huan_shou_dao", "chang_qiang", "yu_di", "juque_sword", "pojun_axe", "dragon_bow",
       "jade_pendant", "jade_bi_disc", "gold_seal_charm", "dragon_scale_charm", "phoenix_feather_charm",
       "qilin_horn_charm", "fox_tail_charm", "silk_pouch", "south_pointing_compass",
       "trinket_box", "dynasty_manual"]
missing_parts = [n for n in new
                 if not os.path.exists(os.path.join(TEXDIR, "item", n + ".png"))
                 or not os.path.exists(os.path.join(ASSETS, "models/item", n + ".json"))
                 or n not in ids]
print("new items fully wired:", len(new) - len(missing_parts), "/", len(new), "problems:", missing_parts)
print("curios tags:", sorted(os.path.basename(f) for f in glob.glob(os.path.join(RES, "data/curios/tags/items/*.json"))))
