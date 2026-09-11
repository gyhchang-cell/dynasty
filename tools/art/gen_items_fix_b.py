"""物品贴图修正 B：糖丝、茶、虎符、火锅。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32


def dragon_beard_candy():
    cv = Cv(S, S)
    for i in range(11):
        x = 9 + int((i / 10.0) * 12)
        sway = math.sin(i * 0.9) * 2
        col = hx("F5DEA0") if i % 2 else hx("E8C86A")
        for y in range(6, 23):
            cv.px(int(x + math.sin(y * 0.5 + i) * 0.8 + sway * 0.4), y, col)
    for i in range(6):
        cv.px(10 + i * 2, 4 + (i % 2), hx("FFF6D8"))
        cv.px(11 + i * 2, 3 + (i % 2), hx("FFF6D8"))
    cv.rect(8, 21, 24, 27, hx("D9B45A"))
    cv.rect(9, 22, 23, 26, hx("F0DC9A"))
    cv.line(9, 24, 23, 24, hx("C9A24A"))
    for x in range(10, 23, 3):
        cv.px(x, 23, hx("FFF6D8"))
    save(cv, "dragon_beard_candy")


def tea():
    cv = Cv(S, S)
    cv.disc(15.5, 20, 10, hx("8A6A4A"))
    cv.disc(15.5, 19, 9, hx("B08A5A"))
    cv.disc(15.5, 18, 8, hx("D8D8D8"))
    cv.disc(15.5, 17, 7, hx("F2F2F2"))
    cv.ring(15.5, 17, 7, hx("9A9A9A"))
    cv.disc(15.5, 16, 5, hx("6B4423"))
    cv.disc(15.5, 16, 4, hx("8B5A2B"))
    cv.disc(14, 15, 2, hx("B07A3C"))
    cv.px(14, 15, hx("D9A85E"))
    for i in range(3):
        cv.px(12 + i * 3, 9 - (i % 2), (235, 235, 235, 150))
        cv.px(12 + i * 3, 7 - (i % 2), (235, 235, 235, 105))
    cv.px(11, 15, (255, 255, 255, 200))
    save(cv, "tea")


def tiger_tally():
    cv = Cv(S, S)
    cv.disc(15.5, 17, 10, BRONZE[3])
    cv.disc(15.5, 16, 9, BRONZE[1])
    cv.poly([(8, 13), (11, 8), (14, 12)], BRONZE[2])
    cv.poly([(17, 12), (20, 8), (23, 13)], BRONZE[2])
    cv.poly([(9, 24), (15, 27), (22, 24), (21, 26), (15, 29), (10, 26)], BRONZE[2])
    cv.disc(12, 15, 2, darken(BRONZE[3], 0.45))
    cv.disc(19, 15, 2, darken(BRONZE[3], 0.45))
    cv.rect(13, 18, 18, 19, darken(BRONZE[3], 0.35))
    cv.line(12, 20, 19, 20, darken(BRONZE[3], 0.3))
    cv.line(11, 22, 20, 22, darken(BRONZE[3], 0.3))
    cv.line(13, 6, 18, 6, darken(BRONZE[3], 0.35))
    cv.px(14, 11, lighten(BRONZE[0], 0.6))
    cv.px(11, 9, lighten(BRONZE[0], 0.5))
    save(cv, "tiger_tally")


def hotpot():
    cv = Cv(S, S)
    cv.disc(15.5, 19, 11, hx("8B4A20"))
    cv.disc(15.5, 18, 10, hx("C98A3C"))
    cv.disc(15.5, 17, 9, hx("E0A860"))
    cv.rect(3, 15, 7, 18, hx("A85F28"))
    cv.rect(24, 15, 28, 18, hx("A85F28"))
    cv.px(4, 16, hx("D9A860"))
    cv.px(26, 16, hx("D9A860"))
    cv.disc(15.5, 18, 7, hx("8B1A14"))
    cv.disc(15.5, 18, 6, hx("C0392B"))
    for x, y in ((11, 16), (15, 15), (19, 16), (13, 20), (18, 20)):
        cv.px(x, y, hx("4E7A4A"))
        cv.px(x + 1, y, hx("6B9B5A"))
    cv.px(16, 17, hx("FFD27F"))
    cv.rect(11, 27, 20, 28, hx("5A3A22"))
    cv.px(13, 29, hx("F0803A"))
    cv.px(16, 30, hx("FFB060"))
    cv.px(19, 29, hx("F0803A"))
    save(cv, "hotpot")


if __name__ == "__main__":
    dragon_beard_candy(); tea(); tiger_tally(); hotpot()
    print("item fixes B applied")
