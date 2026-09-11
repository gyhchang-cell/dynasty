"""王朝物品贴图 D：食物。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32


def mooncake():
    cv = Cv(S, S)
    cv.disc(15.5, 17, 11, hx("B98A4A"))
    cv.disc(15.5, 17, 10, hx("D9A85E"))
    cv.disc(15.5, 16, 9, hx("E8C07A"))
    cv.ring(15.5, 16, 8, hx("A87A38"))
    for a in range(0, 360, 45):
        rad = math.radians(a)
        cv.px(int(15.5 + math.cos(rad) * 6), int(16 + math.sin(rad) * 6), hx("8B5A20"))
    cv.disc(15.5, 16, 4, hx("A87A38"))
    cv.rect(13, 14, 18, 18, hx("C0392B"))
    cv.px(13, 12, hx("F0DCA0"))
    cv.px(14, 12, hx("F0DCA0"))
    save(cv, "mooncake")


def dumpling():
    cv = Cv(S, S)
    cv.disc(15.5, 18, 10, hx("E8D9A8"))
    cv.disc(15.5, 17, 9, hx("F5EBC8"))
    for i in range(5):
        x = 8 + i * 4
        cv.line(x, 12, x + 2, 17, hx("D9C99A"))
        cv.px(x, 11, hx("C9B986"))
    cv.line(7, 20, 24, 20, hx("D9C99A"))
    cv.px(12, 15, (255, 255, 255, 220))
    save(cv, "dumpling")


def tea():
    cv = Cv(S, S)
    cv.disc(15.5, 20, 9, hx("C8C8C8"))
    cv.disc(15.5, 19, 8, hx("EEEEEE"))
    cv.rect(6, 16, 25, 18, hx("D8D8D8"))
    cv.disc(15.5, 16, 6, hx("6B4423"))
    cv.disc(15.5, 16, 5, hx("8B5A2B"))
    cv.disc(14, 15, 2, hx("B07A3C"))
    cv.ring(15.5, 16, 6, hx("5A3A1E"))
    cv.rect(23, 17, 27, 22, hx("E8E8E8"))
    for i in range(3):
        cv.px(12 + i * 3, 9 - (i % 2), (235, 235, 235, 150))
        cv.px(12 + i * 3, 7 - (i % 2), (235, 235, 235, 100))
    save(cv, "tea")


def candied_hawthorn():
    cv = Cv(S, S)
    cv.line(15, 29, 15, 5, hx("8B5A2B"))
    for y in (10, 17, 24):
        cv.disc(15.5, y, 5, hx("8B1A14"))
        cv.disc(15.5, y, 4, hx("C6271C"))
        cv.disc(14, y - 1, 2, hx("E8663A"))
        cv.px(14, y - 2, (255, 200, 180, 235))
    cv.px(15, 4, hx("4E7A4A"))
    cv.px(16, 4, hx("6B9B5A"))
    save(cv, "candied_hawthorn")


def dragon_beard_candy():
    cv = Cv(S, S)
    for i in range(7):
        x0 = 7 + i
        cv.line(x0, 6, x0 + 3, 26, hx("E8C86A") if i % 2 else hx("F5DEA0"))
    for x in range(8, 24, 3):
        cv.px(x, 8, hx("FFF3C8"))
    cv.rect(6, 24, 26, 27, hx("D9B45A"))
    cv.rect(7, 25, 25, 26, hx("F0DC9A"))
    for x in range(8, 25, 3):
        cv.px(x, 25, hx("FFF6D8"))
    save(cv, "dragon_beard_candy")


def hotpot():
    cv = Cv(S, S)
    cv.rect(4, 14, 27, 24, hx("A85F28"))
    cv.rect(5, 15, 26, 23, hx("C98A3C"))
    cv.rect(6, 16, 25, 19, hx("E0A860"))
    cv.rect(3, 14, 6, 17, hx("8B4A20"))
    cv.rect(25, 14, 28, 17, hx("8B4A20"))
    cv.disc(15.5, 18, 7, hx("8B1A14"))
    cv.disc(15.5, 18, 6, hx("C0392B"))
    cv.disc(13, 16, 3, hx("E8663A"))
    for x in (10, 14, 18, 22):
        cv.px(x, 16, hx("4E7A4A"))
        cv.px(x, 15, hx("D9C08B"))
    cv.px(16, 19, hx("FFD27F"))
    cv.rect(10, 25, 21, 26, hx("5A3A22"))
    cv.px(12, 27, hx("F0803A"))
    cv.px(15, 28, hx("FFB060"))
    cv.px(18, 27, hx("F0803A"))
    save(cv, "hotpot")


def wine():
    cv = Cv(S, S)
    cv.poly([(11, 8), (20, 8), (22, 14), (22, 24), (20, 27), (11, 27), (9, 24), (9, 14)], hx("5A3A22"))
    cv.poly([(12, 9), (19, 9), (21, 14), (21, 23), (19, 26), (12, 26), (10, 23), (10, 14)], hx("8B6440"))
    cv.rect(12, 12, 19, 20, hx("A87A4A"))
    cv.rect(10, 6, 21, 8, hx("B22A20"))
    cv.rect(10, 5, 21, 6, hx("D9453A"))
    cv.line(15, 6, 15, 8, hx("8B1A1A"))
    cv.px(13, 11, hx("C9A87A"))
    cv.rect(13, 21, 18, 23, hx("D9C08B"))
    cv.px(14, 22, hx("8B1A1A"))
    cv.px(17, 22, hx("8B1A1A"))
    save(cv, "wine")


def immortal_peach():
    cv = Cv(S, S)
    cv.disc(14, 18, 9, hx("E8806A"))
    cv.disc(19, 19, 8, hx("F0A08A"))
    cv.disc(14, 17, 7, hx("F5B49E"))
    cv.disc(12, 15, 4, hx("FFD0C0"))
    cv.px(11, 14, (255, 245, 240, 240))
    cv.line(15, 10, 12, 5, hx("6B4423"))
    cv.poly([(18, 8), (25, 4), (26, 9), (20, 11)], hx("4E7A4A"))
    cv.line(19, 8, 25, 7, hx("6B9B5A"))
    save(cv, "immortal_peach")


if __name__ == "__main__":
    mooncake(); dumpling(); tea(); candied_hawthorn()
    dragon_beard_candy(); hotpot(); wine(); immortal_peach()
    print("foods done:", len(os.listdir(OUT)))
