"""王朝方块贴图（32x32，细节向）/ Dynasty block textures."""
import os, random, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/block")
os.makedirs(OUT, exist_ok=True)
S = 32


def save(cv, name):
    cv.save(os.path.join(OUT, name + ".png"))


def speckle(cv, x0, y0, x1, y1, dark, light, seed=1, density=0.12):
    rnd = random.Random(seed)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            r = rnd.random()
            if r < density * 0.6:
                cv.px(x, y, dark)
            elif r < density:
                cv.px(x, y, light)


def vein(cv, x, y, length, color, shadow=None, drift=0.9, seed=0):
    rnd = random.Random(seed)
    ph = rnd.random() * 6.28
    for i in range(length):
        px, py = int(x + i), int(y + math.sin(ph + i * 0.5) * drift)
        cv.px(px, py, color)
        if shadow:
            cv.px(px, py + 1, shadow)


def block_edge(cv, shades, light=0.16, dark=0.22):
    for x in range(32):
        cv.px(x, 0, lighten(shades[1], light))
        cv.px(x, 31, darken(shades[1], dark))
    for y in range(32):
        cv.px(0, y, lighten(shades[1], light * 0.7))
        cv.px(31, y, darken(shades[1], dark * 0.8))


def stone_base(shades, seed):
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, shades[1])
    speckle(cv, 0, 0, 31, 31, shades[2], shades[0], seed=seed, density=0.16)
    rnd = random.Random(seed + 7)
    for _ in range(5):
        x, y = rnd.randrange(2, 28), rnd.randrange(2, 28)
        cv.px(x, y, shades[2])
        cv.px(x + 1, y, shades[2])
        cv.px(x, y + 1, shades[0])
    block_edge(cv, shades, 0.14, 0.2)
    return cv


# ---------------------------------------------------------------- 汉白玉
def marble():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, MARBLE[1])
    speckle(cv, 0, 0, 31, 31, MARBLE[2], MARBLE[0], seed=11, density=0.10)
    vein(cv, 1, 9, 24, MARBLE_VEIN, mix(MARBLE[2], MARBLE_VEIN, 0.6), drift=1.1, seed=3)
    vein(cv, 6, 21, 20, mix(MARBLE_VEIN, MARBLE[3], 0.35), None, drift=0.8, seed=8)
    vein(cv, 19, 4, 11, MARBLE_VEIN, None, drift=0.6, seed=5)
    block_edge(cv, MARBLE, 0.12, 0.16)
    save(cv, "marble_block")


# ---------------------------------------------------------------- 宫墙砖
def palace_bricks():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, BRICK_MORTAR)
    bh, bw, gap = 6, 14, 2
    rnd = random.Random(3)
    for row, y in enumerate(range(0, 32, bh + gap)):
        offset = 0 if row % 2 == 0 else -8
        for x in range(offset, 33, bw + gap):
            x0, y0 = max(x, 0), y
            x1, y1 = min(x + bw - 1, 31), min(y + bh - 1, 31)
            if x1 <= x0 or y1 <= y0:
                continue
            base = mix(PALACE_BRICK[1], PALACE_BRICK[2], rnd.random() * 0.5)
            cv.rect(x0, y0, x1, y1, base)
            for by in range(y0, y1 + 1):
                cv.px(x0, by, lighten(base, 0.14))
                cv.px(x1, by, darken(base, 0.2))
            for bx in range(x0, x1 + 1):
                cv.px(bx, y0, lighten(base, 0.26))
                cv.px(bx, y1, darken(base, 0.3))
            if rnd.random() < 0.5:
                cv.px(rnd.randrange(x0, x1 + 1), rnd.randrange(y0, y1 + 1), lighten(base, 0.1))
    save(cv, "palace_bricks")


# ---------------------------------------------------------------- 青玉块
def jade_block():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, JADE[1])
    speckle(cv, 0, 0, 31, 31, JADE[2], JADE[0], seed=21, density=0.12)
    vein(cv, -2, 12, 36, JADE_LIGHT, mix(JADE[0], JADE_LIGHT, 0.5), drift=1.4, seed=13)
    vein(cv, -2, 22, 36, mix(JADE[0], JADE_LIGHT, 0.6), JADE[3], drift=1.0, seed=17)
    for cx, cy in ((7, 6), (22, 9), (12, 24), (26, 26)):
        cv.rect(cx, cy, cx + 1, cy + 1, JADE[0])
        cv.px(cx, cy, JADE_LIGHT)
        cv.px(cx + 1, cy + 1, JADE[2])
    block_edge(cv, JADE, 0.2, 0.22)
    save(cv, "jade_block")


