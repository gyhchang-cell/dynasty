"""麒麟贴图（128x128，按 DetailedBeastModel 的 UV 绘制）。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from entity_kit import box

OUT = os.path.join(os.path.dirname(__file__), "out/entity")
os.makedirs(OUT, exist_ok=True)
S = 128
INK = (16, 12, 10, 255)


def save(cv, name):
    cv.im.save(os.path.join(OUT, name + ".png"))


def scales(cv, x0, y0, w, h, base):
    """鳞片纹 / scale pattern"""
    lo = darken(base, 0.30)
    hi = lighten(base, 0.22)
    for row in range(0, h, 3):
        for col in range((row // 3) % 2 * 2, w, 4):
            cv.line(x0 + col, y0 + row, x0 + col + 2, y0 + row, lo)
            cv.px(x0 + col + 3, y0 + row + 1, hi)
            cv.px(x0 + col + 1, y0 + row + 2, hi)


def qilin():
    cv = Cv(S, S)
    scale = hx("6E9A54")
    belly = hx("CBDCA8")
    mane = hx("C0392B")
    horn = hx("E8C86A")
    hoof = hx("3A2A1A")

    def chest_front(c, x, y):
        scales(c, x + 1, y + 1, 12, 10, scale)
        c.rect(x + 4, y + 6, x + 9, y + 11, belly)

    def chest_top(c, x, y):
        c.rect(x + 4, y + 3, x + 10, y + 12, darken(scale, 0.1))

    box(cv, 0, 0, 14, 12, 16, {"main": scale, "front": scale},
        front_detail=chest_front)
    chest_top(cv, 0 + 16, 0)

    box(cv, 0, 32, 13, 11, 14, {"main": darken(scale, 0.06)})
    scales(cv, 0 + 14, 32 + 14, 13, 11, darken(scale, 0.1))

    def neck_front(c, x, y):
        for i in range(0, 8, 2):
            c.line(x + i, y, x + i, y + 11, mane)

    box(cv, 48, 0, 8, 12, 8, {"main": scale, "front": scale}, front_detail=neck_front)

    def head_front(c, x, y):
        c.rect(x + 1, y + 1, x + 8, y + 8, lighten(scale, 0.08))
        c.px(x + 2, y + 4, hx("E8C86A"))          # 眼 / eyes
        c.px(x + 7, y + 4, hx("E8C86A"))
        c.px(x + 2, y + 4, INK)
        c.px(x + 7, y + 4, INK)
        c.px(x + 2, y + 3, INK)
        c.px(x + 7, y + 3, INK)
        c.rect(x + 3, y + 8, x + 6, y + 8, belly)  # 鼻梁 / muzzle bridge
        c.px(x + 1, y + 6, mane)                   # 颊毛 / cheek
        c.px(x + 8, y + 6, mane)

    box(cv, 48, 24, 10, 10, 10, {"main": scale, "front": lighten(scale, 0.05)},
        front_detail=head_front)

    def snout_front(c, x, y):
        c.rect(x, y + 2, x + 5, y + 4, belly)
        c.px(x + 1, y + 3, INK)                    # 鼻孔 / nostrils
        c.px(x + 4, y + 3, INK)
        c.line(x + 1, y + 5, x + 4, y + 5, darken(belly, 0.3))

    box(cv, 48, 48, 6, 6, 8, {"main": belly, "front": belly}, front_detail=snout_front)

    box(cv, 80, 0, 3, 4, 2, {"main": darken(scale, 0.2)})
    box(cv, 80, 0, 3, 4, 2, {"main": darken(scale, 0.2)})

    def antler(c, x, y):
        for i in range(0, 12, 3):
            c.line(x, y + i, x + 2, y + i, lighten(horn, 0.15))
            c.px(x + 1, y + i + 1, darken(horn, 0.2))

    box(cv, 80, 8, 3, 12, 3, {"main": horn}, front_detail=antler)
    box(cv, 80, 8, 3, 12, 3, {"main": horn}, front_detail=antler)

    def mane_detail(c, x, y):
        for i in range(0, 12, 2):
            c.line(x + i, y, x + i, y + 7, mane if i % 4 == 0 else darken(mane, 0.25))

    box(cv, 0, 64, 12, 8, 4, {"main": mane, "front": mane}, front_detail=mane_detail)

    for u, v, w, h, d in ((80, 24, 5, 10, 5), (80, 24, 5, 10, 5),
                          (80, 24, 5, 10, 5), (80, 24, 5, 10, 5)):
        box(cv, u, v, w, h, d, {"main": lighten(scale, 0.05)})
    for _ in range(4):
        box(cv, 80, 40, 4, 10, 4, {"main": darken(scale, 0.12)})
    for _ in range(4):
        box(cv, 80, 56, 4, 3, 5, {"main": hoof})

    def tail_detail(c, x, y):
        scales(c, x, y, 5, 5, scale)

    box(cv, 32, 64, 5, 5, 10, {"main": scale, "front": lighten(scale, 0.1)},
        front_detail=tail_detail)
    box(cv, 32, 80, 6, 6, 6, {"main": mane},
        front_detail=lambda c, x, y: [c.line(x + i, y, x + i, y + 5, darken(mane, 0.3))
                                      for i in range(0, 6, 2)])
    save(cv, "qilin")


if __name__ == "__main__":
    qilin()
    print("qilin texture done")
