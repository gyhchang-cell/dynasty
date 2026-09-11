"""状态效果图标（18x18，原版尺寸）。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/mob_effect")
os.makedirs(OUT, exist_ok=True)
S = 18
INK = (16, 12, 10, 255)


def save(cv, name):
    cv.outline(INK)
    cv.save(os.path.join(OUT, name + ".png"))


def dragon_might():
    cv = Cv(S, S)
    for i, x in enumerate((3, 7, 11)):                 # 三爪 / three talons
        cv.line(x + 2, 3, x, 13, hx("8A6A16"))
        cv.line(x + 1, 3, x - 1, 13, GOLD[0])
        cv.px(x, 6, lighten(GOLD[0], 0.5))
        cv.line(x - 1, 13, x + 2, 14, GOLD[2])
    cv.disc(9, 13, 3, GOLD[1])                         # 掌 / palm
    cv.disc(9, 13, 2, GOLD[0])
    cv.px(8, 12, lighten(GOLD[0], 0.6))
    save(cv, "dragon_might")


def iron_wall():
    cv = Cv(S, S)
    cv.poly([(9, 1), (16, 4), (16, 10), (9, 16), (2, 10), (2, 4)], hx("8A2F26"))
    cv.poly([(9, 2), (15, 5), (15, 9), (9, 15), (3, 9), (3, 5)], hx("B8433A"))
    for y in range(5, 14, 3):                          # 砖纹 / brick lines
        cv.line(4, y, 14, y, hx("8A2F26"))
    cv.line(9, 3, 9, 14, hx("8A2F26"))
    cv.px(6, 4, hx("E8907A"))
    save(cv, "iron_wall")


def swift_wind():
    cv = Cv(S, S)
    for i, y in enumerate((5, 9, 13)):                 # 风纹 / wind streaks
        cv.line(2, y, 14 - i, y, hx("BFE9FF"))
        cv.line(4, y + 1, 15 - i, y + 1, hx("7CC8F0"))
    cv.poly([(11, 2), (17, 9), (11, 10)], hx("E8F6FF"))   # 飞羽 / wing
    cv.poly([(12, 4), (15, 9), (12, 9)], hx("FFFFFF"))
    cv.px(12, 3, (255, 255, 255, 240))
    save(cv, "swift_wind")


def intimidation():
    cv = Cv(S, S)
    cv.disc(9, 9, 7, hx("3A2A28"))                     # 铁面 / iron mask
    cv.disc(9, 9, 6, hx("5A3A36"))
    cv.rect(4, 7, 6, 9, hx("C0392B"))                  # 赤目 / red eyes
    cv.rect(11, 7, 13, 9, hx("C0392B"))
    cv.px(5, 8, hx("FF8A6A"))
    cv.px(12, 8, hx("FF8A6A"))
    cv.line(6, 12, 12, 12, hx("2A1A18"))
    for x in (5, 8, 11):
        cv.px(x, 13, hx("2A1A18"))
    cv.px(7, 4, hx("9A8A80"))
    save(cv, "intimidation")


def loyalty():
    cv = Cv(S, S)
    cv.disc(6, 7, 4, hx("8B1A14"))                     # 心 / heart
    cv.disc(12, 7, 4, hx("8B1A14"))
    cv.poly([(2, 8), (16, 8), (9, 16)], hx("8B1A14"))
    cv.disc(6, 6, 3, hx("D9453A"))
    cv.disc(12, 6, 3, hx("D9453A"))
    cv.poly([(3, 8), (15, 8), (9, 15)], hx("D9453A"))
    cv.disc(5, 5, 1, hx("F5A090"))
    cv.px(6, 10, hx("F0E0C0"))
    cv.px(9, 12, hx("F0E0C0"))
    save(cv, "loyalty")


def mandate_of_heaven():
    cv = Cv(S, S)
    cv.poly([(3, 12), (15, 12), (13, 15), (5, 15)], GOLD[3])   # 冠底 / crown base
    cv.poly([(3, 11), (5, 5), (9, 9), (13, 5), (15, 11)], GOLD[1])
    cv.poly([(4, 10), (6, 6), (9, 9), (12, 6), (14, 10)], GOLD[0])
    cv.px(6, 6, lighten(GOLD[0], 0.6))
    cv.px(9, 8, hx("C0392B"))                          # 红宝 / ruby
    cv.px(12, 6, lighten(GOLD[0], 0.6))
    cv.px(9, 13, GOLD_TRIM)
    save(cv, "mandate_of_heaven")


def internal_injury():
    cv = Cv(S, S)
    cv.disc(7, 8, 5, hx("8B3A2A"))
    cv.disc(11, 9, 5, hx("8B3A2A"))
    cv.poly([(3, 9), (15, 9), (9, 16)], hx("8B3A2A"))
    cv.disc(7, 7, 4, hx("B04A34"))
    cv.disc(11, 8, 4, hx("B04A34"))
    cv.poly([(4, 9), (14, 9), (9, 15)], hx("B04A34"))
    for i in range(5):                                 # 裂纹 / cracks
        cv.px(6 + i, 8 + i % 3, hx("3A1A14"))
        cv.px(11 - i, 9 + i % 2, hx("3A1A14"))
    cv.rect(9, 2, 12, 12, hx("E8E2D0"))                # 绷带 / bandage
    cv.rect(9, 2, 12, 4, hx("F5F0E0"))
    cv.line(9, 6, 12, 6, hx("C9C0A8"))
    save(cv, "internal_injury")


if __name__ == "__main__":
    dragon_might(); iron_wall(); swift_wind(); intimidation()
    loyalty(); mandate_of_heaven(); internal_injury()
    print("effects done:", len(os.listdir(OUT)))
