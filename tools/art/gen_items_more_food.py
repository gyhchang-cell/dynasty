"""新增物品贴图（32x32）：美食 / 工艺材料 / 符箓 / 任务书与节令灯。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save, YELLOW_PAPER, PAPER

OUT = os.path.join(os.path.dirname(__file__), "out/item")


def zongzi():
    cv = Cv(S := 32, S)
    cv.poly([(16, 4), (27, 16), (16, 28), (5, 16)], hx("3F7A3A"))
    cv.poly([(16, 6), (25, 16), (16, 26), (7, 16)], hx("4E9A46"))
    cv.poly([(16, 8), (22, 16), (16, 23), (10, 16)], hx("5FAF52"))
    for y in range(8, 25, 3):
        cv.line(9, y, 23, y - 6, hx("D9C08B"))
    cv.line(16, 4, 16, 28, hx("2F5A2C"))
    cv.px(13, 12, hx("8FD07A"))
    save(cv, "zongzi")


def tangyuan():
    cv = Cv(32, 32)
    cv.disc(16, 20, 11, hx("B08A5A"))
    cv.disc(16, 19, 10, hx("E0E0E0"))
    for x, y in ((11, 17), (16, 15), (21, 17), (13, 21), (19, 21)):
        cv.disc(x, y, 4, hx("F5F5F5"))
        cv.disc(x - 1, y - 1, 2, (255, 255, 255, 255))
    cv.disc(16, 15, 2, hx("F0E8D0"))
    save(cv, "tangyuan")


def niangao():
    cv = Cv(32, 32)
    for i, y in enumerate((20, 15, 10)):
        cv.rect(7 + i, y, 24 - i, y + 4, hx("F0E0B0"))
        cv.rect(8 + i, y, 23 - i, y + 2, hx("FFF0CC"))
        cv.line(7 + i, y + 4, 24 - i, y + 4, hx("D9C08B"))
    cv.rect(11, 5, 20, 8, hx("F5E8C0"))
    cv.px(13, 6, hx("FFFBF0"))
    cv.px(18, 19, hx("C9A24A"))
    cv.px(12, 14, hx("C9A24A"))
    save(cv, "niangao")


def osmanthus_cake():
    cv = Cv(32, 32)
    cv.disc(16, 17, 11, hx("C9A24A"))
    cv.disc(16, 16, 10, hx("E8C86A"))
    cv.disc(14, 14, 6, hx("F5DEA0"))
    cv.ring(16, 16, 7, hx("B08A3A"))
    for a in range(0, 360, 60):
        rad = math.radians(a)
        cv.px(int(16 + math.cos(rad) * 5), int(16 + math.sin(rad) * 5), hx("F5B041"))
    cv.disc(16, 16, 4, hx("F0B45A"))
    cv.px(13, 13, (255, 255, 255, 230))
    save(cv, "osmanthus_cake")


def cured_meat():
    cv = Cv(32, 32)
    cv.line(6, 6, 26, 6, hx("8B5A2B"))
    for x in (9, 16, 23):
        cv.rect(x, 6, x + 4, 26, hx("A83232"))
        cv.rect(x, 6, x + 4, 24, hx("C4463C"))
        cv.line(x + 1, 9, x + 1, 24, hx("8B1A14"))
        cv.line(x + 3, 9, x + 3, 24, hx("8B1A14"))
        cv.px(x + 1, 12, hx("E8665A"))
        cv.px(x + 2, 8, hx("6B4423"))
    save(cv, "cured_meat")


def roast_duck():
    cv = Cv(32, 32)
    cv.disc(16, 18, 9, hx("8B4A20"))
    cv.disc(16, 17, 8, hx("B4662A"))
    cv.disc(14, 15, 5, hx("D08A3A"))
    cv.poly([(8, 14), (5, 10), (10, 12)], hx("B4662A"))     # 翅 / wing
    cv.poly([(24, 14), (27, 10), (22, 12)], hx("B4662A"))
    cv.poly([(13, 8), (19, 8), (16, 4)], hx("D9A85E"))      # 腿 / leg
    cv.px(14, 14, hx("F0B060"))
    cv.px(18, 20, hx("7A3A18"))
    cv.line(10, 22, 22, 22, hx("7A3A18"))
    cv.rect(10, 24, 22, 26, hx("E0D8C0"))                    # 盘 / plate
    save(cv, "roast_duck")


def longevity_noodles():
    cv = Cv(32, 32)
    cv.disc(16, 19, 11, hx("C8C8C8"))
    cv.disc(16, 18, 10, hx("F0F0F0"))
    cv.disc(16, 17, 8, hx("F5E8C0"))
    for i in range(5):                                       # 面条 / noodles
        y = 13 + i * 2
        cv.line(9, y, 23, y, hx("F5DEA0") if i % 2 else hx("E8C86A"))
    cv.disc(16, 15, 3, hx("F5F5F5"))                         # 蛋 / egg
    cv.disc(16, 14, 2, hx("FFE08A"))
    cv.rect(16, 4, 17, 13, hx("8B5A2B"))                     # 筷 / chopsticks
    cv.rect(20, 4, 21, 13, hx("8B5A2B"))
    cv.px(12, 12, hx("4E7A4A"))
    save(cv, "longevity_noodles")


def baijiu():
    cv = Cv(32, 32)
    cv.rect(11, 8, 20, 27, hx("E8E8E8"))
    cv.rect(12, 9, 19, 26, hx("F8F8F8"))
    cv.rect(13, 12, 18, 22, hx("4E6FA8"))                    # 青花 / blue pattern
    cv.rect(14, 13, 17, 14, hx("E8E8E8"))
    cv.line(14, 17, 17, 17, hx("E8E8E8"))
    cv.px(15, 20, hx("E8E8E8"))
    cv.rect(12, 5, 19, 8, hx("B22A20"))                      # 红盖
    cv.rect(12, 4, 19, 5, hx("D9453A"))
    cv.px(13, 10, (255, 255, 255, 220))
    save(cv, "baijiu")


if __name__ == "__main__":
    zongzi(); tangyuan(); niangao(); osmanthus_cake()
    cured_meat(); roast_duck(); longevity_noodles(); baijiu()
    print("fine foods done")
