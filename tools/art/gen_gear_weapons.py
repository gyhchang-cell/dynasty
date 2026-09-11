"""王朝武器与工具贴图。"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32
HANDLE = ramp(hx("6B4423"), 5)


def sword(name, blade, guard):
    cv = Cv(S, S)
    cv.line(8, 26, 14, 20, HANDLE[2])
    cv.line(9, 27, 15, 21, HANDLE[1])
    for i in range(0, 6, 2):
        cv.line(8 + i, 26 - i, 9 + i, 26 - i, HANDLE[3])
    cv.disc(7, 27, 3, guard[1])
    cv.disc(7, 27, 2, guard[0])
    cv.px(6, 26, lighten(guard[0], 0.5))
    cv.line(11, 22, 17, 16, guard[1])
    cv.line(10, 23, 17, 16, guard[0])
    cv.px(16, 15, lighten(guard[0], 0.45))
    cv.line(15, 19, 27, 7, darken(blade[2], 0.35))
    cv.line(15, 18, 27, 6, blade[1])
    cv.line(16, 18, 27, 7, blade[0])
    cv.line(15, 16, 25, 6, lighten(blade[0], 0.4))
    cv.line(17, 19, 27, 9, darken(blade[2], 0.15))
    cv.line(19, 15, 25, 9, mix(blade[1], (255, 255, 255, 255), 0.3))
    cv.px(27, 6, (255, 255, 255, 235))
    save(cv, name)


def pickaxe(name, head):
    cv = Cv(S, S)
    cv.line(10, 28, 20, 12, HANDLE[2])
    cv.line(11, 28, 21, 12, HANDLE[1])
    cv.line(11, 27, 20, 12, HANDLE[0])
    cv.px(10, 28, darken(HANDLE[3], 0.2))
    cv.poly([(13, 8), (28, 10), (28, 13), (13, 12)], head[2])
    cv.poly([(14, 9), (27, 11), (27, 11), (14, 11)], head[1])
    cv.line(14, 9, 27, 11, lighten(head[0], 0.45))
    cv.line(14, 12, 27, 13, darken(head[3], 0.3))
    cv.px(28, 11, lighten(head[0], 0.6))
    cv.line(15, 14, 17, 16, head[2])
    cv.px(15, 10, darken(head[3], 0.25))
    save(cv, name)


def halberd():
    cv = Cv(S, S)
    cv.rect(15, 8, 17, 30, DARK_WOOD[2])
    cv.rect(15, 9, 16, 29, DARK_WOOD[1])
    cv.px(15, 10, DARK_WOOD[0])
    cv.poly([(9, 12), (14, 5), (17, 12), (14, 10)], SILVER[2])
    cv.poly([(10, 12), (14, 7), (16, 12), (14, 10)], SILVER[1])
    cv.px(14, 7, lighten(SILVER[0], 0.5))
    cv.poly([(15, 4), (17, 1), (18, 5), (17, 8)], DRAGON_CRYSTAL[1])
    cv.line(16, 2, 16, 7, DRAGON_CRYSTAL[0])
    cv.px(16, 2, lighten(DRAGON_CRYSTAL[0], 0.5))
    cv.poly([(18, 12), (23, 9), (24, 13), (20, 15)], GOLD[1])
    cv.px(21, 10, lighten(GOLD[0], 0.5))
    cv.line(12, 13, 12, 17, hx("B22A20"))
    cv.line(13, 14, 13, 18, hx("D9453A"))
    cv.px(12, 18, hx("8B1A14"))
    cv.rect(14, 30, 18, 31, DARK_WOOD[3])
    save(cv, "halberd_fangtian")


if __name__ == "__main__":
    sword("sword_bronze", BRONZE, GOLD)
    sword("sword_silver", SILVER, GOLD)
    sword("sword_jade", JADE, GOLD)
    sword("sword_dragon_crystal", DRAGON_CRYSTAL, GOLD)
    pickaxe("pickaxe_jade", JADE)
    pickaxe("pickaxe_dragon_crystal", DRAGON_CRYSTAL)
    halberd()
    print("weapons done")