# ---------------------------------------------------------------- 青铜块（铸造铜板）
def bronze_block():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, BRONZE[1])
    rnd = random.Random(31)
    # 拉丝只做弱对比，避免像竹编 / low-contrast brushing so it still reads as metal
    for y in range(32):
        for x in range(32):
            t = (x * 0.7 + y * 0.3) % 7
            if t < 1:
                cv.px(x, y, mix(BRONZE[1], BRONZE[0], 0.35))
            elif t > 6:
                cv.px(x, y, mix(BRONZE[1], BRONZE[2], 0.3))
    speckle(cv, 0, 0, 31, 31, BRONZE[2], BRONZE[0], seed=32, density=0.07)
    # 内嵌面板 + 立体边 / inset plate with bevel
    cv.frame(2, 2, 29, 29, darken(BRONZE[2], 0.25))
    cv.line(3, 3, 28, 3, lighten(BRONZE[0], 0.45))
    cv.line(3, 4, 3, 28, lighten(BRONZE[0], 0.25))
    cv.line(4, 28, 28, 28, darken(BRONZE[3], 0.35))
    cv.line(28, 4, 28, 27, darken(BRONZE[3], 0.3))
    for gx in (6, 25):
        for gy in (6, 25):
            cv.disc(gx, gy, 2.6, BRONZE[3])
            cv.disc(gx, gy, 1.7, BRONZE[0])
            cv.px(gx - 1, gy - 1, lighten(BRONZE[0], 0.6))
            cv.px(gx + 1, gy + 1, darken(BRONZE[2], 0.3))
    for _ in range(5):
        cv.px(rnd.randrange(4, 28), rnd.randrange(4, 28), BRONZE_PATINA)
    block_edge(cv, BRONZE, 0.18, 0.26)
    save(cv, "bronze_block")


# ---------------------------------------------------------------- 编钟（圆肩钟形）
def chime_bell():
    cv = Cv(S, S)
    cv.rect(14, 1, 17, 3, BRONZE[2])                 # 悬钮 / suspension knob
    cv.px(15, 0, BRONZE[0])
    cv.px(16, 0, BRONZE[0])
    for y in range(4, 28):
        t = (y - 4) / 23.0
        half = int(2.2 + 9.5 * math.sin(t * math.pi * 0.5) ** 0.75)   # 圆肩外张 / rounded flare
        base = mix(BRONZE[0], BRONZE[2], t * 0.45)
        cv.rect(15 - half, y, 15 + half, y, base)
        cv.px(15 - half, y, lighten(base, 0.32))
        cv.px(15 + half, y, darken(base, 0.3))
    # 竖棱（细）/ thin vertical ribs
    for k in (-0.62, -0.3, 0.3, 0.62):
        for y in range(6, 27):
            t = (y - 4) / 23.0
            half = int(2.2 + 9.5 * math.sin(t * math.pi * 0.5) ** 0.75)
            x = int(15 + k * half)
            if abs(x - 15) < half - 1:
                cv.px(x, y, mix(base_of(y), BRONZE_PATINA, 0.55) if False else BRONZE_PATINA)
    # 钲带 / decorative bands
    for by in (9, 20):
        t = (by - 4) / 23.0
        half = int(2.2 + 9.5 * math.sin(t * math.pi * 0.5) ** 0.75)
        cv.rect(15 - half, by, 15 + half, by, darken(BRONZE[3], 0.1))
    # 钟口（薄唇）/ thin mouth lip
    cv.rect(5, 28, 26, 29, darken(BRONZE[3], 0.15))
    cv.rect(6, 28, 25, 28, lighten(BRONZE[1], 0.25))
    cv.rect(6, 29, 25, 29, darken(BRONZE[3], 0.4))
    cv.px(10, 25, lighten(BRONZE[0], 0.55))
    cv.px(20, 16, darken(BRONZE[3], 0.25))
    save(cv, "chime_bell")


