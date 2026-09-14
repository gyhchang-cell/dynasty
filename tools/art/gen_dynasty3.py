"""王朝新增内容贴图生成器（2024 平衡重制版）。

生成：
  1) 新武器/工具：木矛、石戈、铜刀、铁剑、猎弓、长弓、玄天钺、天子剑
  2) 新护甲物品：布衣套、玄天真龙套
  3) 新材料与信物：图纸、精钢、叛将首级、内廷令牌、帝骸骨、龙帝玉玺、玄天玉
  4) 新饰品：护心镜、玉冠
  5) 护甲层贴图：cloth / xuantian（64x32 原版人形布局）
  6) 饰品槽图标：slot/empty_trinket_slot.png

运行：python3 tools/art/gen_dynasty3.py
"""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *  # noqa: F401,F403

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ITEM_OUT = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/item")
SLOT_OUT = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/slot")
BLOCK_OUT = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/block")
ARMOR_OUT = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/models/armor")
for d in (ITEM_OUT, SLOT_OUT, BLOCK_OUT, ARMOR_OUT):
    os.makedirs(d, exist_ok=True)

S = 32
INK = (26, 18, 12, 255)
HANDLE = ramp(hx("6B4423"), 5)
STONE = ramp(hx("9A9A98"), 5)
COPPER = ramp(hx("C87A4A"), 5)
IRON_M = ramp(hx("D8D8D8"), 5)
CLOTH_M = ramp(hx("C9BFa0".upper()), 5)
CLOTH2 = ramp(hx("8A6F4A"), 5)
XUAN_MAIN = ramp(hx("3B4A6B"), 5)
XUAN_TRIM = ramp(hx("E8C86A"), 5)


def save(cv, name, folder=ITEM_OUT):
    cv.outline(INK)
    cv.save(os.path.join(folder, name + ".png"))
    print("  item:", name)


# ------------------------------------------------------------------ 基础形状
def spear(name, head, shaft=HANDLE, length=26):
    """长柄：木矛 / 石戈 / 长枪通用"""
    cv = Cv(S, S)
    cv.line(9, 29, 9 + length, 29 - length, shaft[2])
    cv.line(10, 29, 10 + length, 29 - length, shaft[1])
    cv.line(10, 28, 10 + length, 28 - length, lighten(shaft[0], 0.2))
    tipx, tipy = 9 + length, 29 - length
    cv.poly([(tipx - 1, tipy + 1), (tipx + 5, tipy - 4), (tipx + 7, tipy - 1),
             (tipx + 3, tipy + 3)], head[2])
    cv.poly([(tipx, tipy + 1), (tipx + 5, tipy - 3), (tipx + 6, tipy - 1),
             (tipx + 2, tipy + 2)], head[1])
    cv.px(tipx + 5, tipy - 4, lighten(head[0], 0.5))
    cv.px(tipx + 1, tipy, head[0])
    save(cv, name)


def dao(name, blade, guard, curve=3):
    """单刃刀（铜刀/唐刀/环首刀）"""
    cv = Cv(S, S)
    cv.line(8, 27, 14, 21, HANDLE[2])
    cv.line(9, 27, 15, 21, HANDLE[1])
    cv.disc(7, 27, 3, guard[1])
    cv.disc(7, 27, 2, guard[0])
    cv.px(6, 26, lighten(guard[0], 0.5))
    cv.line(11, 22, 16, 16, guard[1])
    cv.line(10, 23, 17, 16, guard[0])
    for i in range(12):
        x = 15 + i
        y = 18 - i + (curve if i > 5 else 0)
        cv.px(x, y + 1, darken(blade[2], 0.3))
        cv.px(x, y, blade[1])
        cv.px(x, y - 1, blade[0])
    cv.px(27, 7, (255, 255, 255, 240))
    cv.px(16, 17, lighten(blade[0], 0.4))
    save(cv, name)


