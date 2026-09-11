"""方块贴图修正补丁（第一批）：青铜、编钟、龙椅。"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/block")
os.makedirs(OUT, exist_ok=True)
S = 32


def save(cv, name):
    cv.save(os.path.join(OUT, name + ".png"))


def block_edge(cv, shades, light=0.16, dark=0.22):
    for x in range(32):
        cv.px(x, 0, lighten(shades[1], light))
        cv.px(x, 31, darken(shades[1], dark))
    for y in range(32):
        cv.px(0, y, lighten(shades[1], light * 0.7))
        cv.px(31, y, darken(shades[1], dark * 0.8))


def bronze_block():
    metal = ramp(hx("C98A3C"), 6)
    cv = Cv(S, S)
    for y in range(32):
        for x in range(32):
            s = (x / 31.0) * 0.45 + (y / 31.0) * 0.55
            cv.px(x, y, mix(metal[0], metal[2], s))
    cv.line(2, 29, 29, 2, mix(metal[1], (255, 255, 255, 255), 0.3))
    cv.line(3, 30, 30, 3, mix(metal[2], (255, 255, 255, 255), 0.14))
    cv.line(0, 21, 21, 0, mix(metal[2], (0, 0, 0, 255), 0.22))
    cv.frame(2, 2, 29, 29, darken(metal[3], 0.2))
    cv.line(3, 3, 28, 3, lighten(metal[0], 0.6))
    cv.line(3, 4, 3, 28, lighten(metal[0], 0.4))
    cv.line(4, 28, 28, 28, darken(metal[3], 0.45))
    cv.line(28, 4, 28, 27, darken(metal[3], 0.4))
    for gx in (6, 25):
        for gy in (6, 25):
            cv.disc(gx, gy, 2.6, darken(metal[3], 0.25))
            cv.disc(gx, gy, 1.7, metal[1])
            cv.px(gx - 1, gy - 1, lighten(metal[0], 0.75))
    for gx, gy in ((11, 22), (20, 21), (15, 16), (22, 10)):
        cv.px(gx, gy, BRONZE_PATINA)
        cv.px(gx + 1, gy, mix(BRONZE_PATINA, metal[2], 0.55))
    block_edge(cv, metal, 0.22, 0.32)
    save(cv, "bronze_block")


def chime_bell():
    cv = Cv(S, S)
    cv.rect(14, 1, 17, 3, BRONZE[2])
    cv.px(15, 0, BRONZE[0])
    cv.px(16, 0, BRONZE[0])

    def half_at(y):
        if y < 9:
            return int(3 + (y - 4) * 0.95)
        if y < 24:
            return int(8.5 + (y - 9) * 0.07)
        return int(9.5 + (y - 24) * 0.4)

    for y in range(4, 30):
        half = half_at(y)
        base = mix(BRONZE[0], BRONZE[2], (y - 4) / 25.0 * 0.5)
        cv.rect(15 - half, y, 15 + half, y, base)
        cv.px(15 - half, y, lighten(base, 0.34))
        cv.px(15 + half, y, darken(base, 0.3))
    for k in (-0.66, -0.33, 0.0, 0.33, 0.66):
        for y in range(5, 29):
            half = half_at(y)
            x = int(15 + k * half)
            if abs(x - 15) < half - 1:
                cv.px(x, y, BRONZE_PATINA if k else darken(BRONZE[3], 0.18))
    for by in (11, 22):
        half = half_at(by)
        cv.rect(15 - half, by, 15 + half, by, mix(BRONZE[3], BRONZE_PATINA, 0.3))
    half = half_at(28)
    cv.rect(15 - half, 28, 15 + half, 28, darken(BRONZE[3], 0.35))
    cv.rect(15 - half, 29, 15 + half, 29, darken(BRONZE[3], 0.5))
    cv.px(11, 25, lighten(BRONZE[0], 0.6))
    cv.px(19, 15, darken(BRONZE[3], 0.3))
    save(cv, "chime_bell")


def dragon_throne():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, darken(GOLD_DARK, 0.55))
    cv.disc(15.5, 11, 11, GOLD[2])
    cv.rect(4, 11, 27, 21, GOLD[2])
    cv.disc(15.5, 11, 9, RED_SILK[2])
    cv.rect(6, 11, 25, 21, RED_SILK[2])
    cv.disc(15.5, 11, 7, RED_SILK[0])
    cv.rect(8, 11, 23, 20, RED_SILK[0])
    cv.line(11, 18, 13, 13, GOLD[0])
    cv.line(13, 13, 18, 13, GOLD[0])
    cv.line(18, 13, 20, 17, GOLD[0])
    cv.line(20, 17, 16, 18, GOLD[0])
    cv.px(15, 11, lighten(GOLD[0], 0.65))
    cv.px(12, 16, GOLD[1])
    cv.px(19, 14, GOLD[1])
    cv.px(13, 19, GOLD[2])
    cv.px(18, 19, GOLD[2])
    for ax in (2, 27):
        cv.rect(ax, 12, ax + 2, 25, GOLD[1])
        cv.px(ax, 12, lighten(GOLD[0], 0.55))
        cv.disc(ax + 1, 11, 2, GOLD[0])
        cv.px(ax + 1, 13, lighten(GOLD[0], 0.35))
    cv.rect(7, 22, 24, 25, RED_SILK[1])
    cv.rect(8, 22, 23, 24, RED_SILK[0])
    cv.line(8, 23, 23, 23, RED_SILK[2])
    cv.rect(6, 26, 25, 28, GOLD[1])
    cv.rect(7, 27, 24, 27, GOLD[0])
    cv.rect(7, 29, 10, 30, GOLD[2])
    cv.rect(21, 29, 24, 30, GOLD[2])
    cv.frame(0, 0, 31, 31, darken(GOLD_DARK, 0.6))
    save(cv, "dragon_throne")


def apply_all():
    bronze_block()
    chime_bell()
    dragon_throne()
    deepslate_jade_ore()
    dragon_crystal_ore()
    crimson_pillar()
    print("block fixes applied")


def deepslate_base(seed):
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, DEEPSLATE[1])
    rnd = random.Random(seed)
    for _ in range(26):
        x, y = rnd.randrange(32), rnd.randrange(32)
        col = DEEPSLATE[2] if rnd.random() < 0.6 else DEEPSLATE[0]
        cv.rect(x, y, x + rnd.randrange(0, 2), y + rnd.randrange(0, 1), col)
    for _ in range(5):
        x, y = rnd.randrange(4, 26), rnd.randrange(4, 26)
        cv.line(x, y, x + rnd.randrange(2, 5), y + rnd.randrange(0, 2), darken(DEEPSLATE[3], 0.12))
    block_edge(cv, DEEPSLATE, 0.18, 0.26)
    return cv


def deepslate_jade_ore():
    ds = deepslate_base(43)
    rnd = random.Random(46)
    for _ in range(rnd.randrange(4, 6)):
        cx, cy = rnd.randrange(4, 28), rnd.randrange(4, 28)
        r = rnd.randrange(2, 4)
        ds.disc(cx, cy, r + 0.6, JADE[3])
        ds.disc(cx, cy, r, JADE[1])
        ds.disc(cx - 1, cy - 1, r * 0.6, JADE[0])
        ds.px(cx - 1, cy - 1, JADE_LIGHT)
        ds.px(cx + 1, cy + 1, JADE[2])
    save(ds, "deepslate_jade_ore")


def dragon_crystal_ore():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, STONE_GREY[1])
    rnd = random.Random(47)
    for _ in range(30):
        cv.px(rnd.randrange(32), rnd.randrange(32), rnd.choice([STONE_GREY[0], STONE_GREY[2]]))
    block_edge(cv, STONE_GREY, 0.14, 0.2)
    for cx, cy, h, w in ((8, 11, 7, 2), (17, 9, 9, 2), (24, 16, 6, 2), (12, 22, 7, 2), (21, 24, 5, 2)):
        cv.poly([(cx, cy - h), (cx + w, cy), (cx, cy + h // 2), (cx - w, cy)], DRAGON_CRYSTAL[3])
        cv.poly([(cx, cy - h + 1), (cx + w - 1, cy), (cx, cy + h // 2 - 1), (cx - w + 1, cy)],
                DRAGON_CRYSTAL[1])
        cv.line(cx, cy - h + 2, cx, cy + h // 2 - 2, DRAGON_CRYSTAL[0])
        cv.px(cx, cy - h + 2, lighten(DRAGON_CRYSTAL[0], 0.6))
    save(cv, "dragon_crystal_ore")


def crimson_pillar():
    cv = Cv(S, S)
    for x in range(32):
        shade = mix(RED_LACQUER[1], RED_LACQUER[3], x / 31.0 * 0.5)
        for y in range(32):
            cv.px(x, y, shade)
        if x % 6 == 0:
            for y in range(32):
                cv.px(x, y, darken(shade, 0.18))
        elif x % 6 == 3:
            for y in range(32):
                cv.px(x, y, lighten(shade, 0.12))
    cv.px(6, 12, darken(RED_LACQUER[3], 0.3))
    cv.px(7, 12, darken(RED_LACQUER[3], 0.18))
    cv.rect(0, 0, 31, 1, GOLD_TRIM)
    cv.rect(0, 30, 31, 31, darken(GOLD_TRIM, 0.45))
    cv.line(0, 2, 31, 2, darken(GOLD_TRIM, 0.3))
    save(cv, "crimson_pillar_side")

    top = Cv(S, S)
    top.rect(0, 0, 31, 31, darken(RED_LACQUER[3], 0.3))
    top.disc(15.5, 15.5, 13, mix(RED_LACQUER[0], RED_LACQUER[1], 0.5))
    top.ring(15.5, 15.5, 13, darken(RED_LACQUER[3], 0.2))
    top.ring(15.5, 15.5, 11, mix(RED_LACQUER[1], RED_LACQUER[2], 0.4))
    top.ring(15.5, 15.5, 7, mix(RED_LACQUER[1], RED_LACQUER[2], 0.25))
    top.disc(15.5, 15.5, 4, GOLD_TRIM)
    top.px(15, 15, lighten(GOLD_TRIM, 0.6))
    top.px(16, 16, darken(GOLD_TRIM, 0.3))
    save(top, "crimson_pillar_top")


if __name__ == "__main__":
    apply_all()
