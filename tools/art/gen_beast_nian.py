"""年兽贴图（128x128，麒麟骨架）：青黑兽皮、白色鬃毛、金角、赤目獠牙。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from entity_kit import box

OUT = os.path.join(os.path.dirname(__file__), "out/entity")
S = 128
INK = (12, 8, 8, 255)


def save(cv, name):
    cv.im.save(os.path.join(OUT, name + ".png"))


def nian():
    cv = Cv(S, S)
    hide = hx("3A4258")
    belly = hx("9AA6BE")
    mane = hx("EDEDE4")
    horn = hx("E8C86A")
    hoofColor = hx("201820")

    def fur(c, x, y, w, h, base):
        lo = darken(base, 0.25)
        hi = lighten(base, 0.2)
        for i in range(0, w, 2):
            c.line(x + i, y, x + i, y + h - 1, lo if i % 4 else hi)

    box(cv, 0, 0, 14, 12, 16, {"main": hide},
        front_detail=lambda c, x, y: (fur(c, x, y, 14, 12, hide),
                                      c.rect(x + 4, y + 7, x + 9, y + 11, belly)))
    fur(cv, 16 + 14, 16, 14, 12, darken(hide, 0.15))

    box(cv, 0, 32, 13, 11, 14, {"main": darken(hide, 0.08)})
    fur(cv, 0 + 14, 32 + 14, 13, 11, darken(hide, 0.12))

    box(cv, 48, 0, 8, 12, 8, {"main": hide},
        front_detail=lambda c, x, y: [c.line(x + i, y, x + i, y + 11, mane)
                                      for i in range(0, 8, 2)])

    def head_front(c, x, y):
        c.rect(x, y, x + 9, y + 9, lighten(hide, 0.06))
        c.px(x + 2, y + 4, hx("E8342A"))           # 赤目 / burning eyes
        c.px(x + 7, y + 4, hx("E8342A"))
        c.px(x + 1, y + 4, hx("E8342A"))
        c.px(x + 8, y + 4, hx("E8342A"))
        c.px(x + 2, y + 4, INK)
        c.px(x + 7, y + 4, INK)
        c.rect(x + 3, y + 7, x + 6, y + 9, belly)
        c.px(x, y + 6, mane)
        c.px(x + 9, y + 6, mane)

    box(cv, 48, 24, 10, 10, 10, {"main": hide}, front_detail=head_front)

    def snout_front(c, x, y):
        c.rect(x, y + 1, x + 5, y + 3, belly)
        c.px(x + 1, y + 2, INK)
        c.px(x + 4, y + 2, INK)
        c.line(x, y + 4, x, y + 5, hx("F0F0E8"))   # 獠牙 / fangs
        c.line(x + 5, y + 4, x + 5, y + 5, hx("F0F0E8"))
        c.px(x + 2, y + 5, hx("F0F0E8"))
        c.px(x + 3, y + 5, hx("F0F0E8"))

    box(cv, 48, 48, 6, 6, 8, {"main": darken(hide, 0.2)}, front_detail=snout_front)

    for _ in range(2):
        box(cv, 80, 0, 3, 4, 2, {"main": darken(hide, 0.3)})

    def horn_detail(c, x, y):
        for i in range(0, 12, 3):
            c.line(x, y + i, x + 2, y + i, lighten(horn, 0.2))
            c.px(x + 1, y + i + 1, darken(horn, 0.25))

    for _ in range(2):
        box(cv, 80, 8, 3, 12, 3, {"main": horn}, front_detail=horn_detail)

    box(cv, 0, 64, 12, 8, 4, {"main": mane},
        front_detail=lambda c, x, y: [c.line(x + i, y, x + i, y + 7, mane if i % 3 else darken(mane, 0.18))
                                      for i in range(0, 12, 2)])

    for _ in range(4):
        box(cv, 80, 24, 5, 10, 5, {"main": hide})
    for _ in range(4):
        box(cv, 80, 40, 4, 10, 4, {"main": darken(hide, 0.15)})
    for _ in range(4):
        box(cv, 80, 56, 4, 3, 5, {"main": hoofColor})

    box(cv, 32, 64, 5, 5, 10, {"main": hide},
        front_detail=lambda c, x, y: fur(c, x, y, 5, 5, hide))
    box(cv, 32, 80, 6, 6, 6, {"main": mane},
        front_detail=lambda c, x, y: [c.line(x + i, y, x + i, y + 5, darken(mane, 0.25))
                                      for i in range(0, 6, 2)])
    save(cv, "nian_beast")


if __name__ == "__main__":
    nian()
    print("nian beast texture done")
