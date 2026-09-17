"""补齐 7 个缺失的高阶材料（青龙鳞 / 白虎牙 / 朱雀羽 / 玄武壳 / 太乙玉 / 雷部令 / 混元珠）。

背景：第三十一轮加了 10 套甲与 10 件兵器，但兵器配方引用的这 7 个材料从未注册
（`validate_final.py` 报 "recipes: 305 broken: 7"），本脚本把它们一次补齐：
贴图 → 模型 → 配方 → 中英词条（词条合并进现有 lang 文件，重复运行安全）。

来源统一为「合成 + 图纸门控」，与现有高阶材料一致，不依赖实机掉落配置。

用法：python3 tools/art/gen_relic_materials.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp  # noqa: E402
from palette import *  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "src/main/resources")
ASSETS = os.path.join(RES, "assets/dynasty")
DATA = os.path.join(RES, "data/dynasty")
S = 32
INK = (28, 20, 16, 255)

D = "dynasty:"


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(cv, name):
    cv.outline(INK)
    cv.save(os.path.join(ASSETS, "textures/item/%s.png" % name))


# ---------------------------------------------------------------- 贴图
def shell():  # 玄武壳：龟甲六边形 + 甲片分割
    cv = Cv(S, S)
    cv.poly([(16, 4), (27, 10), (27, 22), (16, 28), (5, 22), (5, 10)], DEEPSLATE[2])
    cv.poly([(16, 6), (25, 11), (25, 21), (16, 26), (7, 21), (7, 11)], DEEPSLATE[3])
    cv.poly([(16, 8), (23, 12), (23, 20), (16, 24), (9, 20), (9, 12)], DEEPSLATE[4])
    for a, b in (((16, 8), (16, 24)), ((9, 12), (23, 20)), ((23, 12), (9, 20))):
        cv.line(a[0], a[1], b[0], b[1], darken(DEEPSLATE[1], 0.2))
    cv.ring(16, 16, 8, BRONZE[3])
    cv.px(12, 10, lighten(DEEPSLATE[0], 0.5))
    cv.px(13, 11, lighten(DEEPSLATE[0], 0.3))
    save(cv, "xuanwu_shell")


def scale():  # 青龙鳞：叠层鳞片
    cv = Cv(S, S)
    cv.poly([(16, 5), (27, 13), (24, 25), (8, 25), (5, 13)], JADE[2])
    cv.poly([(16, 8), (24, 14), (22, 23), (10, 23), (8, 14)], JADE[3])
    cv.line(8, 14, 24, 14, darken(JADE[1], 0.35))
    cv.line(10, 19, 22, 19, darken(JADE[1], 0.35))
    cv.poly([(16, 10), (20, 14), (16, 17), (12, 14)], JADE[1])
    cv.ring(16, 14, 4, DRAGON_CRYSTAL[3])
    cv.px(13, 10, JADE_LIGHT)
    cv.px(14, 11, lighten(JADE[3], 0.4))
    save(cv, "qinglong_scale")


def fang():  # 白虎牙：弯曲獠牙
    cv = Cv(S, S)
    cv.poly([(18, 4), (26, 8), (24, 18), (17, 28), (12, 26), (20, 16), (20, 9)], BONE[3])
    cv.poly([(19, 6), (24, 9), (22, 17), (16, 26), (14, 25), (21, 15), (21, 9)], BONE[4])
    cv.line(20, 10, 17, 24, lighten(BONE[0], 0.45))
    cv.line(22, 10, 19, 22, lighten(BONE[0], 0.25))
    cv.poly([(18, 4), (26, 8), (25, 11), (19, 7)], darken(BONE[1], 0.25))
    cv.px(23, 9, hx("FFFFFF"))
    save(cv, "baihu_fang")


def feather():  # 朱雀羽：羽片 + 羽轴
    cv = Cv(S, S)
    cv.poly([(16, 3), (25, 12), (23, 24), (16, 29), (9, 24), (7, 12)], CINNABAR[2])
    cv.poly([(16, 6), (22, 13), (21, 22), (16, 26), (11, 22), (10, 13)], FIRE[2])
    cv.line(16, 6, 16, 27, GOLD[3])
    for y in (10, 14, 18, 22):
        cv.line(16, y, 11, y - 3, darken(CINNABAR[1], 0.2))
        cv.line(16, y, 21, y - 3, darken(CINNABAR[1], 0.2))
    cv.px(14, 8, hx("FFE9A8"))
    cv.px(15, 9, lighten(FIRE[0], 0.35))
    save(cv, "zhuque_feather")


def taiyi():  # 太乙玉：带金饰的玉牌
    cv = Cv(S, S)
    cv.rect(6, 7, 25, 26, JADE[2])
    cv.frame(6, 7, 25, 26, GOLD[3])
    cv.rect(8, 9, 23, 24, JADE[3])
    cv.rect(11, 12, 20, 21, JADE[1])
    cv.ring(15, 16, 4, JADE_LIGHT)
    cv.disc(15, 16, 2, GOLD[4])
    cv.px(9, 10, JADE_LIGHT)
    cv.px(10, 11, lighten(JADE[3], 0.4))
    save(cv, "taiyi_jade")


def token():  # 雷部令：紫檀令牌 + 雷纹
    cv = Cv(S, S)
    cv.rect(9, 4, 22, 28, PURPLE_SILK[2])
    cv.frame(9, 4, 22, 28, GOLD[3])
    cv.rect(11, 7, 20, 25, darken(PURPLE_SILK[3], 0.15))
    cv.line(16, 10, 13, 16, hx("DCC6FF"))
    cv.line(13, 16, 17, 16, hx("DCC6FF"))
    cv.line(17, 16, 14, 22, hx("DCC6FF"))
    cv.line(14, 22, 19, 22, hx("DCC6FF"))
    cv.px(12, 9, lighten(PURPLE_SILK[0], 0.5))
    cv.px(18, 24, GOLD[4])
    save(cv, "thunder_token")


def pearl():  # 混元珠：带虹光的黑珠
    cv = Cv(S, S)
    cv.disc(16, 16, 11, darken(DRAGON_CRYSTAL[1], 0.55))
    cv.disc(16, 16, 9, darken(DRAGON_CRYSTAL[2], 0.35))
    cv.ring(16, 16, 9, mix(DRAGON_CRYSTAL[3], GOLD[3], 0.4))
    for x0, y0, x1, y1 in ((10, 18, 14, 22), (14, 22, 18, 24), (18, 24, 22, 20)):
        cv.line(x0, y0, x1, y1, mix(PORTAL_UNDERWORLD, hx("FFFFFF"), 0.35))
    cv.disc(12, 12, 3, lighten(DRAGON_CRYSTAL[0], 0.35))
    cv.px(11, 11, hx("FFFFFF"))
    cv.px(20, 21, GOLD[4])
    save(cv, "hunyuan_pearl")


# ---------------------------------------------------------------- 数据
# (id, 中文, 英文, 配方材料)
MATERIALS = [
    ("xuanwu_shell", "玄武壳", "Xuanwu Shell",
     [D + "dragon_scale", D + "dragon_scale", D + "refined_steel", D + "refined_steel", D + "blueprint"]),
    ("qinglong_scale", "青龙鳞", "Qinglong Scale",
     [D + "dragon_scale", D + "dragon_scale", D + "dragon_crystal", D + "blueprint"]),
    ("baihu_fang", "白虎牙", "White Tiger Fang",
     [D + "dragon_crystal", D + "dragon_crystal", D + "refined_steel", D + "refined_steel", D + "blueprint"]),
    ("zhuque_feather", "朱雀羽", "Vermilion Feather",
     [D + "phoenix_feather", D + "phoenix_feather", D + "cinnabar", D + "cinnabar", D + "blueprint"]),
    ("taiyi_jade", "太乙玉", "Taiyi Jade",
     [D + "xuantian_jade", D + "jade", D + "jade", D + "blueprint"]),
    ("thunder_token", "雷部令", "Thunder Token",
     [D + "talisman_paper", D + "talisman_paper", D + "cinnabar", D + "cinnabar", D + "blueprint"]),
    ("hunyuan_pearl", "混元珠", "Hunyuan Pearl",
     [D + "dragon_crystal", D + "dragon_crystal", D + "dragon_emperor_seal", D + "emperor_bone"]),
]

DRAW = {"xuanwu_shell": shell, "qinglong_scale": scale, "baihu_fang": fang,
        "zhuque_feather": feather, "taiyi_jade": taiyi, "thunder_token": token,
        "hunyuan_pearl": pearl}


def main():
    for name, zh, en, ingredients in MATERIALS:
        DRAW[name]()                                            # 1) 贴图
        write(os.path.join(ASSETS, "models/item/%s.json" % name),  # 2) 模型
              {"parent": "minecraft:item/generated",
               "textures": {"layer0": "dynasty:item/%s" % name}})
        write(os.path.join(DATA, "recipes/%s.json" % name),      # 3) 配方
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in ingredients],
               "result": {"item": D + name}})
        print("material wired:", name, zh, "| ingredients:", len(ingredients))

    # 4) 中英词条（合并进现有 lang，重复运行安全）
    zh_extra = {"item.dynasty." + n: zh for n, zh, _en, _i in MATERIALS}
    en_extra = {"item.dynasty." + n: en for n, _zh, en, _i in MATERIALS}
    for filename, extra in (("zh_cn.json", zh_extra), ("en_us.json", en_extra)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        data.update(extra)
        write(path, data)

    # 5) 顺带补两个只在英文里有的效果名（中文名缺失）
    zh_path = os.path.join(ASSETS, "lang/zh_cn.json")
    zh_data = read(zh_path)
    fixed = []
    for key, value in (("effect.dynasty.gali", "咖喱之力"), ("effect.dynasty.wula_shield", "乌拉护盾")):
        if key not in zh_data:
            zh_data[key] = value
            fixed.append(key)
    write(zh_path, zh_data)
    print("语言文件已合并；补上的中文词条:", fixed or "无")


if __name__ == "__main__":
    main()