def base_of(y):
    t = max(0.0, min(1.0, (y - 4) / 23.0))
    return mix(BRONZE[0], BRONZE[2], t * 0.45)


# ---------------------------------------------------------------- 柱顶（断面年轮）
def crimson_pillar_top():
    top = Cv(S, S)
    top.rect(0, 0, 31, 31, darken(RED_LACQUER[3], 0.45))      # 树皮 / bark
    speckle(top, 0, 0, 31, 31, darken(RED_LACQUER[3], 0.6), darken(RED_LACQUER[3], 0.25), seed=71, density=0.22)
    top.disc(15.5, 15.5, 13, RED_LACQUER[1])                  # 断面 / cut face
    top.ring(15.5, 15.5, 13, darken(RED_LACQUER[2], 0.2))
    top.ring(15.5, 15.5, 10, mix(RED_LACQUER[2], RED_LACQUER[1], 0.5))
    top.ring(15.5, 15.5, 6, mix(RED_LACQUER[2], RED_LACQUER[1], 0.35))
    # 径向裂纹 / radial cracks
    for a in (12, 100, 187, 275):
        rad = math.radians(a)
        top.line(int(15.5 + math.cos(rad) * 4), int(15.5 + math.sin(rad) * 4),
                 int(15.5 + math.cos(rad) * 12), int(15.5 + math.sin(rad) * 12),
                 darken(RED_LACQUER[3], 0.2))
    top.disc(15.5, 15.5, 3, GOLD_TRIM)                        # 中心金钉 / centre pin
    top.px(15, 15, lighten(GOLD_TRIM, 0.55))
    top.ring(15.5, 15.5, 15, darken(RED_LACQUER[3], 0.5))
    save(top, "crimson_pillar_top")


# ---------------------------------------------------------------- 龙椅（清晰王座剪影）
def dragon_throne():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, darken(GOLD_DARK, 0.5))
    # 椅背 / backrest
    cv.rect(6, 1, 25, 20, GOLD[2])
    cv.rect(7, 2, 24, 19, GOLD[0])
    cv.rect(9, 4, 22, 17, RED_SILK[1])
    cv.rect(10, 5, 21, 16, RED_SILK[0])
    # 云龙纹：S 形龙身 + 云勾 / coiled dragon + cloud curls
    cv.line(12, 14, 14, 10, GOLD[0])
    cv.line(14, 10, 18, 10, GOLD[0])
    cv.line(18, 10, 20, 13, GOLD[0])
    cv.line(20, 13, 17, 15, GOLD[0])
    cv.px(13, 15, GOLD[1])
    cv.px(11, 11, GOLD[1])
    cv.px(21, 9, GOLD[1])
    cv.px(15, 8, lighten(GOLD[0], 0.55))
    cv.px(12, 17, GOLD[2])
    cv.px(19, 17, GOLD[2])
    # 左右立柱扶手 / armrest posts
    for ax in (4, 27):
        cv.rect(ax, 11, ax + 1, 25, GOLD[1])
        cv.px(ax, 11, lighten(GOLD[0], 0.5))
        cv.px(ax + 1, 25, darken(GOLD[3], 0.2))
        cv.px(ax, 10, GOLD[0])
    # 坐垫 / seat cushion
    cv.rect(8, 21, 23, 24, RED_SILK[1])
    cv.rect(9, 21, 22, 23, RED_SILK[0])
    cv.line(9, 22, 22, 22, RED_SILK[2])
    cv.px(15, 21, RED_SILK[3])
    # 底座与足 / base and legs
    cv.rect(5, 25, 26, 28, GOLD[1])
    cv.rect(6, 26, 25, 27, GOLD[0])
    for x in range(7, 25, 3):
        cv.px(x, 26, lighten(GOLD[0], 0.5))
    cv.rect(7, 29, 10, 30, GOLD[2])
    cv.rect(21, 29, 24, 30, GOLD[2])
    cv.frame(0, 0, 31, 31, darken(GOLD_DARK, 0.55))
    save(cv, "dragon_throne")