def jian(name, blade, guard):
    """双刃剑（铁剑/天子剑）"""
    cv = Cv(S, S)
    cv.line(8, 27, 14, 21, HANDLE[2])
    cv.line(9, 27, 15, 21, HANDLE[1])
    cv.rect(6, 25, 11, 29, guard[2])
    cv.rect(7, 26, 10, 28, guard[1])
    cv.px(7, 26, lighten(guard[0], 0.5))
    cv.line(11, 22, 16, 17, guard[0])
    for i in range(12):
        x, y = 15 + i, 18 - i
        cv.px(x, y + 1, darken(blade[2], 0.25))
        cv.px(x, y, blade[1])
        cv.px(x, y - 1, lighten(blade[0], 0.25))
    cv.px(27, 6, (255, 255, 255, 245))
    save(cv, name)


def bow(name, limb, string_=(220, 210, 180, 255), arrow=None):
    cv = Cv(S, S)
    cv.line(10, 4, 6, 12, limb[2])
    cv.line(6, 12, 6, 20, limb[1])
    cv.line(6, 20, 10, 28, limb[2])
    cv.line(11, 4, 7, 12, limb[1])
    cv.line(7, 12, 7, 20, limb[0])
    cv.line(7, 20, 11, 28, limb[1])
    cv.line(11, 5, 11, 27, string_)
    for y in range(6, 27, 4):
        cv.px(12, y, darken(limb[3], 0.2))
    if arrow:
        cv.line(12, 16, 28, 16, arrow[2])
        cv.line(12, 15, 28, 15, arrow[0])
        cv.poly([(28, 16), (25, 13), (25, 19)], arrow[1])
    save(cv, name)


def axe(name, head, shaft=DARK_WOOD):
    cv = Cv(S, S)
    cv.rect(14, 6, 17, 30, shaft[2])
    cv.rect(14, 7, 16, 29, shaft[1])
    cv.poly([(9, 8), (15, 3), (16, 12), (11, 14)], head[2])
    cv.poly([(10, 9), (15, 5), (15, 12), (11, 13)], head[1])
    cv.poly([(17, 3), (23, 6), (23, 13), (17, 12)], head[3])
    cv.poly([(18, 5), (22, 7), (22, 12), (18, 11)], head[0])
    cv.line(11, 12, 16, 13, darken(head[3], 0.3))
    cv.px(15, 4, lighten(head[0], 0.55))
    save(cv, name)


# ------------------------------------------------------------------ 护甲物品
def armor_piece(name, kind, main, trim, accent):
    cv = Cv(S, S)
    if kind == "helmet":
        cv.poly([(8, 18), (16, 6), (24, 18), (24, 22), (8, 22)], main[2])
        cv.poly([(10, 18), (16, 8), (22, 18), (22, 20), (10, 20)], main[1])
        cv.rect(11, 20, 21, 22, darken(main[3], 0.2))
        cv.rect(14, 14, 18, 20, accent)
        cv.px(16, 12, lighten(accent, 0.5))
        cv.line(8, 18, 24, 18, trim[0])
    elif kind == "chestplate":
        cv.poly([(8, 9), (13, 7), (19, 7), (24, 9), (24, 24), (8, 24)], main[2])
        cv.poly([(10, 10), (13, 8), (19, 8), (22, 10), (22, 22), (10, 22)], main[1])
        cv.poly([(13, 8), (16, 12), (19, 8), (19, 10), (16, 14), (13, 10)], accent)
        cv.rect(14, 16, 18, 20, accent)
        cv.line(8, 22, 24, 22, trim[0])
        cv.px(11, 11, lighten(main[0], 0.4))
    elif kind == "leggings":
        cv.rect(9, 8, 23, 14, main[2])
        cv.rect(10, 9, 22, 13, main[1])
        cv.rect(10, 14, 15, 27, main[2])
        cv.rect(17, 14, 22, 27, main[2])
        cv.rect(11, 14, 14, 26, main[1])
        cv.rect(18, 14, 21, 26, main[1])
        cv.line(9, 13, 23, 13, trim[0])
        cv.px(12, 18, lighten(accent, 0.3))
        cv.px(19, 18, lighten(accent, 0.3))
    else:  # boots
        cv.poly([(9, 8), (14, 8), (14, 22), (20, 22), (20, 27), (8, 27), (8, 12)], main[2])
        cv.poly([(10, 10), (13, 10), (13, 22), (18, 22), (18, 25), (9, 25)], main[1])
        cv.line(9, 16, 14, 16, trim[0])
        cv.rect(9, 23, 18, 25, darken(main[3], 0.25))
        cv.px(11, 12, lighten(accent, 0.35))
    cv.frame(6, 4, 25, 29, trim[1])
    save(cv, name)


