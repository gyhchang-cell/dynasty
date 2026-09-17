"""第三十二轮：+6 把帝兵（麒麟战斧 / 太乙法剑 / 白虎戟 / 雷霆枪 / 紫微刀 / 朱雀弓）。

做法与 `gen_weapons.py` 一致：**复用现成贴图**（每把换个来源，视觉上区分得开），
生成 模型 / 配方 / 中英词条，并把 Java 注册行打印出来（粘进 `DynastyWeapons`）。

数值：全部走 `DynastyTiers.DRAGON_CRYSTAL`（基础攻击 141，与天子剑同一套算法），
总攻击写在注释里；特攻另写进 `DynastyBalance.WEAPON_BONUS`（命中时补固定伤害）。

用法：python3 tools/art/gen_weapons4.py
"""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
D = "dynasty:"

# id: (中文, 英文, 贴图来源, 总攻击, 特攻, [材料], Java 注册代码片段)
WEAPONS = {
    "qilin_war_axe": ("麒麟战斧", "Qilin War Axe", "pojun_axe", 2000, 250,
                      [D + "qilin_horn", D + "refined_steel", D + "refined_steel", D + "blueprint"],
                      'new AxeItem(DynastyTiers.DRAGON_CRYSTAL, 1859, -2.9F, new Item.Properties())'),
    "taiyi_sword": ("太乙法剑", "Taiyi Sword", "juque_sword", 2300, 300,
                    [D + "taiyi_jade", D + "dragon_crystal", D + "blueprint"],
                    'sword("taiyi_sword", DynastyTiers.DRAGON_CRYSTAL, 2159, -2.2F)'),
    "baihu_glaive": ("白虎戟", "White Tiger Glaive", "halberd_fangtian", 2600, 330,
                     [D + "baihu_fang", D + "refined_steel", D + "refined_steel", D + "blueprint"],
                     'new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 2459, -2.8F, new Item.Properties())'),
    "thunder_spear": ("雷霆枪", "Thunder Spear", "chang_qiang", 2900, 360,
                      [D + "thunder_token", D + "refined_steel", D + "refined_steel", D + "blueprint"],
                      'new PolearmItem(DynastyTiers.DRAGON_CRYSTAL, 2759, -2.6F, new Item.Properties())'),
    "ziwei_saber": ("紫微刀", "Ziwei Saber", "seven_star_saber", 3200, 400,
                    [D + "dragon_crystal", D + "xuantian_jade", D + "blueprint"],
                    'sword("ziwei_saber", DynastyTiers.DRAGON_CRYSTAL, 3059, -2.4F)'),
    "zhuque_bow": ("朱雀弓", "Vermilion Bow", "dragon_bow", 0, 300,
                   [D + "zhuque_feather", D + "phoenix_feather", D + "dragon_bow", D + "blueprint"],
                   'new DragonBowItem(4.0D, 300.0D, 2, 4, new Item.Properties().durability(9000))'),
}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    for wid, (zh, en, source, total, bonus, ingredients, code) in WEAPONS.items():
        src = os.path.join(ASSETS, "textures/item/%s.png" % source)
        dst = os.path.join(ASSETS, "textures/item/%s.png" % wid)
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)
        write(os.path.join(ASSETS, "models/item/%s.json" % wid),
              {"parent": "minecraft:item/handheld",
               "textures": {"layer0": "dynasty:item/%s" % wid}})
        write(os.path.join(DATA, "recipes/%s.json" % wid),
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in ingredients],
               "result": {"item": D + wid}})
        print("weapon wired:", wid, zh, "总攻击", total, "特攻", bonus)

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        for wid, values in WEAPONS.items():
            data["item.dynasty.%s" % wid] = values[0] if index == 0 else values[1]
        write(path, data)

    print("\n--- DynastyWeapons 追加行（Java）---")
    for wid, (zh, en, source, total, bonus, ingredients, code) in WEAPONS.items():
        print("    /** %s / %s：%s（特攻 +%d） */" % (zh, en, "弓：箭矢 ×4.0 + 300" if total == 0 else "总攻击 %d" % total, bonus))
        print('    public static final RegistryObject<Item> %s =\n            %s;' % (wid.upper(), code))

    print("\n--- DynastyBalance.WEAPON_BONUS 追加行 ---")
    for wid, values in WEAPONS.items():
        print('        WEAPON_BONUS.put("%s", %sD);' % (wid, float(values[4])))

    print("\n兵器扩充完成：%d 把 ✅" % len(WEAPONS))


if __name__ == "__main__":
    main()