# ---------------------------------------------------------------- 祭坛（方坛 + 八角嵌纹）
def altar():
    cv = stone_base(MARBLE, 61)
    pts = []
    for a in range(0, 360, 45):
        rad = math.radians(a + 22.5)
        pts.append((int(15.5 + math.cos(rad) * 11), int(15.5 + math.sin(rad) * 11)))
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.line(x0, y0, x1, y1, GOLD_TRIM)
        cv.px(x0, y0 + 1, darken(GOLD_TRIM, 0.3))
    cv.disc(15.5, 15.5, 6, MARBLE[2])
    cv.disc(15.5, 15.5, 5, mix(MARBLE[1], GOLD_TRIM, 0.25))
    cv.disc(15.5, 15.5, 3, hx("B22A20"))
    cv.px(14, 14, hx("E86A4A"))
    cv.px(16, 16, hx("7A1A14"))
    for dx, dy in ((0, -8), (0, 8), (-8, 0), (8, 0)):
        cv.rect(15 + dx - 1, 15 + dy, 15 + dx + 1, 15 + dy, MARBLE_VEIN)
    cv.frame(0, 0, 31, 31, MARBLE[3])
    save(cv, "altar")


# ---------------------------------------------------------------- 香炉（三足双耳）
def incense_burner():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, (26, 22, 18, 255))
    # 双耳 / two handles
    for hx_ in (4, 26):
        cv.rect(hx_, 11, hx_ + 1, 17, BRONZE[1])
        cv.px(hx_, 11, BRONZE[0])
        cv.px(hx_ + 1, 17, BRONZE[2])
    # 炉身 / body
    cv.disc(15.5, 17, 11, BRONZE[2])
    cv.disc(15.5, 16, 10, BRONZE[1])
    cv.disc(12, 13, 5, BRONZE[0])
    for x in range(8, 24, 3):                       # 镂空纹 / pierced pattern
        for y in range(13, 19, 2):
            cv.px(x, y, darken(BRONZE[3], 0.25))
    cv.rect(7, 20, 24, 21, GOLD_TRIM)
    cv.rect(8, 22, 23, 23, BRONZE[2])
    # 盖与钮 / lid + knob
    cv.rect(11, 7, 20, 10, GOLD_DARK)
    cv.rect(12, 6, 19, 8, GOLD_TRIM)
    cv.rect(14, 4, 17, 5, GOLD_TRIM)
    cv.px(15, 3, lighten(GOLD_TRIM, 0.5))
    # 三足 / three legs
    for lx in (7, 15, 23):
        cv.rect(lx, 24, lx + 1, 28, BRONZE[2])
        cv.px(lx, 29, BRONZE[3])
        cv.px(lx, 24, BRONZE[0])
    # 香火 / glowing embers
    cv.rect(13, 16, 18, 18, hx("B22A20"))
    cv.px(14, 16, hx("F0803A"))
    cv.px(17, 17, hx("FFD27F"))
    cv.px(15, 17, hx("FF8A3A"))
    save(cv, "incense_burner")


# ---------------------------------------------------------------- 矿石
def ore(name, base_shades, gem_ramp, glow, seed):
    cv = stone_base(base_shades, seed)
    rnd = random.Random(seed + 3)
    for _ in range(rnd.randrange(4, 6)):
        cx = rnd.randrange(4, 28)
        cy = rnd.randrange(4, 28)
        r = rnd.randrange(2, 4)
        cv.disc(cx, cy, r + 0.6, gem_ramp[3])          # 暗边 / dark rim
        cv.disc(cx, cy, r, gem_ramp[1])                # 主体 / body
        cv.disc(cx - 1, cy - 1, r * 0.6, gem_ramp[0])  # 受光 / lit area
        cv.px(cx - 1, cy - 1, glow)                    # 高光 / specular
        cv.px(cx + 1, cy + 1, gem_ramp[2])
    return cv