def seal_item(name, body, accent, glyph="seal"):
    """玺印类：方正 + 顶钮 + 刻字"""
    cv = Cv(S, S)
    cv.rect(7, 12, 24, 27, body[2])
    cv.rect(8, 13, 23, 26, body[1])
    cv.rect(9, 14, 22, 25, body[0])
    cv.rect(13, 7, 18, 12, accent[2])
    cv.rect(14, 8, 17, 11, accent[0])
    cv.rect(15, 1, 16, 7, accent[1])
    cv.px(14, 2, lighten(accent[0], 0.5))
    cv.frame(9, 14, 22, 25, darken(body[3], 0.35))
    if glyph == "dragon":
        cv.line(11, 17, 20, 17, accent[0])
        cv.line(11, 21, 20, 21, accent[0])
        cv.line(15, 17, 15, 23, accent[1])
        cv.px(13, 19, accent[0])
        cv.px(18, 19, accent[0])
    elif glyph == "jie":
        cv.rect(12, 17, 19, 23, accent[1])
        cv.rect(14, 19, 17, 21, darken(body[3], 0.4))
    else:
        cv.line(12, 18, 19, 18, accent[0])
        cv.line(15, 18, 15, 23, accent[0])
        cv.line(12, 22, 19, 22, accent[1])
    save(cv, name)


def scroll_item(name, paper, ink, glyph=True):
    """图纸 / 文书"""
    cv = Cv(S, S)
    cv.rect(5, 7, 26, 25, GOLD_TRIM)
    cv.rect(6, 8, 25, 24, paper[1])
    cv.rect(7, 9, 24, 23, paper[0])
    cv.rect(5, 6, 26, 8, GOLD[1])
    cv.rect(5, 24, 26, 26, GOLD[2])
    if glyph:
        cv.line(10, 13, 20, 13, ink)
        cv.line(10, 16, 22, 16, ink)
        cv.line(10, 19, 17, 19, ink)
        cv.poly([(19, 18), (23, 20), (19, 22)], CINNABAR[2])
    save(cv, name)


def head_item(name, flesh, accent):
    """首级类"""
    cv = Cv(S, S)
    cv.disc(16, 17, 9, flesh[2])
    cv.disc(16, 17, 8, flesh[1])
    cv.disc(14, 15, 6, flesh[0])
    cv.rect(12, 14, 20, 16, darken(flesh[3], 0.45))
    cv.px(13, 15, (30, 30, 30, 255))
    cv.px(19, 15, (30, 30, 30, 255))
    cv.line(14, 20, 18, 20, darken(flesh[3], 0.5))
    cv.rect(9, 22, 23, 25, accent[2])
    cv.rect(10, 23, 22, 24, accent[1])
    cv.px(12, 10, darken(flesh[3], 0.3))
    save(cv, name)


def token_item(name, body, accent):
    """令牌类（长方形木牌 + 刻纹）"""
    cv = Cv(S, S)
    cv.rect(10, 4, 22, 28, body[2])
    cv.rect(11, 5, 21, 27, body[1])
    cv.frame(12, 6, 20, 26, darken(body[3], 0.3))
    cv.disc(16, 9, 2, accent[1])
    cv.line(13, 13, 19, 13, accent[0])
    cv.line(13, 17, 19, 17, accent[0])
    cv.line(16, 13, 16, 22, accent[1])
    cv.line(13, 22, 19, 22, accent[0])
    save(cv, name)


def bone_item(name):
    cv = Cv(S, S)
    cv.rect(9, 14, 24, 19, BONE[2])
    cv.rect(10, 15, 23, 18, BONE[1])
    cv.line(10, 15, 23, 15, BONE[0])
    cv.disc(9, 13, 3, BONE[1])
    cv.disc(9, 20, 3, BONE[1])
    cv.disc(24, 13, 3, BONE[2])
    cv.disc(24, 20, 3, BONE[2])
    cv.px(9, 11, lighten(BONE[0], 0.4))
    cv.px(24, 11, lighten(BONE[0], 0.3))
    for x in range(12, 22, 3):
        cv.px(x, 17, darken(BONE[3], 0.25))
    save(cv, name)


