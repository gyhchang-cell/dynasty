import json, os, shutil, glob

ART = "/tmp/dyn_art/out/item"
REPO = os.path.expanduser("~/Desktop/dynasty/src/main/resources")
ASSETS = os.path.join(REPO, "assets/dynasty")
DATA = os.path.join(REPO, "data/dynasty")
TEX = os.path.join(ASSETS, "textures/item")
MODELS = os.path.join(ASSETS, "models/item")
LANGS = os.path.join(ASSETS, "lang")
RECIPES = os.path.join(DATA, "recipes")
os.makedirs(RECIPES, exist_ok=True)

NEW = {
    "zongzi": ("粽子", "Zongzi"),
    "tangyuan": ("汤圆", "Tangyuan"),
    "niangao": ("年糕", "Rice Cake"),
    "osmanthus_cake": ("桂花糕", "Osmanthus Cake"),
    "cured_meat": ("腊肉", "Cured Meat"),
    "roast_duck": ("烤鸭", "Roast Duck"),
    "longevity_noodles": ("长寿面", "Longevity Noodles"),
    "baijiu": ("白酒", "Baijiu"),
    "raw_silk": ("生丝", "Raw Silk"),
    "silk": ("丝绸", "Silk"),
    "brocade": ("锦缎", "Brocade"),
    "bamboo_slip": ("竹简", "Bamboo Slip"),
    "ink_stick": ("徽墨", "Ink Stick"),
    "ink_brush": ("毛笔", "Ink Brush"),
    "bronze_mirror": ("铜镜", "Bronze Mirror"),
    "roof_tile": ("琉璃瓦", "Glazed Roof Tile"),
    "wind_talisman": ("御风符", "Wind Talisman"),
    "stealth_talisman": ("隐身符", "Stealth Talisman"),
    "healing_talisman": ("回春符", "Healing Talisman"),
    "fire_talisman": ("火符", "Fire Talisman"),
    "thunder_talisman": ("雷符", "Thunder Talisman"),
    "return_talisman": ("归乡符", "Return Talisman"),
    "quest_ledger": ("王朝手札", "Quest Ledger"),
    "festival_lantern": ("节令灯", "Festival Lantern"),
}

# 1) 贴图 / textures
installed = 0
for name in NEW:
    src = os.path.join(ART, name + ".png")
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(TEX, name + ".png"))
        installed += 1

# 2) 模型 / models
for name in NEW:
    with open(os.path.join(MODELS, name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"parent": "item/generated", "textures": {"layer0": "dynasty:item/" + name}},
                  f, ensure_ascii=False, indent=2)

# 3) 语言 / lang
for lang, idx in (("zh_cn", 0), ("en_us", 1)):
    path = os.path.join(LANGS, lang + ".json")
    data = json.load(open(path, encoding="utf-8"))
    for name, names in NEW.items():
        data["item.dynasty." + name] = names[idx]
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("installed textures:", installed)
print("models+lang done for", len(NEW), "items")