def ores():
    ore("jade_ore", STONE_GREY, JADE, JADE_LIGHT, 41).save(os.path.join(OUT, "jade_ore.png"))
    ore("deepslate_jade_ore", DEEPSLATE, JADE, JADE_LIGHT, 43).save(os.path.join(OUT, "deepslate_jade_ore.png"))
    # 覆盖深板岩底纹为纵向纹理 / re-render deepslate ore with a vertical-slate base
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
    ds.save(os.path.join(OUT, "deepslate_jade_ore.png"))
    # 龙晶：尖锐晶簇 / angular crystal shards
    cv = stone_base(STONE_GREY, 47)
    rnd = random.Random(53)
    for cx, cy, size in ((8, 9, 4), (20, 7, 3), (24, 20, 4), (11, 23, 3), (16, 16, 2)):
        pts = [(cx, cy - size), (cx + size - 1, cy), (cx, cy + size), (cx - size + 1, cy)]
        cv.poly(pts, DRAGON_CRYSTAL[3])
        cv.poly([(cx, cy - size + 1), (cx + size - 2, cy), (cx, cy + size - 1), (cx - size + 2, cy)],
                DRAGON_CRYSTAL[1])
        cv.poly([(cx, cy - size + 1), (cx + 1, cy), (cx, cy + 1), (cx - 1, cy)], DRAGON_CRYSTAL[0])
        cv.px(cx - 1, cy - size + 2, lighten(DRAGON_CRYSTAL[0], 0.5))
        cv.px(cx, cy - size - 1, lighten(DRAGON_CRYSTAL[0], 0.25))
    cv.save(os.path.join(OUT, "dragon_crystal_ore.png"))


# ---------------------------------------------------------------- 朱红柱
def crimson_pillar():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, RED_LACQUER[2])
    rnd = random.Random(19)
    # 木纹（细直纹，低对比）/ subtle straight grain
    for x in range(32):
        if x % 6 == 0:
            for y in range(32):
                cv.px(x, y, mix(RED_LACQUER[2], RED_LACQUER[3], 0.35))
        elif x % 6 == 3:
            for y in range(32):
                cv.px(x, y, mix(RED_LACQUER[2], RED_LACQUER[1], 0.3))
    speckle(cv, 0, 0, 31, 31, RED_LACQUER[3], RED_LACQUER[1], seed=27, density=0.05)
    cv.px(6, 12, darken(RED_LACQUER[3], 0.25))     # 一处小疤 / small knot
    cv.px(7, 12, darken(RED_LACQUER[3], 0.15))
    cv.rect(0, 0, 31, 1, GOLD_TRIM)
    cv.rect(0, 30, 31, 31, darken(GOLD_TRIM, 0.45))
    cv.line(0, 2, 31, 2, darken(GOLD_TRIM, 0.3))
    cv.line(0, 29, 31, 29, darken(GOLD_TRIM, 0.6))
    save(cv, "crimson_pillar_side")

    top = Cv(S, S)
    top.rect(0, 0, 31, 31, darken(RED_LACQUER[3], 0.35))       # 柱侧 / shaft edge
    top.disc(15.5, 15.5, 13, mix(RED_LACQUER[1], RED_LACQUER[2], 0.4))   # 断面 / cut face
    top.ring(15.5, 15.5, 13, darken(RED_LACQUER[3], 0.25))
    top.ring(15.5, 15.5, 9, mix(RED_LACQUER[2], RED_LACQUER[1], 0.45))
    top.px(15, 15, GOLD_TRIM)                                   # 金心 / gold pin
    top.px(14, 15, GOLD[0])
    top.px(16, 15, GOLD[2])
    top.px(15, 14, GOLD[0])
    top.px(15, 16, GOLD[2])
    save(top, "crimson_pillar_top")


# ---------------------------------------------------------------- 宫灯
def imperial_lantern():
    cv = Cv(S, S)
    cv.rect(8, 0, 23, 2, GOLD_DARK)
    cv.rect(9, 1, 22, 1, GOLD_TRIM)
    cv.disc(15.5, 15, 11, RED_SILK[1])
    cv.disc(15.5, 15, 10, RED_SILK[0])
    for i in range(7):
        x = 6 + i * 3
        cv.line(x, 7, x, 23, RED_SILK[2] if i % 2 else RED_SILK[3])
    cv.disc(15.5, 15, 4, LAMP_GLOW)
    cv.disc(15.5, 15, 2, lighten(LAMP_GLOW, 0.55))
    cv.line(15, 7, 15, 23, lighten(RED_SILK[0], 0.35))
    cv.rect(9, 25, 22, 26, GOLD_TRIM)
    cv.rect(9, 26, 22, 26, GOLD_DARK)
    cv.line(13, 27, 15, 31, GOLD_TRIM)
    cv.line(18, 27, 16, 31, GOLD_TRIM)
    save(cv, "imperial_lantern")