def ingot_item(name, metal):
    cv = Cv(S, S)
    cv.poly([(7, 20), (12, 11), (24, 11), (27, 20)], metal[2])
    cv.poly([(9, 19), (13, 13), (23, 13), (25, 19)], metal[1])
    cv.poly([(11, 17), (14, 14), (22, 14), (23, 17)], metal[0])
    cv.line(7, 20, 27, 20, darken(metal[3], 0.35))
    cv.px(15, 15, lighten(metal[0], 0.55))
    save(cv, name)


def mirror_item(name):
    """护心镜：圆镜 + 背面云纹 + 挂绳"""
    cv = Cv(S, S)
    cv.disc(16, 17, 10, BRONZE[3])
    cv.disc(16, 17, 9, BRONZE[1])
    cv.ring(16, 17, 7, BRONZE[0], 1)
    cv.disc(15, 16, 5, SILVER[1])
    cv.disc(14, 15, 3, SILVER[0])
    cv.px(13, 14, (255, 255, 255, 235))
    cv.line(11, 8, 16, 7, GOLD_TRIM)
    cv.line(21, 8, 16, 7, GOLD_TRIM)
    cv.px(16, 6, CINNABAR[2])
    for a in range(6):
        cv.px(16 + a - 3, 26, BRONZE[2])
    save(cv, name)


def crown_item(name):
    """玉冠：发冠 + 玉珠"""
    cv = Cv(S, S)
    cv.rect(8, 14, 24, 24, JADE[3])
    cv.rect(9, 15, 23, 23, JADE[1])
    cv.poly([(9, 15), (12, 8), (15, 15)], JADE[2])
    cv.poly([(13, 15), (16, 6), (19, 15)], JADE[1])
    cv.poly([(17, 15), (20, 8), (23, 15)], JADE[2])
    cv.px(16, 7, lighten(JADE[0], 0.55))
    cv.rect(10, 19, 22, 22, GOLD[1])
    cv.px(13, 21, CINNABAR[1])
    cv.px(16, 21, CINNABAR[2])
    cv.px(19, 21, CINNABAR[1])
    save(cv, name)


def talisman(name, ink, glow):
    """符箓：黄纸 + 朱砂符文 / talisman: yellow paper with a cinnabar glyph"""
    cv = Cv(S, S)
    cv.rect(6, 2, 25, 29, (232, 214, 150, 255))
    cv.rect(7, 3, 24, 28, (245, 232, 178, 255))
    cv.rect(6, 2, 25, 4, (196, 170, 96, 255))
    cv.rect(6, 28, 25, 29, (196, 170, 96, 255))
    cv.line(11, 7, 20, 7, ink)
    cv.line(15, 7, 15, 15, ink)
    cv.line(11, 11, 20, 11, ink)
    cv.line(12, 15, 19, 15, ink)
    cv.line(12, 18, 19, 18, ink)
    cv.line(15, 18, 15, 25, ink)
    cv.line(11, 22, 20, 22, ink)
    cv.px(15, 5, glow)
    for y in range(6, 27, 5):
        cv.px(8, y, darken(ink, 0.4))
        cv.px(23, y, darken(ink, 0.4))
    save(cv, name)


