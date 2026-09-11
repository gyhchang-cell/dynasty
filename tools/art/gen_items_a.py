"""王朝物品贴图 A：货币 / 材料 / 文书（32x32）。"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/item")
os.makedirs(OUT, exist_ok=True)
S = 32
INK = (28, 20, 16, 255)


def save(cv, name):
    cv.outline(INK)
    cv.save(os.path.join(OUT, name + ".png"))


# ---------------------------------------------------------------- 通用
def coin(name, metal, face_glyph=True):
    cv = Cv(S, S)
    cv.disc(15.5, 15.5, 11, darken(metal[2], 0.25))
    cv.disc(15.5, 15.5, 10, metal[1])
    cv.disc(13, 13, 6, metal[0])
    cv.ring(15.5, 15.5, 10, metal[2])
    cv.ring(15.5, 15.5, 6, darken(metal[2], 0.15))
    cv.rect(12, 12, 19, 19, darken(metal[3], 0.35))          # 方孔 / square hole
    cv.frame(12, 12, 19, 19, metal[1])
    if face_glyph:
        cv.px(9, 9, lighten(metal[0], 0.55))                  # 高光 / specular
        cv.px(10, 9, lighten(metal[0], 0.35))
        cv.px(20, 22, darken(metal[3], 0.3))
    save(cv, name)


def ingot(name, metal):
    cv = Cv(S, S)
    cv.poly([(6, 20), (12, 12), (25, 12), (27, 17), (21, 23), (8, 23)], metal[2])
    cv.poly([(7, 20), (13, 13), (24, 13), (25, 16), (20, 22), (9, 22)], metal[1])
    cv.poly([(9, 18), (14, 14), (23, 14), (24, 15), (19, 19), (10, 19)], metal[0])
    cv.poly([(25, 13), (27, 16), (21, 20), (20, 19)], darken(metal[2], 0.3))
    cv.line(12, 16, 22, 16, lighten(metal[0], 0.4))
    save(cv, name)


def gem_cut(name, colors, tall=True):
    cv = Cv(S, S)
    cx, cy = 15.5, 16
    w, h = (9, 10) if tall else (10, 8)
    cv.poly([(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)], colors[3])
    cv.poly([(cx, cy - h + 1), (cx + w - 2, cy), (cx, cy + h - 1), (cx - w + 2, cy)], colors[1])
    cv.poly([(cx, cy - h + 1), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)], colors[0])
    cv.line(cx - w + 3, cy - 1, cx - 2, cy - h + 3, lighten(colors[0], 0.45))
    cv.px(cx - 2, cy - 4, (255, 255, 255, 235))
    cv.line(cx + 2, cy + 2, cx + w - 3, cy + 1, darken(colors[2], 0.15))
    save(cv, name)


def scale_plate(name, colors):
    cv = Cv(S, S)
    cv.poly([(15, 4), (26, 10), (26, 20), (15, 28), (4, 20), (4, 10)], colors[3])
    cv.poly([(15, 6), (24, 11), (24, 19), (15, 26), (6, 19), (6, 11)], colors[1])
    cv.poly([(15, 7), (22, 12), (22, 17), (15, 23), (8, 17), (8, 12)], colors[0])
    for i in range(3):
        y = 12 + i * 4
        cv.line(8, y, 22, y, colors[2])
        cv.px(15, y - 1, lighten(colors[0], 0.3))
    cv.px(11, 10, lighten(colors[0], 0.55))
    save(cv, name)


def cinnabar_chunk():
    cv = Cv(S, S)
    cv.poly([(7, 22), (10, 10), (18, 7), (25, 13), (24, 22), (14, 26)], CINNABAR[3])
    cv.poly([(9, 21), (11, 12), (17, 9), (23, 14), (22, 21), (14, 24)], CINNABAR[1])
    cv.poly([(12, 18), (13, 12), (17, 11), (20, 15), (18, 19), (14, 20)], CINNABAR[0])
    cv.px(14, 13, lighten(CINNABAR[0], 0.45))
    cv.px(19, 19, darken(CINNABAR[3], 0.25))
    save(cv, "cinnabar")


def fox_tail():
    cv = Cv(S, S)
    for i, (x, y, r, c) in enumerate(((18, 22, 6, (196, 126, 58, 255)), (15, 16, 6, (220, 150, 74, 255)),
                                      (12, 10, 5, (236, 170, 96, 255)), (10, 6, 4, (245, 238, 226, 255)))):
        cv.disc(x, y, r, c)
    cv.disc(19, 24, 4, (150, 92, 40, 255))
    cv.px(13, 12, (255, 255, 255, 230))
    cv.px(11, 15, (250, 244, 232, 220))
    save(cv, "fox_tail")


def qilin_horn():
    cv = Cv(S, S)
    pts = [(8, 26), (11, 18), (15, 10), (19, 5), (22, 4), (20, 9), (17, 15), (14, 21), (12, 27)]
    cv.poly(pts, BONE[3])
    cv.poly([(10, 25), (12, 18), (16, 11), (19, 7), (18, 11), (15, 17), (13, 23)], BONE[1])
    cv.poly([(12, 24), (13, 19), (16, 13), (15, 17), (13, 22)], BONE[0])
    cv.px(16, 12, lighten(BONE[0], 0.5))
    for i in range(4):
        y = 12 + i * 3
        cv.px(11 + i, y, darken(BONE[3], 0.2))
    cv.px(9, 25, darken(BONE[3], 0.25))
    save(cv, "qilin_horn")


def phoenix_feather():
    cv = Cv(S, S)
    cv.line(16, 27, 13, 6, (240, 190, 90, 255))
    for i in range(7):
        y0 = 8 + i * 3
        cv.line(14, y0, 22 - i, y0 + 3, FIRE[1] if i % 2 else FIRE[0])
        cv.line(14, y0, 8 + i // 2, y0 + 3, FIRE[2])
    cv.poly([(13, 4), (19, 8), (13, 12)], (255, 214, 120, 255))
    cv.px(16, 6, (255, 246, 214, 240))
    cv.px(11, 16, (255, 226, 150, 220))
    save(cv, "phoenix_feather")


if __name__ == "__main__":
    coin("copper_coin", ramp(hx("B87333"), 6))
    coin("silver_coin", SILVER)
    coin("gold_coin", GOLD)
    coin("jade_coin", JADE)
    coin("dragon_coin", DRAGON_CRYSTAL)
    ingot("bronze_ingot", BRONZE)
    ingot("silver_ingot", SILVER)
    gem_cut("jade", JADE)
    gem_cut("dragon_crystal", DRAGON_CRYSTAL, tall=True)
    scale_plate("dragon_scale", DRAGON_CRYSTAL)
    cinnabar_chunk()
    fox_tail()
    qilin_horn()
    phoenix_feather()
    print("items A done:", len(os.listdir(OUT)))
