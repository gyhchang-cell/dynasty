import json, os

RECIPES = os.path.expanduser("~/Desktop/dynasty/src/main/resources/data/dynasty/recipes")
os.makedirs(RECIPES, exist_ok=True)


def shapeless(name, ingredients, result, count=1):
    data = {
        "type": "minecraft:crafting_shapeless",
        "ingredients": [{"item": i} for i in ingredients],
        "result": {"item": result, "count": count},
    }
    with open(os.path.join(RECIPES, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


D = "dynasty:"
M = "minecraft:"

recipes = {
    "zongzi": ([M + "wheat", M + "wheat", D + "bamboo_slip"], D + "zongzi", 2),
    "tangyuan": ([M + "wheat", M + "wheat", M + "sugar"], D + "tangyuan", 2),
    "niangao": ([M + "wheat", M + "wheat", M + "wheat", M + "sugar"], D + "niangao", 1),
    "osmanthus_cake": ([M + "wheat", M + "wheat", M + "oxeye_daisy", M + "sugar"], D + "osmanthus_cake", 1),
    "cured_meat": ([M + "cooked_porkchop", M + "wheat", M + "coal"], D + "cured_meat", 1),
    "roast_duck": ([M + "cooked_chicken", M + "cooked_chicken", M + "coal"], D + "roast_duck", 1),
    "longevity_noodles": ([M + "wheat", M + "wheat", M + "wheat", M + "egg"], D + "longevity_noodles", 1),
    "baijiu": ([D + "wine", M + "glass_bottle"], D + "baijiu", 1),
    "raw_silk": ([M + "string", M + "string", M + "string"], D + "raw_silk", 1),
    "silk": ([D + "raw_silk", D + "raw_silk", D + "raw_silk"], D + "silk", 1),
    "brocade": ([D + "silk", D + "silk", M + "gold_ingot"], D + "brocade", 1),
    "bamboo_slip": ([M + "bamboo", M + "bamboo", M + "string"], D + "bamboo_slip", 2),
    "ink_stick": ([M + "coal", M + "coal", D + "cinnabar"], D + "ink_stick", 1),
    "ink_brush": ([M + "stick", D + "silk"], D + "ink_brush", 1),
    "bronze_mirror": ([D + "bronze_ingot", D + "bronze_ingot", D + "bronze_ingot", M + "glass"],
                      D + "bronze_mirror", 1),
    "roof_tile": ([M + "clay_ball", M + "clay_ball", M + "coal"], D + "roof_tile", 2),
    "wind_talisman": ([D + "talisman_paper", M + "feather"], D + "wind_talisman", 1),
    "stealth_talisman": ([D + "talisman_paper", M + "coal", D + "ink_stick"], D + "stealth_talisman", 1),
    "healing_talisman": ([D + "talisman_paper", D + "cinnabar", M + "wheat"], D + "healing_talisman", 1),
    "fire_talisman": ([D + "talisman_paper", M + "coal", M + "coal"], D + "fire_talisman", 1),
    "thunder_talisman": ([D + "talisman_paper", M + "gunpowder"], D + "thunder_talisman", 1),
    "return_talisman": ([D + "talisman_paper", M + "ender_pearl"], D + "return_talisman", 1),
    "quest_ledger": ([M + "book", D + "silk", D + "bamboo_slip"], D + "quest_ledger", 1),
    "festival_lantern": ([M + "paper", M + "paper", M + "paper", M + "paper",
                          D + "gold_coin", M + "torch"], D + "festival_lantern", 1),
    "dynasty_guide_craft": ([M + "book", D + "silk"], D + "dynasty_guide", 1),
}

for name, (ing, res, count) in recipes.items():
    shapeless(name, ing, res, count)

print("recipes written:", len(recipes))
print("total recipes now:", len(os.listdir(RECIPES)))
