"""王朝物品贴图 B：文书 / 食物 / 丹药 / 药水。"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/item")
os.makedirs(OUT, exist_ok=True)
S = 32
INK = (28, 20, 16, 255)
PAPER = ramp(hx("EDDFBC"), 5)
YELLOW_PAPER = ramp(hx("F0D66A"), 5)


def save(cv, name):
    cv.outline(INK)
    cv.save(os.path.join(OUT, name + ".png"))


# ---------------------------------------------------------------- 文书
def talisman(name="talisman_paper"):
    cv = Cv(S, S)
    cv.rect(7, 3, 24, 28, YELLOW_PAPER[3])
    cv.rect(8, 4, 23, 27, YELLOW_PAPER[1])
    cv.rect(9, 5, 22, 9, YELLOW_PAPER[0])
    for y in range(11, 25, 3):                        # 朱砂符文 / vermilion glyph strokes
        cv.line(11, y, 20, y, hx("C0392B"))
        cv.px(11 + (y % 4), y - 1, hx("8B1A1A"))
    cv.rect(11, 12, 13, 14, hx("C0392B"))
    cv.rect(18, 20, 20, 22, hx("C0392B"))
    cv.line(10, 6, 21, 6, hx("E8C86A"))
    save(cv, name)


def official_seal():
    cv = Cv(S, S)
    cv.rect(6, 6, 25, 25, hx("8B1A1A"))
    cv.rect(7, 7, 24, 24, hx("B22A20"))
    cv.frame(9, 9, 22, 22, hx("C0392B"))
    cv.rect(11, 11, 20, 20, hx("D9453A"))
    for gx, gy in ((12, 12), (18, 12), (12, 18), (18, 18)):     # 印纹 / stamped marks
        cv.rect(gx, gy, gx + 1, gy + 1, hx("7A1A14"))
    cv.px(13, 13, hx("F0A090"))
    save(cv, "official_seal")


def jade_seal():
    cv = Cv(S, S)
    cv.disc(15.5, 9, 5, GOLD[1])                      # 龙钮 / dragon knob
    cv.disc(15.5, 9, 3, GOLD[0])
    cv.px(14, 8, lighten(GOLD[0], 0.6))
    cv.px(17, 10, GOLD[3])
    cv.rect(8, 13, 23, 26, JADE[2])                   # 印身 / seal body
    cv.rect(9, 14, 22, 25, JADE[1])
    cv.rect(10, 15, 21, 19, JADE[0])
    cv.rect(11, 22, 20, 22, JADE[3])
    cv.line(10, 23, 21, 23, hx("8B1A1A"))             # 朱印 / red ink face
    cv.rect(12, 24, 19, 25, hx("A82C24"))
    cv.px(12, 16, JADE_LIGHT)
    save(cv, "jade_seal")


def edict():
    cv = Cv(S, S)
    cv.rect(6, 8, 26, 24, PAPER[3])                   # 卷轴 / scroll
    cv.rect(7, 9, 25, 23, PAPER[1])
    cv.rect(8, 10, 24, 14, PAPER[0])
    for y in range(16, 22, 2):
        cv.line(10, y, 22, y, PAPER[3])
    cv.rect(4, 6, 8, 26, hx("8B1A1A"))                # 卷轴两端 / rods
    cv.rect(24, 6, 28, 26, hx("8B1A1A"))
    cv.rect(4, 6, 8, 7, hx("B02A22"))
    cv.rect(24, 6, 28, 7, hx("B02A22"))
    cv.rect(14, 18, 18, 22, hx("C0392B"))             # 朱印 / seal
    cv.px(15, 19, hx("F0A090"))
    save(cv, "edict")


def tiger_tally():
    cv = Cv(S, S)
    cv.poly([(8, 24), (10, 12), (15, 8), (21, 12), (23, 24)], BRONZE[3])
    cv.poly([(9, 23), (11, 13), (15, 10), (20, 13), (22, 23)], BRONZE[1])
    cv.poly([(11, 20), (13, 14), (15, 12), (18, 14), (20, 20)], BRONZE[0])
    cv.line(15, 12, 15, 22, darken(BRONZE[3], 0.35))  # 虎纹 / stripes
    cv.line(12, 16, 18, 16, darken(BRONZE[3], 0.3))
    cv.line(12, 19, 18, 19, darken(BRONZE[3], 0.3))
    cv.px(14, 13, lighten(BRONZE[0], 0.6))
    cv.rect(9, 24, 22, 26, BRONZE[2])
    save(cv, "tiger_tally")


def exam_paper():
    cv = Cv(S, S)
    cv.rect(6, 4, 25, 27, PAPER[3])
    cv.rect(7, 5, 24, 26, PAPER[0])
    cv.rect(7, 5, 24, 10, PAPER[1])
    for y in range(12, 26, 2):                        # 米字格 / grid
        cv.line(9, y, 22, y, PAPER[3])
    for x in range(11, 23, 4):
        cv.line(x, 11, x, 26, mix(PAPER[3], hx("C0392B"), 0.25))
    cv.line(9, 11, 9, 26, mix(PAPER[3], hx("C0392B"), 0.3))
    cv.rect(13, 7, 18, 9, hx("3A2414"))
    save(cv, "exam_paper")


def dynasty_guide():
    cv = Cv(S, S)
    cv.rect(6, 4, 25, 27, hx("7A1A14"))               # 书壳 / cover
    cv.rect(7, 5, 24, 26, hx("A82C24"))
    cv.rect(8, 6, 23, 25, hx("C0392B"))
    cv.rect(6, 4, 8, 27, hx("5A1210"))                # 书脊 / spine
    cv.frame(10, 8, 21, 22, GOLD_TRIM)                # 金框 / gold frame
    cv.rect(12, 11, 19, 11, GOLD[0])
    cv.rect(12, 14, 19, 14, GOLD[0])
    cv.rect(12, 17, 17, 17, GOLD[0])
    cv.px(13, 9, lighten(GOLD[0], 0.5))
    cv.rect(23, 6, 25, 25, hx("D9C08B"))              # 书页 / pages
    save(cv, "dynasty_guide")


if __name__ == "__main__":
    talisman()
    official_seal()
    jade_seal()
    edict()
    tiger_tally()
    exam_paper()
    dynasty_guide()
    print("documents done")