def charm_piece(name, kind, main, accent):
    """新饰品贴图：蝉 / 珍珠 / 指环 / 符牌 / 明月 / 虎符"""
    cv = Cv(S, S)
    if kind == "cicada":
        cv.poly([(16, 6), (23, 13), (21, 25), (11, 25), (9, 13)], main[2])
        cv.poly([(16, 8), (21, 13), (19, 23), (13, 23), (11, 13)], main[1])
        cv.line(16, 9, 16, 23, main[0])
        cv.line(11, 13, 15, 17, main[0])
        cv.line(21, 13, 17, 17, main[0])
        cv.px(13, 10, lighten(main[0], 0.6))
        cv.px(15, 6, accent)
        cv.px(17, 6, accent)
    elif kind == "pearl":
        cv.disc(16, 17, 9, main[3])
        cv.disc(16, 17, 8, main[1])
        cv.disc(15, 16, 6, main[0])
        cv.px(13, 13, (255, 255, 255, 240))
        cv.ring(16, 17, 9, accent, 1)
        for a in range(8):
            cv.px(16 + int(9 * __import__("math").cos(a)), 17 + int(9 * __import__("math").sin(a)) * -1,
                  accent)
    elif kind == "ring":
        cv.ring(16, 18, 8, main[2], 3)
        cv.ring(16, 18, 7, main[0], 1)
        cv.disc(16, 8, 3, accent)
        cv.px(15, 7, lighten(accent, 0.5))
        cv.px(12, 22, main[1])
        cv.px(20, 22, main[1])
    elif kind == "tablet":
        cv.rect(9, 5, 22, 27, main[2])
        cv.rect(10, 6, 21, 26, main[1])
        cv.frame(11, 7, 20, 25, darken(main[3], 0.25))
        cv.line(13, 10, 18, 10, accent)
        cv.line(13, 14, 18, 14, accent)
        cv.line(16, 10, 16, 20, accent)
        cv.line(13, 20, 18, 20, accent)
    elif kind == "moon":
        cv.disc(16, 16, 10, main[2])
        cv.disc(16, 16, 9, main[1])
        cv.disc(13, 14, 7, main[0])
        cv.disc(21, 17, 7, (0, 0, 0, 0))
        cv.line(11, 24, 21, 24, accent)
        cv.px(12, 6, accent)
    elif kind == "tortoise":
        cv.poly([(16, 5), (25, 11), (23, 23), (16, 27), (9, 23), (7, 11)], main[2])
        cv.poly([(16, 7), (23, 12), (21, 22), (16, 25), (11, 22), (9, 12)], main[1])
        cv.line(16, 8, 16, 24, main[0])
        cv.line(11, 14, 21, 14, main[0])
        cv.line(11, 20, 21, 20, main[0])
        cv.px(16, 6, accent)
    elif kind == "bag":
        cv.poly([(9, 12), (23, 12), (25, 26), (7, 26)], main[2])
        cv.poly([(11, 13), (21, 13), (23, 24), (9, 24)], main[1])
        cv.line(9, 12, 16, 8, accent)
        cv.line(23, 12, 16, 8, accent)
        cv.px(16, 8, accent)
        cv.rect(13, 17, 19, 21, main[0])
        cv.px(14, 18, accent)
    elif kind == "feather":
        cv.poly([(16, 4), (21, 13), (19, 24), (16, 28), (13, 24), (11, 13)], main[2])
        cv.poly([(16, 6), (19, 13), (17, 22), (16, 26), (15, 22), (13, 13)], main[1])
        cv.line(16, 6, 16, 26, main[0])
        for y in range(9, 23, 3):
            cv.line(16, y, 19, y + 2, main[0])
            cv.line(16, y, 13, y + 2, main[0])
        cv.px(16, 5, accent)
    elif kind == "bell":
        cv.poly([(9, 20), (11, 10), (16, 6), (21, 10), (23, 20)], main[2])
        cv.poly([(11, 19), (12, 11), (16, 8), (20, 11), (21, 19)], main[1])
        cv.rect(9, 20, 23, 23, main[0])
        cv.line(12, 12, 20, 12, accent)
        cv.px(16, 6, accent)
        cv.rect(15, 24, 17, 27, accent)
    else:  # crest 虎符
        cv.poly([(16, 5), (24, 10), (24, 22), (16, 27), (8, 22), (8, 10)], main[2])
        cv.poly([(16, 7), (22, 12), (22, 20), (16, 25), (10, 20), (10, 12)], main[1])
        cv.line(12, 14, 20, 14, accent)
        cv.line(12, 18, 20, 18, accent)
        cv.px(16, 11, lighten(main[0], 0.5))
    save(cv, name)


