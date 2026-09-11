"""新武器贴图（32x32）：唐刀 / 环首刀 / 长枪 / 玉笛 / 巨阙 / 破军斧 / 龙吟弓。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

S = 32


def blade(cv, dark, light, edge, x0, y0, x1, y1, thick=2):
    """斜向刀身 / diagonal blade"""
    cv.line(x0, y0, x1, y1, dark)
    for i in range(1, thick + 1):
        cv.line(x0 - i, y0 + i, x1 - i, y1 + i, light)
    cv.line(x0 - thick, y0 + thick, x1 - thick, y1 + thick, edge)


def hilt(cv, x, y, guard=True):
    cv.rect(x - 1, y, x + 2, y + 6, hx("3A2414"))
    for i in range(0, 6, 2):
        cv.px(x, y + i, hx("6B4423"))
    if guard:
        cv.rect(x - 3, y - 1, x + 4, y + 1, GOLD_TRIM)


def weapons():
    # 唐刀 / Tang Dao：细长弯刀
    cv = Cv(S, S)
    blade(cv, hx("B9C4CC"), hx("E8F0F5"), hx("FFFFFF"), 24, 5, 9, 20)
    cv.px(25, 4, hx("8B99A5"))
    hilt(cv, 8, 20)
    cv.line(7, 27, 9, 24, hx("B22A20"))          # 刀穗 / tassel
    save(cv, "tang_dao")

    # 环首刀 / Huan Shou Dao：直刀 + 环首
    cv = Cv(S, S)
    blade(cv, hx("A8B4BD"), hx("DCE6EC"), hx("FFFFFF"), 24, 6, 10, 20)
    cv.ring(9, 23, 3, GOLD_TRIM)
    cv.rect(11, 18, 14, 22, hx("3A2414"))
    save(cv, "huan_shou_dao")

    # 长枪 / Chang Qiang：长杆 + 枪头
    cv = Cv(S, S)
    cv.line(6, 28, 24, 8, hx("8B5A2B"))
    cv.line(7, 28, 25, 8, hx("A87A3C"))
    for i in range(0, 20, 4):
        cv.px(6 + i, 28 - i, hx("6B4423"))
    cv.poly([(23, 9), (28, 3), (29, 7), (25, 12)], hx("DCE6EC"))
    cv.line(25, 12, 27, 6, hx("FFFFFF"))
    cv.rect(5, 28, 8, 30, hx("B22A20"))          # 红缨 / red tassel
    save(cv, "chang_qiang")

    # 玉笛 / Yu Di
    cv = Cv(S, S)
    cv.rect(4, 13, 28, 18, hx("8FD0A8"))
    cv.rect(5, 14, 27, 17, hx("BCE8CC"))
    cv.rect(4, 14, 28, 15, hx("E4F7EC"))
    for x in (8, 13, 18, 23):
        cv.px(x, 15, hx("2A4A38"))
    cv.px(26, 13, hx("6FAE86"))
    cv.line(6, 18, 26, 18, hx("6FAE86"))
    cv.rect(2, 14, 4, 17, GOLD_TRIM)             # 笛口 / mouthpiece
    save(cv, "yu_di")

    # 巨阙重剑 / Juque
    cv = Cv(S, S)
    cv.poly([(22, 4), (27, 9), (12, 24), (8, 20)], hx("B9C4CC"))
    cv.poly([(21, 5), (25, 9), (11, 23), (9, 20)], hx("E0EAF0"))
    cv.line(23, 6, 10, 21, hx("FFFFFF"))
    cv.rect(6, 19, 13, 24, hx("3A2414"))
    cv.rect(4, 23, 15, 26, GOLD_TRIM)
    cv.rect(8, 25, 11, 30, hx("6B4423"))
    save(cv, "juque_sword")

    # 破军战斧 / Po Jun Axe
    cv = Cv(S, S)
    cv.line(9, 29, 21, 8, hx("8B5A2B"))
    cv.line(10, 29, 22, 8, hx("A87A3C"))
    cv.poly([(18, 6), (28, 10), (27, 20), (19, 17)], hx("C9D2D9"))
    cv.poly([(20, 8), (26, 11), (25, 18), (21, 16)], hx("E8F0F5"))
    cv.line(27, 10, 27, 19, hx("FFFFFF"))
    cv.poly([(14, 8), (8, 12), (9, 18), (15, 16)], hx("A8B4BD"))
    cv.rect(19, 14, 23, 17, hx("B22A20"))
    save(cv, "pojun_axe")

    # 龙吟弓 / Dragon Bow
    cv = Cv(S, S)
    for a in range(200, 341, 10):
        rad = math.radians(a)
        cv.px(int(16 + math.cos(rad) * 11), int(16 + math.sin(rad) * 12), hx("8B1A14"))
        cv.px(int(16 + math.cos(rad) * 12), int(16 + math.sin(rad) * 13), hx("C8402F"))
    cv.line(4, 8, 4, 24, hx("E8E8E8"))            # 弓弦 / string
    cv.rect(15, 15, 17, 18, GOLD_TRIM)
    cv.px(16, 16, hx("FFF0B0"))
    cv.poly([(28, 13), (31, 16), (28, 19)], GOLD_TRIM)   # 龙首 / dragon head
    cv.px(29, 15, hx("2A2A34"))
    save(cv, "dragon_bow")


if __name__ == "__main__":
    weapons()
    print("weapon textures done")
