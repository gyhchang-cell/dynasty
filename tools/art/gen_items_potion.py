"""王朝物品贴图 E：丹药与药水。"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from gen_items_b import save

OUT = os.path.join(os.path.dirname(__file__), "out/item")
S = 32


def pill(name, c1, c2, c3):
    cv = Cv(S, S)
    cv.disc(15.5, 20, 9, darken(c3, 0.3))
    cv.disc(15.5, 19, 8, c2)
    cv.disc(13, 16, 4, c1)
    cv.px(12, 15, lighten(c1, 0.6))
    cv.px(12, 16, lighten(c1, 0.4))
    cv.px(19, 23, darken(c3, 0.2))
    cv.disc(20, 9, 3, c2)
    cv.disc(20, 8, 2, c1)
    cv.px(19, 7, lighten(c1, 0.5))
    save(cv, name)


def healing_salve():
    cv = Cv(S, S)
    cv.rect(8, 12, 23, 26, hx("6B4423"))
    cv.rect(9, 13, 22, 25, hx("B08A5A"))
    cv.rect(10, 14, 21, 18, hx("C9A87A"))
    cv.rect(7, 9, 24, 12, hx("D9C08B"))
    cv.rect(8, 10, 23, 11, hx("F0DCB0"))
    cv.rect(12, 19, 19, 24, hx("E8F0D8"))
    cv.rect(13, 20, 18, 23, hx("8FBF6A"))
    cv.px(14, 21, hx("C8E8A0"))
    cv.px(15, 21, hx("4E7A4A"))
    save(cv, "healing_salve")


def potion(name, liquid, splash=False, lingering=False):
    cv = Cv(S, S)
    cv.rect(13, 4, 18, 9, hx("D8DEE8"))
    cv.rect(14, 5, 17, 8, hx("AEB6C2"))
    cv.rect(12, 3, 19, 4, hx("C9A66B"))
    cv.rect(12, 2, 19, 3, hx("A88450"))
    cv.disc(15.5, 19, 9, hx("D8DEE8"))
    cv.disc(15.5, 19, 8, hx("C0C8D4"))
    cv.disc(15.5, 19, 7, liquid)
    cv.disc(13, 16, 4, lighten(liquid, 0.35))
    cv.px(11, 16, (255, 255, 255, 235))
    cv.px(12, 15, (255, 255, 255, 190))
    cv.rect(9, 19, 22, 20, mix(liquid, (0, 0, 0, 255), 0.25))
    if splash:
        for dx, dy in ((-4, -2), (4, -3), (-3, 4), (4, 3)):
            cv.disc(15 + dx, 19 + dy, 1.6, liquid)
    if lingering:
        cv.ring(15.5, 19, 10, mix(liquid, (255, 255, 255, 255), 0.35))
    save(cv, name)


if __name__ == "__main__":
    pill("pill_longevity", hx("F5D76E"), hx("E0A83A"), hx("9A6A16"))
    pill("pill_focus", hx("8FD9FF"), hx("4FA8D9"), hx("1E5F8A"))
    healing_salve()
    potion("dynasty_potion", hx("39C1A0"))
    potion("dynasty_splash_potion", hx("D9453A"), splash=True)
    potion("dynasty_lingering_potion", hx("A44FE0"), lingering=True)
    print("pills/potions done:", len(os.listdir(OUT)))
