"""物品贴图修正 A：狐尾、麒麟角、凤羽、镐。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32
HANDLE = ramp(hx("6B4423"), 5)
FUR = ramp(hx("D98A3C"), 6)
FUR_PALE = ramp(hx("F5EDE0"), 5)


def fox_tail():
    cv = Cv(S, S)
    lobes = [(21, 25, 7, FUR[3]), (19, 20, 7, FUR[2]), (16, 15, 7, FUR[1]), (13, 10, 6, FUR[0]),
             (10, 7, 5, FUR_PALE[2]), (8, 5, 4, FUR_PALE[1])]
    for x, y, r, c in lobes:
        cv.disc(x, y, r, c)
    for x, y, r, c in lobes:
        cv.disc(x - 1, y - 1, r - 2, lighten(c, 0.22))
    for i in range(9):
        cv.px(24 - i * 2, 28 - i * 2, darken(FUR[3], 0.25))
        cv.px(22 - i * 2, 29 - i * 2, darken(FUR[3], 0.15))
    cv.px(9, 4, (255, 255, 255, 235))
    cv.px(11, 6, (255, 255, 255, 200))
    save(cv, "fox_tail")


def qilin_horn():
    cv = Cv(S, S)
    for t in range(22):
        f = t / 21.0
        x = 9 + int(f * 15 - f * f * 4)
        y = 27 - int(f * 22)
        r = max(1, int(4 - f * 3))
        col = mix(BONE[2], BONE[0], f)
        cv.disc(x, y, r, col)
        cv.disc(x - 1, y, r - 1, lighten(col, 0.25))
        if t % 3 == 0 and r > 1:
            cv.line(x - r, y, x + r, y, darken(BONE[3], 0.2))
    cv.px(23, 5, lighten(BONE[0], 0.5))
    cv.px(12, 24, lighten(BONE[0], 0.35))
    save(cv, "qilin_horn")


def phoenix_feather():
    cv = Cv(S, S)
    cv.line(8, 27, 23, 5, (240, 200, 110, 255))
    cv.line(8, 28, 23, 6, (200, 150, 60, 255))
    for i in range(9):
        t = i / 8.0
        x = 9 + int(t * 13)
        y = 26 - int(t * 20)
        length = int(7 - t * 3)
        for k in range(1, length):
            cv.px(x + k, y - k // 2, mix(FIRE[0], FIRE[2], k / length))
            cv.px(x - k, y + k // 2, mix(FIRE[1], FIRE[2], k / length))
    cv.poly([(23, 5), (27, 8), (21, 10)], (255, 226, 150, 255))
    cv.px(22, 6, (255, 250, 230, 240))
    cv.px(12, 22, (255, 232, 170, 220))
    save(cv, "phoenix_feather")


def pickaxe(name, head):
    cv = Cv(S, S)
    cv.line(10, 28, 19, 14, HANDLE[2])
    cv.line(11, 28, 20, 14, HANDLE[1])
    cv.line(11, 27, 19, 14, HANDLE[0])
    cv.px(10, 28, darken(HANDLE[3], 0.2))
    cv.poly([(12, 13), (16, 8), (19, 10), (15, 14)], head[3])
    cv.poly([(13, 13), (16, 9), (18, 10), (15, 13)], head[0])
    cv.poly([(19, 10), (26, 8), (28, 11), (22, 13), (19, 13)], head[3])
    cv.poly([(20, 11), (26, 9), (27, 11), (22, 12), (20, 12)], head[0])
    cv.poly([(12, 13), (8, 16), (10, 19), (15, 15)], head[2])
    cv.poly([(13, 14), (9, 16), (11, 18), (15, 16)], head[1])
    cv.line(16, 9, 16, 12, lighten(head[0], 0.5))
    cv.px(27, 9, lighten(head[0], 0.6))
    cv.px(9, 16, lighten(head[0], 0.4))
    save(cv, name)


if __name__ == "__main__":
    fox_tail(); qilin_horn(); phoenix_feather()
    pickaxe("pickaxe_jade", JADE)
    pickaxe("pickaxe_dragon_crystal", DRAGON_CRYSTAL)
    print("item fixes A applied")
