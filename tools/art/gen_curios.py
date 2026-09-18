"""Curios 分类的唯一来源；不生成贴图，不改第三方饰品。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/main/resources/data"
SLOT_NAMES = {
    "head": "头部", "necklace": "项链", "ring": "戒指", "bracelet": "手镯",
    "hands": "手部", "body": "身体", "back": "背部", "belt": "腰带", "charm": "护符",
}
# 未列出的玉器、符印、法器统一归护符；每件饰品只有一个分类槽。
GROUPS = {
    "head": "jade_crown phoenix_feather_charm sun_feather phoenix_hairpin gilded_lotus_crown iron_helmet_plume deer_antler hawk_eye",
    "necklace": "jade_pendant jade_bi_disc dragon_scale_charm qilin_horn_charm moon_pendant jade_marrow_charm alchemy_pendant fox_spirit_pendant imperial_pearl_earring",
    "ring": "phoenix_ring dragon_bone_ring jade_ring",
    "bracelet": "wrist_guard zen_bead_string guqin_string bow_string",
    "hands": "bear_paw tiger_claw folding_fan jade_ruyi drum_beater",
    "body": "heart_mirror scale_plate iron_pauldron knee_guard cloud_brocade mandarin_rank_badge merit_badge scholar_ink_badge dragon_king_scale",
    "back": "arrow_quiver turtle_shell crane_feather sky_feather immortal_crane_feather phoenix_wing_charm war_banner_charm scroll_case_charm",
    "belt": "silk_pouch cinnabar_pouch iron_waist_token jade_belt_hook belt_buckle dragon_robe_sash dragon_scale_sash wine_gourd incense_sachet mirror_pouch talisman_pouch fox_tail_charm leopard_tail horse_stirrup war_horse_bell saber_tassel sword_tassel pike_tassel dragon_whisker",
}


def accessories():
    text = (ROOT / "src/main/java/com/dynasty/DynastyTrinkets.java").read_text()
    return set(re.findall(r'charm\("([a-z_]+)"\)', text)) | set(
        re.findall(r'\{"([a-z_]+)", -?\d+, ', text)) | {"bronze_mirror"}


def classifications():
    result = {item: "charm" for item in accessories()}
    seen = set()
    for slot, words in GROUPS.items():
        for item in words.split():
            assert item in result, "未注册饰品：" + item
            assert item not in seen, "重复分类：" + item
            seen.add(item)
            result[item] = slot
    return result


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def build():
    mapping = classifications()
    for slot in [*SLOT_NAMES, "curio"]:
        path = DATA / f"curios/tags/items/{slot}.json"
        previous = json.loads(path.read_text()) if path.exists() else {}
        # curios:curio 是所有槽通用的物品标签，不能把王朝饰品加入这里。
        foreign = [v for v in previous.get("values", [])
                   if not (isinstance(v, str) and v.startswith("dynasty:"))]
        values = foreign + ["dynasty:" + item for item in sorted(mapping) if mapping[item] == slot]
        write(path, {"replace": False, "values": values})
        slot_data = {"size": 2 if slot == "ring" else 1, "operation": "SET"}
        if slot == "curio":
            slot_data.update({"order": 200, "validators": ["dynasty:accessory"]})
        write(DATA / f"dynasty/curios/slots/{slot}.json", slot_data)
    write(DATA / "dynasty/tags/items/accessories.json",
          {"replace": False, "values": ["dynasty:" + item for item in sorted(mapping)]})
    write(DATA / "dynasty/curios/entities/player.json",
          {"replace": False, "entities": ["minecraft:player"], "slots": [*SLOT_NAMES, "curio"]})
    print(f"Curios：{len(mapping)} 件饰品，9 类标准槽 + 1 个任务成长万能槽")


if __name__ == "__main__":
    build()