def ritual_altar_block():
    """法阵·祭坛方块贴图：白玉底 + 玉环 + 中央灵火"""
    cv = Cv(32, 32)
    for y in range(32):
        for x in range(32):
            t = (x + y) / 62.0
            cv.px(x, y, mix(lighten(MARBLE[1], 0.15), darken(MARBLE[3], 0.1), t))
    cv.rect(0, 0, 31, 1, MARBLE[3])
    cv.rect(0, 30, 31, 31, MARBLE[3])
    cv.rect(0, 0, 1, 31, MARBLE[3])
    cv.rect(30, 0, 31, 31, MARBLE[3])
    cv.ring(16, 16, 12, JADE[1], 3)
    cv.ring(16, 16, 8, JADE[0], 2)
    for a in range(0, 360, 45):
        import math
        x = 16 + int(round(10 * math.cos(math.radians(a))))
        y = 16 + int(round(10 * math.sin(math.radians(a))))
        cv.px(x, y, GOLD_TRIM)
    cv.disc(16, 16, 5, CINNABAR[3])
    cv.disc(16, 16, 4, CINNABAR[1])
    cv.disc(15, 15, 2, LAMP_GLOW if isinstance(LAMP_GLOW, tuple) else (255, 226, 150, 255))
    cv.save(os.path.join(BLOCK_OUT, "ritual_altar.png"))
    print("  block: ritual_altar")


def slot_icon(name):
    """饰品槽图标（16x16，和 Curios 槽位同尺寸）"""
    cv = Cv(16, 16)
    cv.rect(1, 1, 14, 14, (60, 45, 28))
    cv.rect(2, 2, 13, 13, (28, 20, 12))
    cv.ring(8, 8, 5, GOLD_TRIM, 1)
    cv.disc(7, 7, 2, BRONZE[0])
    cv.px(6, 6, (255, 246, 214, 240))
    cv.frame(1, 1, 14, 14, GOLD[2])
    cv.save(os.path.join(SLOT_OUT, name + ".png"))
    print("  slot:", name)


def armor_layer(name, main, trim, accent, plate_lines=True):
    """64x32 原版人形护甲布局 / vanilla humanoid armour layer"""
    cv = Cv(64, 32)
    for y in range(32):
        for x in range(64):
            t = y / 31.0
            cv.px(x, y, mix(lighten(main[1], 0.18), darken(main[3], 0.15), t))
    if plate_lines:
        for y in range(0, 32, 6):
            for x in range(64):
                cv.px(x, y, darken(main[3], 0.35))
                if y + 1 < 32:
                    cv.px(x, y + 1, lighten(main[1], 0.2))
    for y in range(2, 32, 8):
        for x in range(2, 64, 8):
            cv.px(x, y, trim[0])
            cv.px(x, y + 1, darken(trim[2], 0.2))
    for x in range(0, 64, 16):
        for y in range(32):
            if x + 1 < 64:
                cv.px(x, y, lighten(cv.get(x, y), 0.12))
    for x in range(64):
        cv.px(x, 18, trim[1])
        cv.px(x, 19, trim[0])
        cv.px(x, 20, darken(trim[2], 0.25))
    for y in range(23, 29):
        for x in range(21, 27):
            cv.px(x, y, accent)
    rnd = random.Random(11)
    for _ in range(60):
        cv.px(rnd.randrange(64), rnd.randrange(32), darken(main[3], 0.3))
    cv.save(os.path.join(ARMOR_OUT, name + ".png"))
    print("  armor layer:", name)


