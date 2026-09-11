"""新增物品贴图：六种符箓 + 任务手札 + 节令灯。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save, YELLOW_PAPER

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32


def talisman(name, glyph, aura):
    cv = Cv(S, S)
    cv.rect(9, 3, 22, 28, YELLOW_PAPER[3])
    cv.rect(10, 4, 21, 27, YELLOW_PAPER[1])
    cv.rect(10, 4, 21, 8, YELLOW_PAPER[0])
    cv.line(11, 6, 20, 6, aura)
    glyphs = {
        "swirl": [(13, 12, 18, 12), (18, 12, 18, 16), (18, 16, 13, 16), (13, 16, 13, 20), (13, 20, 19, 20)],
        "cloud": [(12, 13, 19, 13), (12, 16, 19, 16), (14, 19, 17, 19), (15, 22, 16, 22)],
        "life": [(14, 11, 17, 23), (11, 15, 20, 18)],
        "flame": [(16, 10, 13, 18), (16, 10, 19, 18), (13, 18, 16, 24), (19, 18, 16, 24)],
        "bolt": [(17, 10, 13, 17), (13, 17, 18, 17), (18, 17, 14, 24)],
        "return": [],
    }
    for x0, y0, x1, y1 in glyphs.get(glyph, []):
        cv.line(x0, y0, x1, y1, hx("C0392B"))
    if glyph == "return":
        cv.ring(16, 16, 6, hx("C0392B"))
        cv.line(16, 10, 16, 16, hx("C0392B"))
        cv.line(16, 16, 20, 18, hx("C0392B"))
    cv.rect(9, 29, 22, 30, hx("8B1A14"))
    save(cv, name)


def misc():
    cv = Cv(S, S)
    cv.rect(7, 5, 24, 27, hx("6B4423"))
    cv.rect(8, 6, 23, 26, hx("8B5A2B"))
    cv.rect(9, 7, 22, 25, hx("F0E0C0"))
    for y in range(9, 24, 3):
        cv.line(11, y, 20, y, hx("8B5A2B"))
    cv.rect(7, 5, 10, 27, hx("5A3A22"))
    cv.rect(11, 9, 20, 12, hx("B22A20"))
    cv.px(12, 10, hx("E86A5A"))
    cv.line(13, 14, 18, 14, hx("C0392B"))
    cv.rect(20, 20, 23, 26, hx("D9453A"))
    save(cv, "quest_ledger")

    cv = Cv(S, S)
    cv.rect(12, 2, 19, 4, GOLD_DARK)
    cv.disc(16, 16, 9, hx("8B1A14"))
    cv.disc(16, 15, 8, hx("C8402F"))
    for i in range(5):
        cv.line(9 + i * 3, 9, 9 + i * 3, 22, hx("A82C24") if i % 2 else hx("E8604A"))
    cv.disc(16, 15, 3, hx("FFE9A8"))
    cv.rect(11, 24, 21, 25, GOLD_TRIM)
    cv.line(14, 26, 16, 30, GOLD_TRIM)
    cv.line(19, 26, 17, 30, GOLD_TRIM)
    save(cv, "festival_lantern")


if __name__ == "__main__":
    talisman("wind_talisman", "swirl", hx("7CC8F0"))
    talisman("stealth_talisman", "cloud", hx("B0B0C0"))
    talisman("healing_talisman", "life", hx("8FD07A"))
    talisman("fire_talisman", "flame", hx("F0803A"))
    talisman("thunder_talisman", "bolt", hx("A44FE0"))
    talisman("return_talisman", "return", hx("4E9AE0"))
    misc()
    print("talismans + misc done:", len(os.listdir(OUT)))