# ---------------------------------------------------------------- 传送门
def portals():
    def rift(bg, dark_c, mid_c, bright_c, core_c, seed):
        cv = Cv(S, S)
        cv.rect(0, 0, 31, 31, bg)
        rnd = random.Random(seed)
        for i in range(34):                                   # 星屑 / motes
            cv.px(rnd.randrange(32), rnd.randrange(32), mid_c if rnd.random() < 0.5 else dark_c)
        # 三条明亮弧纹 / three bright wisps
        for ox, amp, phase in ((6, 7, 0.0), (14, 6, 1.6), (23, 7, 3.0)):
            pts = []
            for t in range(0, 24):
                yy = 4 + t
                xx = ox + math.sin(phase + t * 0.32) * amp * 0.5
                pts.append((int(xx), int(yy)))
            for i in range(len(pts) - 1):
                d = abs(pts[i][0] - 15.5) / 15.0
                col = mix(bright_c, dark_c, min(1.0, d * 0.75))
                cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], col)
                cv.px(pts[i][0] + 1, pts[i][1], mix(col, dark_c, 0.4))
        # 中央光晕 / central bloom
        for r, col in ((11, mix(mid_c, bright_c, 0.2)), (8, mix(mid_c, bright_c, 0.5)),
                       (5, bright_c), (3, core_c), (1, (255, 255, 255, 250))):
            cv.disc(15.5, 15.5, r, col)
        return cv

    rift(JADE[2], JADE[3], JADE[1], JADE_LIGHT, PORTAL_JADE,
         23).save(os.path.join(OUT, "jade_portal.png"))
    rift(mix(DRAGON_CRYSTAL[2], (30, 12, 40, 255), 0.5), darken(DRAGON_CRYSTAL[3], 0.3),
         DRAGON_CRYSTAL[2], lighten(DRAGON_CRYSTAL[0], 0.35), PORTAL_UNDERWORLD,
         29).save(os.path.join(OUT, "underworld_portal.png"))


# ---------------------------------------------------------------- 深板岩（纵向纹理）
def deepslate_base(seed):
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, DEEPSLATE[1])
    for x in range(32):
        m = x % 9
        if m in (0, 1):
            for y in range(32):
                cv.px(x, y, DEEPSLATE[2])
        elif m == 5:
            for y in range(32):
                cv.px(x, y, DEEPSLATE[0])
    speckle(cv, 0, 0, 31, 31, DEEPSLATE[2], DEEPSLATE[0], seed=seed, density=0.07)
    rnd = random.Random(seed + 5)
    for _ in range(4):
        x, y = rnd.randrange(2, 28), rnd.randrange(2, 28)
        cv.line(x, y, x, y + rnd.randrange(2, 5), darken(DEEPSLATE[3], 0.15))
    block_edge(cv, DEEPSLATE, 0.16, 0.24)
    return cv


# ---------------------------------------------------------------- 龙椅
def dragon_throne():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, GOLD_DARK)
    cv.rect(2, 2, 29, 29, GOLD[1])
    cv.rect(3, 3, 28, 28, GOLD[0])
    cv.rect(5, 5, 26, 20, RED_SILK[1])        # 靠背 / backrest
    cv.rect(6, 6, 25, 19, RED_SILK[0])
    for y in range(6, 20, 4):
        cv.line(6, y, 25, y, RED_SILK[2])
    # 龙首纹 / dragon motif
    cv.line(11, 16, 15, 12, GOLD[0])
    cv.line(15, 12, 20, 16, GOLD[0])
    cv.px(15, 11, lighten(GOLD[0], 0.5))
    cv.px(13, 14, GOLD[2])
    cv.px(17, 14, GOLD[2])
    cv.rect(4, 21, 27, 24, RED_SILK[1])       # 座面 / seat
    cv.rect(5, 22, 26, 23, RED_SILK[0])
    cv.rect(2, 25, 29, 29, GOLD[2])           # 底座 / base
    cv.rect(4, 26, 27, 28, GOLD[0])
    for x in range(5, 27, 4):
        cv.px(x, 27, lighten(GOLD[0], 0.45))
    cv.frame(0, 0, 31, 31, darken(GOLD_DARK, 0.35))
    save(cv, "dragon_throne")


