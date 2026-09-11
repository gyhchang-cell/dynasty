"""新增物品贴图：工艺材料。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32


def materials():
    cv = Cv(S, S)
    cv.disc(16, 18, 8, hx("F0E8D0"))
    cv.disc(15, 16, 6, hx("FFFBF0"))
    for i in range(6):
        cv.line(8 + i * 3, 24 - i, 12 + i * 3, 22 - i, hx("E0D8C0"))
    cv.line(16, 4, 16, 10, hx("D9C08B"))
    cv.px(13, 14, (255, 255, 255, 240))
    save(cv, "raw_silk")

    cv = Cv(S, S)
    cv.poly([(5, 12), (27, 12), (27, 22), (5, 22)], hx("C8402F"))
    cv.poly([(5, 12), (27, 12), (24, 15), (8, 15)], hx("E8604A"))
    cv.poly([(5, 15), (27, 15), (27, 19), (5, 19)], hx("A82C24"))
    cv.poly([(5, 19), (27, 19), (24, 22), (8, 22)], hx("8B1A14"))
    cv.line(7, 13, 25, 13, hx("F5A090"))
    cv.px(9, 20, hx("F0A090"))
    save(cv, "silk")

    cv = Cv(S, S)
    cv.rect(5, 8, 26, 25, hx("6B1F4A"))
    cv.rect(6, 9, 25, 24, hx("8B2A5A"))
    for x in range(8, 24, 4):
        for y in range(11, 23, 4):
            cv.disc(x, y, 2, hx("E8C86A"))
            cv.px(x, y, hx("FFF0B0"))
    cv.line(6, 12, 25, 12, hx("C98A3C"))
    cv.line(6, 21, 25, 21, hx("C98A3C"))
    save(cv, "brocade")

    cv = Cv(S, S)
    for x in (9, 15, 21):
        cv.rect(x, 5, x + 4, 27, hx("A87A3C"))
        cv.rect(x, 5, x + 3, 27, hx("C99A4A"))
        cv.px(x, 7, hx("8B5A2B"))
        for y in range(9, 25, 3):
            cv.line(x + 1, y, x + 3, y, hx("3A2414"))
    cv.line(8, 6, 26, 6, hx("8B5A2B"))
    cv.line(8, 26, 26, 26, hx("8B5A2B"))
    save(cv, "bamboo_slip")

    cv = Cv(S, S)
    cv.rect(8, 11, 24, 23, hx("1A1A22"))
    cv.rect(9, 12, 23, 22, hx("2A2A34"))
    cv.rect(11, 14, 21, 20, hx("3A3A46"))
    cv.line(13, 17, 19, 17, hx("C9A24A"))
    cv.px(14, 19, hx("E8C86A"))
    cv.px(18, 15, hx("E8C86A"))
    cv.px(10, 13, hx("6A6A7A"))
    save(cv, "ink_stick")

    cv = Cv(S, S)
    cv.line(9, 27, 20, 12, hx("8B5A2B"))
    cv.line(10, 27, 21, 12, hx("A87A3C"))
    for i in range(0, 11, 3):
        cv.px(9 + i, 27 - i, hx("6B4423"))
    cv.poly([(20, 12), (24, 6), (26, 9), (22, 14)], hx("D9C08B"))
    cv.poly([(21, 12), (24, 7), (25, 9), (22, 13)], hx("2A2A34"))
    cv.px(24, 6, hx("1A1A22"))
    save(cv, "ink_brush")

    cv = Cv(S, S)
    cv.disc(16, 17, 11, BRONZE[3])
    cv.disc(16, 17, 10, BRONZE[1])
    cv.disc(14, 15, 6, BRONZE[0])
    cv.ring(16, 17, 7, BRONZE[2])
    for a in range(0, 360, 45):
        rad = math.radians(a)
        cv.px(int(16 + math.cos(rad) * 7), int(17 + math.sin(rad) * 7), BRONZE_PATINA)
    cv.disc(16, 17, 2, GOLD_TRIM)
    cv.px(15, 16, lighten(GOLD_TRIM, 0.5))
    cv.px(11, 11, (255, 255, 255, 220))
    save(cv, "bronze_mirror")

    cv = Cv(S, S)
    cv.poly([(6, 24), (16, 8), (26, 24)], hx("B08A16"))
    cv.poly([(8, 23), (16, 10), (24, 23)], hx("E8C24A"))
    cv.poly([(11, 21), (16, 12), (21, 21)], hx("F5DEA0"))
    cv.line(6, 24, 26, 24, hx("8B6A0A"))
    for x in range(8, 25, 4):
        cv.px(x, 22, hx("A8800A"))
    cv.px(16, 10, (255, 255, 240, 230))
    save(cv, "roof_tile")


if __name__ == "__main__":
    materials()
    print("craft materials done")
