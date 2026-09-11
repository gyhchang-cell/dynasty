"""饰品与说明书贴图（32x32）。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

S = 32


def cord(cv, x0, y0, x1, y1, color=hx("B22A20")):
    cv.line(x0, y0, x1, y1, color)
    cv.line(x0 + 1, y0, x1 + 1, y1, darken(color, 0.2))


def pendants():
    # 玉佩
    cv = Cv(S, S)
    cord(cv, 16, 3, 16, 12)
    cv.disc(16, 18, 9, hx("4E8A6A"))
    cv.disc(16, 18, 8, hx("8FD0A8"))
    cv.disc(14, 16, 4, hx("E4F7EC"))
    cv.ring(16, 18, 5, hx("2A4A38"))
    cv.px(13, 13, (255, 255, 255, 230))
    save(cv, "jade_pendant")

    # 玉璧
    cv = Cv(S, S)
    cv.disc(16, 17, 12, hx("2A4A38"))
    cv.disc(16, 17, 11, hx("6FAE86"))
    cv.disc(16, 17, 7, hx("8FD0A8"))
    for a in range(0, 360, 30):
        rad = math.radians(a)
        cv.px(int(16 + math.cos(rad) * 9), int(17 + math.sin(rad) * 9), hx("E4F7EC"))
    cv.disc(16, 17, 4, (0, 0, 0, 0))
    save(cv, "jade_bi_disc")

    # 金印
    cv = Cv(S, S)
    cv.rect(8, 10, 24, 22, GOLD_DARK)
    cv.rect(9, 11, 23, 21, GOLD_TRIM)
    cv.rect(12, 14, 20, 18, hx("8B1A14"))
    cv.px(15, 16, GOLD_TRIM)
    cv.rect(14, 6, 18, 10, GOLD_TRIM)          # 印钮 / knob
    cv.rect(15, 3, 17, 6, hx("8B1A14"))
    save(cv, "gold_seal_charm")

    # 龙鳞护符
    cv = Cv(S, S)
    cord(cv, 16, 3, 16, 11, hx("4E6FA8"))
    cv.poly([(16, 10), (25, 18), (16, 28), (7, 18)], hx("2E5A3A"))
    cv.poly([(16, 12), (23, 18), (16, 26), (9, 18)], hx("4E8A5A"))
    for i in range(13, 26, 3):
        cv.line(10, i, 22, i - 4, hx("6FAE7A") if i % 2 else hx("2E5A3A"))
    cv.px(13, 15, (255, 255, 255, 200))
    save(cv, "dragon_scale_charm")

    # 凤羽翎
    cv = Cv(S, S)
    cv.line(20, 4, 10, 26, hx("8B1A14"))
    for i in range(0, 22, 2):
        x = 20 - i * 0.45
        y = 4 + i
        cv.line(int(x), int(y), int(x) - 5, int(y) + 3, hx("E8604A"))
    cv.line(20, 4, 10, 26, hx("E8C86A"))
    cv.disc(11, 25, 3, hx("C8402F"))
    save(cv, "phoenix_feather_charm")

    # 麒麟角坠
    cv = Cv(S, S)
    cord(cv, 16, 3, 16, 10, hx("B22A20"))
    cv.poly([(16, 9), (21, 20), (16, 29), (11, 20)], GOLD_TRIM)
    cv.poly([(16, 12), (19, 19), (16, 26), (13, 19)], hx("F5DEA0"))
    cv.px(17, 14, hx("FFFBF0"))
    cv.rect(13, 19, 19, 20, hx("B08A16"))
    save(cv, "qilin_horn_charm")

    # 狐尾坠
    cv = Cv(S, S)
    cord(cv, 16, 3, 16, 9, hx("B22A20"))
    for i in range(0, 5):
        x = 10 + i * 3
        cv.poly([(x, 10 + i), (x + 6, 12 + i), (x + 3, 28 - i), (x - 1, 24 - i)],
                mix(hx("B4652A"), hx("E8C86A"), i / 4.0))
    cv.disc(16, 12, 3, hx("E84A2A"))
    cv.px(15, 11, (255, 255, 255, 220))
    save(cv, "fox_tail_charm")

    # 锦囊
    cv = Cv(S, S)
    cv.disc(16, 19, 9, hx("8B2A5A"))
    cv.disc(16, 19, 8, hx("B8407A"))
    cv.disc(14, 17, 4, hx("D9709E"))
    cv.line(9, 12, 23, 12, GOLD_TRIM)
    cv.line(12, 10, 16, 13, GOLD_TRIM)
    cv.line(20, 10, 16, 13, GOLD_TRIM)
    cv.disc(16, 14, 2, GOLD_TRIM)
    for x in (12, 16, 20):
        cv.px(x, 22, hx("F0D060"))
    save(cv, "silk_pouch")

    # 司南
    cv = Cv(S, S)
    cv.disc(16, 17, 11, BRONZE[3])
    cv.disc(16, 17, 10, BRONZE[1])
    cv.disc(14, 15, 5, BRONZE[0])
    cv.poly([(16, 8), (19, 17), (16, 26), (13, 17)], hx("E8F0F5"))   # 磁勺 / spoon
    cv.ring(16, 17, 7, BRONZE[2])
    cv.px(11, 12, (255, 255, 255, 200))
    save(cv, "south_pointing_compass")


def util():
    # 百宝妆匣
    cv = Cv(S, S)
    cv.rect(5, 12, 26, 26, hx("6B4423"))
    cv.rect(6, 13, 25, 25, hx("8B5A2B"))
    cv.rect(5, 8, 26, 12, hx("7A4E2A"))
    cv.rect(6, 9, 25, 11, hx("A87A3C"))
    cv.rect(14, 10, 18, 16, GOLD_TRIM)          # 锁扣 / clasp
    cv.px(16, 13, hx("4E8A6A"))
    cv.line(7, 20, 24, 20, hx("6B4423"))
    cv.px(9, 17, hx("C9A24A"))
    save(cv, "trinket_box")

    # 王朝说明书
    cv = Cv(S, S)
    cv.rect(6, 4, 25, 28, hx("6B1F1F"))
    cv.rect(7, 5, 24, 27, hx("B22A20"))
    cv.rect(7, 5, 10, 27, hx("8B1A14"))
    cv.rect(11, 8, 22, 12, GOLD_TRIM)
    cv.px(13, 10, hx("4E8A6A"))
    for y in range(15, 26, 3):
        cv.line(12, y, 21, y, hx("F0E0C0"))
    cv.rect(23, 6, 25, 27, hx("F5F0E0"))        # 书页 / pages
    save(cv, "dynasty_manual")


if __name__ == "__main__":
    pendants()
    util()
    print("trinket textures done")