# ---------------------------------------------------------------- 祭坛
def altar():
    cv = stone_base(MARBLE, 61)
    # 八边形金嵌 / octagonal gold inlay
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x0, y0 = 15.5 + math.cos(rad) * 11, 15.5 + math.sin(rad) * 11
        rad2 = math.radians(a + 45)
        x1, y1 = 15.5 + math.cos(rad2) * 11, 15.5 + math.sin(rad2) * 11
        cv.line(int(x0), int(y0), int(x1), int(y1), GOLD_TRIM)
    cv.ring(15.5, 15.5, 8, MARBLE_VEIN)
    cv.ring(15.5, 15.5, 7, GOLD[2])
    # 四向刻纹 / carved notches
    for dx, dy in ((0, -5), (0, 5), (-5, 0), (5, 0)):
        cv.rect(15 + dx - 2, 15 + dy, 15 + dx + 2, 15 + dy, darken(GOLD_TRIM, 0.35))
        cv.px(15 + dx, 15 + dy - 1, MARBLE[0])
    cv.disc(15.5, 15.5, 3, hx("B22A20"))
    cv.disc(15.5, 15.5, 1, hx("FFE08A"))
    cv.frame(0, 0, 31, 31, MARBLE[3])
    save(cv, "altar")


# ---------------------------------------------------------------- 编钟
def chime_bell():
    cv = Cv(S, S)
    cv.ring(15.5, 4, 3, GOLD_DARK)
    cv.rect(13, 4, 18, 6, BRONZE[2])
    for y in range(6, 12):
        half = int(2 + (y - 6) * 1.6)
        cv.rect(15 - half, y, 15 + half, y, BRONZE[1])
    for y in range(12, 26):
        half = int(7 + (y - 12) * 0.5)
        cv.rect(15 - half, y, 15 + half, y, BRONZE[1])
    for y in range(6, 26, 4):
        half = int(3 + (y - 6) * 0.85)
        cv.rect(15 - half, y, 15 + half, y, BRONZE_PATINA)
    cv.line(9, 8, 7, 25, lighten(BRONZE[0], 0.4))
    cv.line(10, 9, 9, 24, lighten(BRONZE[0], 0.2))
    cv.line(22, 9, 24, 24, darken(BRONZE[3], 0.2))
    cv.rect(7, 25, 24, 27, BRONZE[2])
    cv.rect(8, 26, 23, 26, BRONZE[0])
    cv.px(12, 24, lighten(BRONZE[0], 0.55))
    save(cv, "chime_bell")


# ---------------------------------------------------------------- 太鼓
def taiko_drum():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, DARK_WOOD[2])
    cv.rect(1, 1, 30, 30, DARK_WOOD[1])
    cv.disc(15.5, 15.5, 13, hx("C9A66B"))          # 鼓面 / drum head
    cv.disc(15.5, 15.5, 12, hx("E5D3A8"))
    cv.disc(15.5, 15.5, 11, hx("D9C08B"))
    cv.ring(15.5, 15.5, 13, hx("8A2F26"))          # 红漆包边 / red binding
    cv.ring(15.5, 15.5, 10, hx("A83A2E"))
    for a in range(0, 360, 45):
        rad = math.radians(a)
        cv.px(int(15.5 + math.cos(rad) * 13), int(15.5 + math.sin(rad) * 13), GOLD_TRIM)
    cv.disc(15.5, 15.5, 4, hx("C2A878"))
    cv.px(13, 12, hx("F0E4C8"))
    cv.frame(0, 0, 31, 31, darken(DARK_WOOD[2], 0.35))
    save(cv, "taiko_drum")


# ---------------------------------------------------------------- 香炉
def incense_burner():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, darken(BRONZE[3], 0.5))
    cv.disc(15.5, 16, 11, BRONZE[2])
    cv.disc(15.5, 15, 10, BRONZE[1])
    cv.disc(13, 12, 4, BRONZE[0])
    for x in range(6, 26, 4):
        cv.rect(x, 12, x + 1, 18, darken(BRONZE[3], 0.25))   # 镂空纹 / pierced holes
    cv.rect(8, 19, 23, 20, GOLD_TRIM)
    cv.rect(9, 21, 22, 22, BRONZE[2])
    for x in (7, 15, 24):
        cv.rect(x, 23, x + 1, 28, BRONZE[2])                 # 三足 / legs
        cv.px(x, 29, BRONZE[3])
    cv.rect(12, 6, 19, 8, GOLD_DARK)                          # 盖 / lid
    cv.rect(13, 5, 18, 6, GOLD_TRIM)
    cv.px(15, 4, GOLD_TRIM)
    cv.rect(13, 15, 18, 17, hx("C0392B"))                     # 香火 / embers
    cv.px(14, 15, hx("F0803A"))
    cv.px(17, 16, hx("FFD27F"))
    save(cv, "incense_burner")


