#!/usr/bin/env python3
"""Rebuild only four-school resources, never textures, existing recipes, quests or saves.

The fixed content contract is docs/content/schools-v1-contract.json. Artwork is authored
separately. Vanilla pulling models intentionally provide three genuinely different bow poses.
"""
import json
from pathlib import Path
from gen_trinkets6 import CONTRACT, ITEMS

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "src/main/resources"


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def language(locale):
    zh = locale == "zh_cn"
    result = {}
    for key, item in ITEMS.items():
        result["item.dynasty." + key] = item["zh" if zh else "en"]
        result["tooltip.dynasty.school." + key] = item["zh_effect" if zh else "en_effect"]
    messages = {
        "guard_ready": ("守御反击已就绪：下一次镇岳刀满力普攻 +35%", "Counter ready: next full-strength Mountain-Ward hit +35%"),
        "combo_1": ("游龙剑舞 · 1 / 3", "Flowing-Cloud chain · 1 / 3"),
        "combo_2": ("游龙剑舞 · 2 / 3", "Flowing-Cloud chain · 2 / 3"),
        "star_marked": ("逐星标记：8秒内再次满蓄命中以引爆", "Star mark: land another fully drawn shot within 8s"),
        "edict_cast": ("敕令已出：保持站定、按住右键2秒凝神", "Edict cast: hold use and stand still for 2s"),
        "edict_ready": ("律令蓄势：4秒内下一次敕令笔满力普攻 +50%", "Edict ready: next full-strength brush hit +50% within 4s"),
    }
    for key, names in messages.items():
        result["message.dynasty.school." + key] = names[0 if zh else 1]
    passives = {
        "zhenguan_mirror": ("韧性转伤害：每点 +1.6%（最多 +200%）", "Toughness to damage: +1.6% per point (max +200%)"),
        "huben_bracer": ("守御伤害 +12%", "Guard damage +12%"),
        "liancheng_tassel": ("剑舞伤害 +16%", "Sword damage +16%"),
        "tayun_pendant": ("剑舞伤害 +12%", "Sword damage +12%"),
        "guanxing_pendant": ("弓伤害 +10%；对发光目标 +25%", "Bow damage +10%; +25% against glowing targets"),
        "mingxian_ring": ("弓伤害 +12%", "Bow damage +12%"),
        "sitian_seal": ("律令伤害 +25%", "Edict damage +25%"),
        "dingfeng_silk": ("律令伤害 +15%", "Edict damage +15%"),
    }
    for key, names in passives.items():
        result["tooltip.dynasty.school.passive." + key] = names[0 if zh else 1]
    return result


def main():
    for key, item in ITEMS.items():
        write(RES / f"data/dynasty/recipes/{key}.json", {
            "type": "minecraft:crafting_shapeless", "category": "equipment",
            "ingredients": [{"item": material} for material in item["recipe"]],
            "result": {"item": "dynasty:" + key, "count": 1},
        })
        model = {"parent": "minecraft:item/handheld" if item["kind"] == "weapon" else "minecraft:item/generated",
                 "textures": {"layer0": "dynasty:item/" + key}}
        if key == "zhuxing_bow":
            model["parent"] = "minecraft:item/bow"
            model["overrides"] = [
                {"predicate": {"dynasty:pulling": 1, **({"dynasty:pull": pull} if pull else {})},
                 "model": f"dynasty:item/zhuxing_bow_pulling_{index}"}
                for index, pull in enumerate([0, 0.65, 0.9])
            ]
            for index in range(3):
                write(RES / f"assets/dynasty/models/item/zhuxing_bow_pulling_{index}.json",
                      {"parent": f"minecraft:item/bow_pulling_{index}",
                       "textures": {"layer0": f"dynasty:item/zhuxing_bow_pulling_{index}"},
                       # Approved sprites have a LEFT-facing nocked arrow (-X).
                       # Keep this consistent with the shared six-bow regression test.
                       # Keep the inherited third-person/GUI poses and correct only drawn hands.
                       "display": {
                           "firstperson_righthand": {"rotation": [26.78, -76.87, 0],
                                                     "translation": [0.8, 3.2, 0.8], "scale": [0.62, 0.62, 0.62]},
                           "firstperson_lefthand": {"rotation": [26.78, 103.13, 0],
                                                    "translation": [0.8, 3.2, 0.8], "scale": [0.62, 0.62, 0.62]}}})
        write(RES / f"assets/dynasty/models/item/{key}.json", model)
        # Standard recipe-book unlock, not an extra reward or a progression gate.
        write(RES / f"data/dynasty/advancements/recipes/schools/{key}.json", {
            "parent": "minecraft:recipes/root",
            "criteria": {"ingredient": {"trigger": "minecraft:inventory_changed", "conditions": {
                "items": [{"items": [item["recipe"][0]]}]}}},
            "rewards": {"recipes": ["dynasty:" + key]},
        })
    for trial in CONTRACT["trials"]:
        write(RES / f"data/dynasty/advancements/{trial['id']}.json", {
            "criteria": {"performed": {"trigger": "minecraft:impossible"}},
        })
    for locale in ("zh_cn", "en_us"):
        path = RES / f"assets/dynasty/lang/{locale}.json"
        data = json.loads(path.read_text())
        for stage in range(3):
            data.pop(f"item.dynasty.zhuxing_bow_pulling_{stage}", None)
        data.update(language(locale))
        write(path, data)
    lines = ["package com.dynasty;", "", "import java.util.List;", "",
             "/** Generated by tools/art/gen_schools.py from schools-v1-contract.json. */",
             "final class DynastyCodexSchools {", "    private DynastyCodexSchools() { }",
             "    static void add(List<DynastyCodex.Entry> l) {"]
    # Include all 12 entries here first so custom mechanics win over generic attribute-only text.
    for key, item in ITEMS.items():
        def q(value):
            return json.dumps(value, ensure_ascii=False)
        ingredients = ", ".join(q(value) for value in item["recipe"])
        zh_source = "中期流派支线；工作台无序合成，配方材料见下方。不要求加入固定职业。"
        en_source = "Optional mid-game school; shapeless crafting. Freely switch builds; ingredients below."
        lines.append(f'        l.add(new DynastyCodex.Entry({q(key)}, {q(zh_source)}, {q(en_source)}, {q(item["zh_effect"])}, {q(item["en_effect"])}, {ingredients}));')
    lines += ["    }", "}", ""]
    (ROOT / "src/main/java/com/dynasty/DynastyCodexSchools.java").write_text("\n".join(lines))
    import subprocess
    subprocess.run(['node',str(ROOT/'tools/art/generate_bow_models.cjs')],check=True)
    subprocess.run(['node',str(ROOT/'tools/art/generate_handheld_edges.cjs')],check=True)
    print("Four schools regenerated; all bows use the shared model contract.")


if __name__ == "__main__":
    main()
