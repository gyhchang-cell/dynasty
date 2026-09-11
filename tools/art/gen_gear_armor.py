"""王朝护甲件贴图（头盔/胸甲/护腿/靴子 × 3 套）。"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32


def armor_helmet(name, main, trim, accent):
    cv = Cv(S, S)
    cv.disc(15.5, 16, 10, darken(main[2], 0.25))
    cv.disc(15.5, 16, 9, main[1])
    cv.disc(13, 13, 5, main[0])
    cv.rect(6, 16, 25, 22, main[1])
    cv.rect(7, 17, 24, 21, main[0])
    cv.rect(11, 14, 20, 20, darken(main[3], 0.55))
    cv.rect(12, 15, 19, 18, darken(main[3], 0.72))
    cv.rect(6, 22, 25, 23, trim[1])
    cv.rect(7, 23, 24, 23, trim[0])
    for x in range(9, 23, 4):
        cv.px(x, 23, lighten(trim[0], 0.4))
    cv.rect(15, 4, 16, 8, accent)
    cv.line(14, 5, 17, 5, lighten(accent, 0.35))
    cv.px(12, 12, lighten(main[0], 0.5))
    save(cv, name)


def armor_chestplate(name, main, trim, accent):
    cv = Cv(S, S)
    cv.poly([(9, 8), (22, 8), (24, 14), (23, 25), (8, 25), (7, 14)], darken(main[2], 0.25))
    cv.poly([(10, 9), (21, 9), (22, 14), (21, 24), (10, 24), (9, 14)], main[1])
    cv.poly([(11, 10), (20, 10), (20, 15), (11, 15)], main[0])
    cv.rect(12, 16, 19, 23, main[1])
    cv.line(11, 17, 20, 17, darken(main[3], 0.3))
    cv.line(11, 21, 20, 21, darken(main[3], 0.3))
    cv.rect(4, 9, 9, 15, main[2])
    cv.rect(22, 9, 27, 15, main[2])
    cv.rect(4, 9, 9, 11, main[0])
    cv.rect(22, 9, 27, 11, main[0])
    cv.rect(13, 11, 18, 15, accent)
    cv.px(14, 12, lighten(accent, 0.45))
    cv.rect(9, 25, 22, 27, trim[1])
    cv.rect(10, 26, 21, 26, trim[0])
    save(cv, name)


def armor_leggings(name, main, trim, accent):
    cv = Cv(S, S)
    cv.rect(9, 6, 22, 13, main[1])
    cv.rect(10, 6, 21, 9, main[0])
    cv.rect(9, 12, 22, 14, trim[1])
    cv.rect(10, 13, 21, 14, trim[0])
    cv.rect(10, 15, 15, 27, main[1])
    cv.rect(16, 15, 21, 27, main[1])
    cv.line(10, 15, 10, 27, main[0])
    cv.line(16, 15, 16, 27, main[0])
    cv.line(15, 15, 15, 27, darken(main[3], 0.35))
    cv.line(22, 15, 22, 27, darken(main[3], 0.35))
    cv.rect(10, 22, 15, 23, accent)
    cv.rect(16, 22, 21, 23, accent)
    cv.rect(10, 26, 15, 27, trim[1])
    cv.rect(16, 26, 21, 27, trim[1])
    save(cv, name)


def armor_boots(name, main, trim, accent):
    cv = Cv(S, S)
    for ox in (4, 17):
        cv.rect(ox + 2, 8, ox + 9, 22, main[1])
        cv.rect(ox + 3, 9, ox + 8, 14, main[0])
        cv.rect(ox, 22, ox + 11, 26, main[2])
        cv.rect(ox + 1, 22, ox + 10, 24, main[1])
        cv.rect(ox + 2, 15, ox + 9, 16, accent)
        cv.rect(ox, 25, ox + 11, 26, darken(main[3], 0.4))
        cv.rect(ox + 2, 7, ox + 9, 8, trim[1])
    cv.px(7, 10, lighten(main[0], 0.45))
    cv.px(20, 10, lighten(main[0], 0.45))
    save(cv, name)


if __name__ == "__main__":
    sets = {
        "jade": (JADE, GOLD, hx("A9E8BC")),
        "dragon_scale": (DRAGON_CRYSTAL, BRONZE, lighten(DRAGON_CRYSTAL[0], 0.4)),
        "general": (ramp(hx("5A6472"), 5), GOLD, hx("C0392B")),
    }
    for prefix, (main, trim, accent) in sets.items():
        armor_helmet(prefix + "_helmet", main, trim, accent)
        armor_chestplate(prefix + "_chestplate", main, trim, accent)
        armor_leggings(prefix + "_leggings", main, trim, accent)
        armor_boots(prefix + "_boots", main, trim, accent)
    print("armor items done:", len(os.listdir(OUT)))
