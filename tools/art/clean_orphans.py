import glob, json, os

ROOT = os.path.expanduser("~/Desktop/dynasty")
RES = os.path.join(ROOT, "src/main/resources")
ASSETS = os.path.join(RES, "assets/dynasty")

DEAD = ["kaishen_coin", "kaishen_block", "laote_coin", "zaomiao_coin", "qingde_coin",
        "renminbi", "renminbi_helmet", "renminbi_chestplate", "renminbi_leggings", "renminbi_boots",
        "zhaoming", "zhaoming_helmet", "zhaoming_chestplate", "zhaoming_leggings", "zhaoming_boots",
        "wula", "gali", "pujing", "pujing_block", "jingwei", "jingwei_helmet", "jingwei_chestplate",
        "jingwei_leggings", "jingwei_boots"]

removed = []
for name in DEAD:
    for sub in ("models/item", "models/block", "blockstates"):
        path = os.path.join(ASSETS, sub, name + ".json")
        if os.path.exists(path):
            os.remove(path)
            removed.append(os.path.relpath(path, RES))
print("removed models/blockstates:", len(removed))
for r in removed:
    print("   ", r)

for lang in ("zh_cn", "en_us"):
    path = os.path.join(ASSETS, "lang", lang + ".json")
    data = json.load(open(path, encoding="utf-8"))
    before = len(data)
    for key in list(data):
        short = key.split(".")[-1]
        if key.startswith("item.dynasty.") and short in DEAD:
            del data[key]
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("lang %s: %d -> %d" % (lang, before, len(data)))
