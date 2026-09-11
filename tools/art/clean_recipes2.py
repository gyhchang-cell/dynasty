import glob, json, os

ROOT = os.path.expanduser("~/Desktop/dynasty")
RES = os.path.join(ROOT, "src/main/resources")
DEAD = ["kaishen_coin", "kaishen_block", "laote_coin", "zaomiao_coin", "qingde_coin", "renminbi",
        "renminbi_leggings", "zhaoming", "zhaoming_chestplate", "wula", "gali", "pujing", "jingwei",
        "zhaoming_to_jingwei_smelting"]

removed = []
for f in sorted(glob.glob(os.path.join(RES, "data/dynasty/recipes/*.json"))):
    data = json.load(open(f, encoding="utf-8"))
    if any("dynasty:" + d in json.dumps(data) for d in DEAD):
        os.remove(f)
        removed.append(os.path.basename(f))
print("removed:", len(removed), removed)

for lang in ("zh_cn", "en_us"):
    path = os.path.join(RES, "assets/dynasty/lang", lang + ".json")
    data = json.load(open(path, encoding="utf-8"))
    for d in DEAD:
        data.pop("item.dynasty." + d, None)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("lang", lang, len(data), "keys")

print("recipes left:", len(glob.glob(os.path.join(RES, "data/dynasty/recipes/*.json"))))
