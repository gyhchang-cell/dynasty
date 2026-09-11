"""凤凰贴图（128x128）：朱红羽衣、鎏金喙冠、三层羽翼、三根长尾羽。"""
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


def feathers(cv, x0, y0, w, h, base, step=3):
    """羽毛层纹 / layered feather texture"""
    lo = darken(base, 0.28)
    hi = lighten(base, 0.22)
    for row in range(0, h, step):
        for col in range(0, w, 2):
            cv.px(x0 + col, y0 + row + 1, lo)
            cv.px(x0 + col + 1, y0 + row + 1, hi)


def phoenix():
    cv = Cv(S, S)
    body = hx("C0392B")
    bodylight = hx("E85A3A")
    gold = hx("E8C86A")
    wingA = hx("B22A20")
    wingB = hx("E07A2A")
    wingC = hx("E8C86A")
    tail = hx("8B1A14")

    def chest_front(c, x, y):
        feathers(c, x, y, 10, 9, body, 3)
        c.rect(x + 3, y + 4, x + 6, y + 8, bodylight)

    box(cv, 0, 0, 10, 9, 16, {"main": body}, front_detail=chest_front)

    def neck_front(c, x, y):
        for i in range(0, 6, 2):
            c.line(x + i, y, x + i, y + 9, gold if i % 4 == 0 else darken(gold, 0.3))

    box(cv, 48, 0, 6, 10, 6, {"main": bodylight}, front_detail=neck_front)

    def head_front(c, x, y):
        c.rect(x, y, x + 7, y + 6, bodylight)
        c.px(x + 2, y + 2, gold)
        c.px(x + 5, y + 2, gold)
        c.px(x + 2, y + 2, INK)
        c.px(x + 5, y + 2, INK)
        c.px(x + 3, y + 5, gold)
        c.px(x + 4, y + 5, gold)

    box(cv, 48, 16, 8, 7, 8, {"main": bodylight}, front_detail=head_front)

    def beak_front(c, x, y):
        c.rect(x, y, x + 3, y + 2, gold)
        c.px(x + 1, y + 1, darken(gold, 0.35))
        c.px(x + 2, y + 1, darken(gold, 0.35))

    box(cv, 48, 36, 4, 3, 6, {"main": gold}, front_detail=beak_front)

    def crest_detail(c, x, y):
        for i in range(0, 8, 2):
            c.line(x, y + i, x + 1, y + i, gold if i % 4 == 0 else hx("F0803A"))

    box(cv, 48, 48, 2, 8, 2, {"main": gold}, front_detail=crest_detail)

    def wing(u, v, w, h, d, base):
        def detail(c, x, y):
            feathers(c, x, y, w, d, base, 2)
        box(cv, u, v, w, h, d, {"main": base}, front_detail=detail)

    for flip in (0, 1):
        wing(80, 0, 4, 2, 18, wingA)
        wing(80, 24, 4, 2, 16, wingB)
        wing(80, 48, 4, 2, 12, wingC)

    def tail_detail(c, x, y):
        for i in range(0, 20, 4):
            c.line(x + 1, y + i, x + 1, y + i + 2, gold if i % 8 == 0 else wingB)

    for i in range(3):
        base = mix(tail, wingB, i / 3.0)
        box(cv, 0, 40, 3, 2, 20, {"main": base}, front_detail=tail_detail)

    for _ in range(2):
        box(cv, 0, 64, 3, 8, 3, {"main": darken(body, 0.2)})
    for _ in range(2):
        def talon(c, x, y):
            for i in range(0, 4, 1):
                c.line(x + i, y + 1, x + i, y + 2, gold)
        box(cv, 0, 80, 4, 3, 5, {"main": gold}, front_detail=talon)
    save(cv, "phoenix")


if __name__ == "__main__":
    phoenix()
    print("phoenix texture done")
