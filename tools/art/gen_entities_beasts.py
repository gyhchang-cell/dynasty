"""神兽贴图（128x128）：麒麟 / 九尾狐（四足）、凤凰（飞行）。"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from entity_kit import box, INK

OUT = os.path.join(os.path.dirname(__file__), "out/entity")
QILIN = ramp(hx("3FA86B"), 6)
FOX = ramp(hx("E08A3C"), 6)
PHOENIX = ramp(hx("E04A1E"), 6)
GOLD_H = ramp(hx("E8C24A"), 5)


def beast_skin(name, body, belly_r, hoof, horn, eye, tail_tuft=None, scales=False):
    belly = belly_r[1] if isinstance(belly_r, list) else belly_r
    cv = Cv(128, 128)
    # 躯干 12x10x18 @ (0,0)
    def body_side(c, x, y, w, h):
        c.rect(x, y + h - 3, x + w - 1, y + h - 1, belly)
        if scales:
            for i in range(0, w, 3):
                for j in range(0, h - 3, 3):
                    c.px(x + i, y + j, darken(body[2], 0.25))
    box(cv, 0, 0, 12, 10, 18, {"main": body[1]})
    cv.rect(18, 25, 29, 27, belly)                      # 腹部 / underside
    if scales:
        for x in range(18, 30, 3):
            for y in range(18, 28, 3):
                cv.px(x, y, darken(body[2], 0.3))
                cv.px(x + 1, y + 1, lighten(body[0], 0.2))
    # 头 8x8x8 @ (0,30)
    box(cv, 0, 30, 8, 8, 8, {"main": body[0], "front": lighten(body[1], 0.06)})
    cv.rect(8, 38, 15, 45, body[1])
    cv.rect(9, 40, 10, 41, eye)                         # 目 / eyes
    cv.rect(13, 40, 14, 41, eye)
    cv.px(9, 40, (255, 255, 255, 220))
    cv.px(13, 40, (255, 255, 255, 220))
    cv.rect(10, 43, 13, 43, darken(body[3], 0.4))
    cv.rect(11, 44, 12, 44, (40, 20, 20, 255))
    # 角 2x5x2 @ (32,30)（左右共用）
    box(cv, 32, 30, 2, 5, 2, {"main": horn[1]})
    # 尾 4x4x12 @ (44,30)
    box(cv, 44, 30, 4, 4, 12, {"main": body[1]})
    cv.rect(56, 42, 59, 45, tail_tuft or body[0])
    cv.rect(56, 42, 59, 43, lighten(tail_tuft or body[0], 0.25))
    # 四腿 4x9x4 @ (0,48)
    box(cv, 0, 48, 4, 9, 4, {"main": body[1]})
    cv.rect(4, 53, 7, 56, darken(body[2], 0.2))
    cv.rect(4, 54, 7, 56, hoof[1])                      # 蹄 / hooves
    cv.rect(4, 56, 7, 56, darken(hoof[3], 0.3))
    cv.outline(INK)
    cv.save(os.path.join(OUT, name + ".png"))


def phoenix_skin():
    cv = Cv(128, 128)
    # 身体 8x8x14 @ (0,0)
    box(cv, 0, 0, 8, 8, 14, {"main": PHOENIX[1]})
    cv.rect(14, 18, 21, 21, GOLD_H[1])                  # 胸羽 / chest feathers
    cv.rect(15, 19, 20, 20, GOLD_H[0])
    cv.rect(15, 13, 20, 15, darken(PHOENIX[2], 0.15))
    # 头 6x6x6 @ (0,24)
    box(cv, 0, 24, 6, 6, 6, {"main": PHOENIX[0], "front": lighten(PHOENIX[1], 0.08)})
    cv.rect(6, 30, 11, 35, PHOENIX[1])
    cv.rect(6, 31, 7, 32, (255, 230, 140, 255))         # 目 / eyes
    cv.rect(10, 31, 11, 32, (255, 230, 140, 255))
    cv.rect(8, 34, 9, 35, GOLD_H[2])                    # 喙 / beak
    # 凤冠 2x4x2 @ (24,24)
    box(cv, 24, 24, 2, 4, 2, {"main": GOLD_H[1]})
    # 双翼 18x2x12 @ (32,0)
    box(cv, 32, 0, 18, 2, 12, {"main": PHOENIX[1]})
    for i in range(0, 18, 3):                           # 飞羽 / flight feathers
        for j in range(4, 12, 2):
            cv.px(44 + i, 12 + j, PHOENIX[0] if (i // 3) % 2 else GOLD_H[1])
            cv.px(44 + i + 1, 12 + j, darken(PHOENIX[3], 0.1))
    # 尾羽 6x2x16 @ (0,40)
    box(cv, 0, 40, 6, 2, 16, {"main": PHOENIX[2]})
    for x in range(16, 22, 2):
        cv.rect(x, 56, x, 63, GOLD_H[1])
    cv.rect(16, 56, 21, 57, lighten(PHOENIX[0], 0.25))
    cv.outline(INK)
    cv.save(os.path.join(OUT, "phoenix.png"))


if __name__ == "__main__":
    beast_skin("qilin", QILIN, ramp(hx("D8E8C0"), 5), GOLD_H, ramp(hx("E8E0C0"), 4),
               (30, 60, 40, 255), scales=True)
    beast_skin("nine_tailed_fox", FOX, ramp(hx("F5EDE0"), 5), ramp(hx("3A2A22"), 4),
               ramp(hx("4A3A2E"), 4), (60, 40, 30, 255), tail_tuft=ramp(hx("F5EDE0"), 4)[0])
    phoenix_skin()
    print("beasts done:", len(os.listdir(OUT)))
