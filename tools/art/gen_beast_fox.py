"""九尾狐贴图（128x128）：琥珀色皮毛、奶白胸毛、九条渐变色狐尾。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from entity_kit import box

OUT = os.path.join(os.path.dirname(__file__), "out/entity")
S = 128
INK = (16, 12, 10, 255)


def save(cv, name):
    cv.im.save(os.path.join(OUT, name + ".png"))


def fur(cv, x0, y0, w, h, base):
    """毛发纹路 / fur strands"""
    lo = darken(base, 0.22)
    hi = lighten(base, 0.18)
    for i in range(0, w, 2):
        cv.line(x0 + i, y0, x0 + i, y0 + h - 1, lo if i % 4 else hi)


def fox():
    cv = Cv(S, S)
    coat = hx("B4652A")
    belly = hx("EFDCBA")
    tailbase = hx("C87A32")
    tailtip = hx("E8C86A")
    paw = hx("3A2A1A")

    def body_front(c, x, y):
        fur(c, x, y, 12, 10, coat)
        c.rect(x + 3, y + 5, x + 8, y + 9, belly)

    box(cv, 0, 0, 12, 10, 16, {"main": coat}, front_detail=body_front)
    fur(cv, 0 + 16 + 12, 0 + 16, 12, 10, darken(coat, 0.12))   # 背面 / back

    def head_front(c, x, y):
        c.rect(x, y, x + 8, y + 8, lighten(coat, 0.08))
        c.rect(x + 1, y + 5, x + 7, y + 8, belly)
        c.px(x + 2, y + 3, hx("E84A2A"))           # 狐眼 / fox eyes
        c.px(x + 6, y + 3, hx("E84A2A"))
        c.px(x + 2, y + 3, INK)
        c.px(x + 6, y + 3, INK)
        c.px(x + 4, y + 4, INK)
        c.px(x + 1, y + 1, lighten(coat, 0.25))
        c.px(x + 7, y + 1, lighten(coat, 0.25))

    box(cv, 48, 24, 9, 9, 9, {"main": coat}, front_detail=head_front)

    def snout_front(c, x, y):
        c.rect(x, y + 1, x + 4, y + 3, belly)
        c.px(x, y + 2, INK)
        c.px(x + 4, y + 2, INK)

    box(cv, 48, 48, 5, 5, 7, {"main": belly}, front_detail=snout_front)

    for _ in range(2):
        def ear(c, x, y):
            c.rect(x, y + 2, x + 2, y + 3, belly)
        box(cv, 80, 0, 3, 4, 2, {"main": coat}, front_detail=ear)

    def ruff_detail(c, x, y):
        for i in range(0, 10, 2):
            c.line(x + i, y, x + i + 1, y + 7, belly if i % 4 == 0 else darken(belly, 0.15))

    box(cv, 0, 64, 10, 8, 3, {"main": belly}, front_detail=ruff_detail)

    for _ in range(4):
        box(cv, 80, 24, 4, 9, 4, {"main": coat})
    for _ in range(4):
        box(cv, 80, 40, 3, 9, 3, {"main": darken(coat, 0.18)})
    for _ in range(4):
        box(cv, 80, 56, 3, 2, 4, {"main": paw})

    spots = [(0, 96), (24, 96), (48, 96), (72, 96), (96, 96), (0, 108), (24, 108), (48, 108), (72, 108)]
    for i, (u, v) in enumerate(spots):
        t = i / 8.0
        color = mix(tailbase, tailtip, t)

        def detail(c, x, y, color=color):
            fur(c, x, y, 4, 4, color)
            c.line(x, y + 3, x + 3, y + 3, darken(color, 0.3))

        box(cv, u, v, 4, 4, 8, {"main": color}, front_detail=detail)
    save(cv, "nine_tailed_fox")


if __name__ == "__main__":
    fox()
    print("nine-tailed fox texture done")