def main():
    print("== 武器 / weapons ==")
    spear("mu_mao", WOOD)
    spear("shi_ge", STONE)
    dao("tong_dao", COPPER, GOLD)
    jian("tie_jian", IRON_M, BRONZE)
    bow("lie_gong", WOOD, arrow=WOOD)
    bow("chang_gong", DARK_WOOD, arrow=IRON_M)
    # 弓·速射支线：长弓 → 神臂弓 → 落雁弓 → 天狼弓
    # Bow (rapid-fire branch): Shenbi -> Luoyan -> Tianlang
    bow("shenbi_bow", ramp(hx("7A5A32"), 5), string_=hx("D8CFA8"), arrow=IRON_M)
    bow("luoyan_bow", ramp(hx("9AA6B8"), 5), string_=hx("CFE6F0"), arrow=IRON_M)
    bow("tianlang_bow", ramp(hx("4A5A9A"), 5), string_=hx("8FD0F0"), arrow=DRAGON_CRYSTAL)
    axe("xuantian_axe", DRAGON_CRYSTAL)
    jian("tianzi_sword", GOLD, DRAGON_CRYSTAL)

    print("== 护甲 / armor ==")
    for kind in ("helmet", "chestplate", "leggings", "boots"):
        armor_piece("cloth_" + kind, kind, CLOTH_M, CLOTH2, hx("D8C7A0"))
        armor_piece("xuantian_" + kind, kind, XUAN_MAIN, XUAN_TRIM, hx("7FE8D0"))

    print("== 材料与信物 / relics ==")
    scroll_item("blueprint", ramp(hx("E8DCB0"), 5), INK)
    ingot_item("refined_steel", IRON_M)
    head_item("rebel_head", ramp(hx("A8703C"), 5), ramp(hx("6B1F1F"), 4))
    token_item("eunuch_token", DARK_WOOD, PURPLE_SILK)
    bone_item("emperor_bone")
    seal_item("dragon_emperor_seal", GOLD, DRAGON_CRYSTAL, glyph="dragon")
    seal_item("xuantian_jade", JADE, GOLD, glyph="jie")

    print("== 饰品 / trinkets ==")
    mirror_item("heart_mirror")
    crown_item("jade_crown")
    slot_icon("empty_trinket_slot")

    print("== 新符箓 / new talismans ==")
    talisman("vajra_talisman", hx("8B6A1F"), hx("FFE08A"))
    talisman("soul_talisman", hx("5A2C7A"), hx("D9A6FF"))

    print("== 新饰品 / new trinkets ==")
    charm_piece("jade_cicada", "cicada", JADE, GOLD_TRIM)
    charm_piece("dragon_pearl", "pearl", DRAGON_CRYSTAL, GOLD_TRIM)
    charm_piece("phoenix_ring", "ring", ramp(hx("D9481F"), 5), hx("FFD75E"))
    charm_piece("storm_charm", "tablet", ramp(hx("4A5A8A"), 5), CINNABAR[1])
    charm_piece("moon_pendant", "moon", ramp(hx("D8DCE8"), 5), GOLD_TRIM)
    charm_piece("tiger_crest", "crest", BRONZE, GOLD_TRIM)
    charm_piece("jade_tortoise", "tortoise", JADE, GOLD_TRIM)
    charm_piece("war_drum_charm", "tablet", ramp(hx("8B1F1F"), 5), GOLD_TRIM)
    charm_piece("cinnabar_pouch", "bag", ramp(hx("C0392B"), 5), hx("F5D76E"))
    charm_piece("dragon_whisker", "feather", DRAGON_CRYSTAL, GOLD_TRIM)
    charm_piece("tiger_token", "crest", ramp(hx("C8A02A"), 5), hx("6B1F1F"))
    charm_piece("sun_feather", "feather", ramp(hx("E8A02A"), 5), hx("FFF0A0"))
    charm_piece("war_horse_bell", "bell", BRONZE, hx("FFD75E"))
    charm_piece("iron_waist_token", "tablet", ramp(hx("6A7078"), 5), hx("D8D8D8"))
    charm_piece("auspicious_bell", "bell", GOLD, CINNABAR[1])

    print("== 新方块 / new blocks ==")
    ritual_altar_block()

    print("== 护甲层 / armor layers ==")
    armor_layer("cloth_layer_1", CLOTH_M, CLOTH2, hx("D8C7A0"))
    armor_layer("cloth_layer_2", CLOTH_M, CLOTH2, hx("D8C7A0"), plate_lines=False)
    armor_layer("xuantian_layer_1", XUAN_MAIN, XUAN_TRIM, hx("7FE8D0"))
    armor_layer("xuantian_layer_2", XUAN_MAIN, XUAN_TRIM, hx("7FE8D0"), plate_lines=False)
    print("完成 / done")


if __name__ == "__main__":
    main()