# ---------------------------------------------------------------- 屏风
def screen_block():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, DARK_WOOD[2])
    cv.rect(2, 2, 29, 29, DARK_WOOD[1])
    cv.rect(4, 4, 27, 27, hx("DCE8EC"))
    cv.rect(4, 4, 27, 13, hx("CADFE6"))
    cv.rect(4, 20, 27, 27, hx("C2D6D2"))
    # 层叠远山 / layered misty peaks
    cv.poly([(4, 20), (9, 13), (13, 18), (18, 11), (23, 17), (27, 20), (27, 24), (4, 24)], hx("9CBEB4"))
    cv.poly([(4, 24), (10, 18), (15, 23), (21, 17), (27, 24), (27, 27), (4, 27)], hx("6F9B92"))
    cv.poly([(6, 27), (12, 21), (18, 26), (24, 22), (26, 27)], hx("4E7A6A"))
    cv.line(5, 16, 26, 16, hx("E4EEF0"))          # 云雾 / mist
    cv.line(7, 21, 22, 21, hx("EAF2F2"))
    cv.disc(23, 8, 2, hx("E8C24A"))               # 落日 / sun
    cv.px(22, 7, hx("FFF0B0"))
    cv.rect(4, 4, 27, 4, GOLD_TRIM)
    cv.rect(4, 27, 27, 27, GOLD[2])
    cv.rect(0, 0, 31, 1, DARK_WOOD[0])
    cv.frame(0, 0, 31, 31, darken(DARK_WOOD[2], 0.3))
    save(cv, "screen")


# ---------------------------------------------------------------- 匾额
def plaque():
    cv = Cv(S, S)
    cv.rect(0, 0, 31, 31, DARK_WOOD[3])
    cv.rect(1, 3, 30, 28, DARK_WOOD[1])
    cv.rect(2, 4, 29, 27, hx("3A2414"))
    cv.frame(1, 3, 30, 28, GOLD_TRIM)
    cv.line(2, 4, 29, 4, darken(GOLD_TRIM, 0.3))
    # 三字额（字形各异）/ three distinct gold glyphs
    g1 = [(6, 9, 12, 9), (6, 9, 6, 11), (11, 9, 11, 21), (7, 15, 12, 15), (8, 21, 12, 21)]
    g2 = [(13, 9, 20, 9), (15, 9, 15, 12), (18, 9, 18, 12), (15, 13, 18, 13),
          (16, 15, 16, 21), (14, 21, 19, 21)]
    g3 = [(21, 9, 27, 9), (24, 9, 24, 15), (21, 11, 22, 13), (26, 11, 27, 13),
          (21, 16, 27, 16), (23, 17, 23, 22), (21, 22, 27, 22)]
    for seg in g1 + g2 + g3:
        x0, y0, x1, y1 = seg
        cv.line(x0, y0, x1, y1, GOLD[0])
        cv.px(x0, y0, lighten(GOLD[0], 0.5))
        cv.px(x1, y1, GOLD[2])
    cv.frame(0, 0, 31, 31, darken(DARK_WOOD[3], 0.4))
    save(cv, "plaque")


# ---------------------------------------------------------------- 入口
def main():
    marble()
    palace_bricks()
    stone_base(STONE_GREY, 51).save(os.path.join(OUT, "stone_base.png"))
    jade_block()
    bronze_block()
    ores()
    crimson_pillar()
    imperial_lantern()
    portals()
    dragon_throne()
    altar()
    chime_bell()
    taiko_drum()
    incense_burner()
    screen_block()
    plaque()
    print("blocks done:", len(os.listdir(OUT)))


if __name__ == "__main__":
    main()
