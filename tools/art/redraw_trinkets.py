#!/usr/bin/env python3
"""第三十四轮：把最近 50 件饰品的贴图**真正画出来**（之前是「复制旧图 + RGB 染色」）。

之前的做法在这批新饰品上有个明显问题：同一张源图被染成 8~10 种颜色，背包里全是「同一个轮廓的
不同颜色」，玩家分不出「破晓刃坠」和「蚀月珠」。这里按**形状类别**逐件重绘 16×16 图标：
戒指 / 吊坠 / 珠 / 印 / 符 / 羽 / 钟鼓 / 手套 / 腰带 / 镜 / 罗盘 / 蝉 / 钥 / 骰，每个形状用对应色阶，
并统一加一圈描边（`Cv.outline`），保证在任何背景上都看得清。

同时输出一张预览页 `docs/贴图预览-第三十四轮.html`（8 倍放大、像素风），方便肉眼验收。

运行：python3 tools/art/redraw_trinkets.py
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import Cv, darken, hx, lighten, ramp  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/item")
PREVIEW = os.path.join(ROOT, "docs/贴图预览-第三十四轮.html")

# 形状 → 画法由下面的 paint_* 实现；id 里的关键词决定用哪种形状
SHAPES = ("ring", "pendant", "bead", "seal", "talisman", "feather", "bell", "glove",
          "belt", "mirror", "compass", "cicada", "key", "die")

# 50 件新饰品：id → (形状, 主色, 点缀色)
ART = {
    # ---- 一、昼夜双生：暖（日）→ 冷（月）----
    "dawn_blade_charm": ("talisman", "F0C88A", "E07A3C"),
    "dusk_veil_charm": ("pendant", "9080C8", "4A3C78"),
    "noon_pendant": ("pendant", "F0E080", "C8A020"),
    "moonlit_mirror": ("mirror", "B0C8F0", "5878B8"),
    "sun_chaser_ring": ("ring", "F0D070", "C88A20"),
    "night_heron_feather": ("feather", "8090C0", "3C4870"),
    "twilight_cicada": ("cicada", "A0B890", "586848"),
    "eclipse_bead": ("bead", "8870B0", "3C2C5C"),
    "dawn_drum": ("bell", "F0D8A0", "B08830"),
    "starless_night_ring": ("ring", "606898", "2A3050"),
    # ---- 二、生死代价：血与骨 ----
    "blood_oath_seal": ("seal", "C05050", "6A1C1C"),
    "bone_reaper_tally": ("talisman", "E0E0D0", "8A8A78"),
    "internal_injury_talisman": ("talisman", "D06070", "7A2028"),
    "lifedrain_ring": ("ring", "B04060", "4C1024"),
    "crimson_pact_charm": ("pendant", "D04050", "701018"),
    "flesh_gamble_dice": ("die", "E0A090", "8A4038"),
    "deathbed_talisman": ("talisman", "E0E0C0", "908C60"),
    "scarlet_lotus": ("bead", "E07080", "8A2438"),
    "blood_iron_sash": ("belt", "A06060", "582828"),
    "soul_candle_charm": ("pendant", "C8B070", "6A5820"),
    # ---- 三、天朝敕令：金玉 ----
    "edict_of_dragon": ("seal", "E0C060", "8A6A10"),
    "edict_of_iron": ("seal", "A8C0D8", "4A6480"),
    "edict_of_swift": ("seal", "B8E0C0", "487850"),
    "edict_of_mandate": ("seal", "F0D890", "96842C"),
    "edict_of_dread": ("seal", "B08090", "543040"),
    "edict_of_loyalty": ("seal", "E8D0A0", "8A7038"),
    "seal_of_two_heavens": ("seal", "F0E0B0", "A08A38"),
    "throne_inheritance_charm": ("pendant", "E0D090", "8A7828"),
    "war_deity_signet": ("ring", "D07060", "6A2418"),
    "unbroken_wall_charm": ("bead", "90A890", "3A5038"),
    # ---- 四、幽冥献祭：暗紫与骨白 ----
    "sacrificial_blade_charm": ("talisman", "906070", "3C1C2C"),
    "nether_binding_ring": ("ring", "505070", "1E1E34"),
    "ghost_ferry_tally": ("talisman", "708070", "2A3A2A"),
    "bone_chill_pendant": ("pendant", "88B0C0", "345868"),
    "candle_of_the_dead": ("bell", "90B080", "405A38"),
    "tomb_warden_seal": ("seal", "809080", "344034"),
    "jade_shroud_charm": ("pendant", "A0C0A8", "3C6444"),
    "karma_ledger_charm": ("talisman", "C8B890", "6A5A34"),
    "abyss_pearl": ("bead", "507090", "16283C"),
    "underworld_gate_key": ("key", "606080", "20203C"),
    # ---- 五、巧匠边塞：工与军 ----
    "ranging_compass_charm": ("compass", "C8B880", "6A5C28"),
    "quickdraw_glove": ("glove", "C09070", "5A3828"),
    "siege_hammer_charm": ("bell", "A08060", "4A3420"),
    "dusk_raider_badge": ("seal", "8070A0", "382A58"),
    "rain_prayer_knot": ("belt", "80A8C8", "2C4E6A"),
    "diver_signet": ("ring", "70B0B0", "205454"),
    "cavalry_sash": ("belt", "B08860", "543C20"),
    "wound_binder_charm": ("belt", "E0D8C8", "8A8070"),
    "iron_ration_charm": ("bead", "C8B088", "5A4828"),
    "warlord_drum_charm": ("bell", "C06050", "5A1E16"),
}


def shades(main, accent):
    """主色/点缀色 → 各自的明暗色阶 / ramps for the item"""
    return ramp(hx(main), 5), ramp(hx(accent), 5)


def paint_ring(c, main, acc):
    c.ring(7, 8, 4, main[2], 2)
    c.ring(7, 8, 4, main[3], 1)
    c.px(7, 3, main[1])
    c.px(7, 4, acc[3])
    c.px(6, 3, acc[2])
    c.px(8, 3, acc[2])
    c.px(7, 11, main[1])


def paint_pendant(c, main, acc):
    c.disc(7, 10, 4, main[2])
    c.disc(7, 9, 3, main[3])
    c.px(6, 8, main[4])
    c.px(6, 9, main[4])
    c.rect(6, 2, 8, 3, acc[3])
    c.rect(7, 3, 7, 6, acc[2])
    c.px(7, 13, main[1])


def paint_bead(c, main, acc):
    c.disc(7, 8, 5, main[2])
    c.disc(6, 7, 4, main[3])
    c.disc(5, 6, 2, main[4])
    c.px(4, 5, lighten(main[4], 0.3))
    c.px(11, 12, main[1])
    c.px(11, 3, acc[3])
    c.px(3, 12, acc[3])


def paint_seal(c, main, acc):
    c.rect(3, 7, 12, 13, main[2])
    c.rect(3, 7, 12, 8, main[3])
    c.rect(3, 12, 12, 13, main[1])
    c.rect(6, 3, 9, 6, acc[3])
    c.rect(7, 2, 8, 2, acc[4])
    c.px(7, 10, acc[4])
    c.px(8, 10, acc[4])
    c.px(7, 11, acc[4])


def paint_talisman(c, main, acc):
    c.rect(5, 2, 10, 13, main[3])
    c.frame(5, 2, 10, 13, main[1])
    c.line(7, 4, 8, 6, acc[3])
    c.line(8, 6, 6, 9, acc[3])
    c.line(6, 9, 8, 11, acc[3])
    c.rect(5, 6, 10, 7, acc[2])
    c.px(6, 3, acc[4])


def paint_feather(c, main, acc):
    c.line(4, 13, 11, 3, acc[2])
    for i, y in enumerate(range(4, 13, 2)):
        c.line(11 - i, y, 8 - i, y + 2, main[2])
        c.line(11 - i, y, 10 - i, y + 3, main[3])
    c.px(11, 3, main[4])
    c.px(4, 13, acc[1])


def paint_bell(c, main, acc):
    c.disc(7, 8, 5, main[3])
    c.rect(3, 8, 11, 11, main[3])
    c.rect(3, 11, 11, 12, main[1])
    c.px(7, 13, main[1])
    c.rect(7, 2, 7, 3, acc[2])
    c.px(6, 5, lighten(main[4], 0.2))
    c.px(9, 7, main[1])


def paint_glove(c, main, acc):
    c.rect(4, 6, 11, 12, main[3])
    c.rect(4, 6, 8, 8, main[4])
    c.rect(9, 4, 11, 7, main[3])
    c.rect(5, 12, 10, 13, main[2])
    c.frame(4, 6, 11, 12, main[1])
    c.rect(4, 9, 11, 9, acc[3])
    c.px(11, 4, acc[4])


def paint_belt(c, main, acc):
    c.line(2, 11, 13, 4, main[3])
    c.line(2, 12, 13, 5, main[2])
    c.line(2, 10, 13, 3, main[4])
    c.rect(6, 6, 9, 9, acc[3])
    c.frame(6, 6, 9, 9, acc[1])
    c.px(7, 7, acc[4])


def paint_mirror(c, main, acc):
    c.disc(7, 7, 5, main[2])
    c.disc(7, 7, 4, main[3])
    c.ring(7, 7, 5, main[1], 1)
    c.disc(5, 5, 1, lighten(main[4], 0.35))
    c.rect(7, 12, 7, 14, acc[2])
    c.px(6, 12, acc[3])
    c.px(8, 12, acc[3])


def paint_compass(c, main, acc):
    c.disc(7, 7, 5, main[3])
    c.ring(7, 7, 5, main[1], 1)
    c.line(7, 3, 7, 11, acc[3])
    c.line(5, 5, 9, 9, acc[1])
    c.px(7, 4, acc[4])
    c.px(4, 7, main[1])
    c.px(10, 7, main[1])


def paint_cicada(c, main, acc):
    c.disc(7, 8, 4, main[3])
    c.px(7, 3, acc[3])
    c.px(6, 4, acc[2])
    c.px(8, 4, acc[2])
    c.line(4, 7, 2, 4, acc[2])
    c.line(10, 7, 12, 4, acc[2])
    c.rect(6, 8, 8, 10, acc[3])
    c.px(6, 12, main[1])


def paint_key(c, main, acc):
    c.ring(5, 5, 3, main[3], 2)
    c.px(5, 5, main[1])
    c.rect(6, 7, 7, 13, main[3])
    c.px(8, 10, main[3])
    c.px(8, 11, main[2])
    c.px(8, 12, main[3])
    c.px(4, 3, acc[3])


def paint_die(c, main, acc):
    c.poly([(3, 6), (7, 3), (12, 6), (8, 9)], main[4])
    c.poly([(3, 6), (8, 9), (8, 14), (3, 11)], main[2])
    c.poly([(12, 6), (8, 9), (8, 14), (12, 11)], main[1])
    c.px(6, 6, acc[4])
    c.px(10, 7, acc[4])
    c.px(5, 10, acc[3])
    c.px(6, 12, acc[3])


PAINTERS = {
    "ring": paint_ring, "pendant": paint_pendant, "bead": paint_bead, "seal": paint_seal,
    "talisman": paint_talisman, "feather": paint_feather, "bell": paint_bell,
    "glove": paint_glove, "belt": paint_belt, "mirror": paint_mirror,
    "compass": paint_compass, "cicada": paint_cicada, "key": paint_key, "die": paint_die,
}


def draw(shape, main_hex, accent_hex):
    """画一枚 16×16 图标（最后统一描一圈边，保证任何背景都看得清）"""
    main, accent = shades(main_hex, accent_hex)
    canvas = Cv(16, 16)
    PAINTERS[shape](canvas, main, accent)
    canvas.outline(darken(main[1], 0.45))
    return canvas


def main():
    drawn = []
    for item_id, (shape, main_hex, accent_hex) in sorted(ART.items()):
        if shape not in PAINTERS:
            print("!! 未知形状：", item_id, shape)
            continue
        canvas = draw(shape, main_hex, accent_hex)
        # 项目里所有贴图都是 32×32：画 16×16 再按最近邻放大一倍，保持像素风且尺寸统一
        canvas.im = canvas.im.resize((32, 32), Image.NEAREST)
        canvas.im.save(os.path.join(TEX, item_id + ".png"))
        drawn.append((item_id, shape, main_hex))
    shapes = "、".join(sorted({row[1] for row in drawn}))
    print("重绘贴图：%d 件，形状 %d 类（%s）" % (len(drawn), len({row[1] for row in drawn}), shapes))

    rows = "\n".join(
        '<figure><img src="../src/main/resources/assets/dynasty/textures/item/%s.png" alt="%s">'
        '<figcaption>%s<br><small>%s · #%s</small></figcaption></figure>' % row * 1
        for row in [(item_id, item_id, item_id, shape, main_hex) for item_id, shape, main_hex in drawn])
    html = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>第三十四轮饰品贴图预览</title>
<style>
 body { font: 14px/1.5 system-ui, "PingFang SC", sans-serif; margin: 24px; }
 h1 { font-size: 18px; }
 p.muted { opacity: .7; }
 .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 14px; }
 figure { margin: 0; text-align: center; border: 1px solid #8883; border-radius: 10px; padding: 10px 6px; }
 img { width: 64px; height: 64px; image-rendering: pixelated; }
 figcaption { font-size: 12px; margin-top: 6px; word-break: break-all; }
 small { opacity: .65; }
</style></head><body>
<h1>第三十四轮 · 50 件饰品贴图预览（16×16，放大 8 倍）</h1>
<p class="muted">这批是<b>按形状重绘</b>的（戒指 / 吊坠 / 珠 / 印 / 符 / 羽 / 钟 / 手套 / 腰带 / 镜 / 罗盘 / 蝉 / 钥 / 骰），
不再是「同一张图染色」。觉得哪件不像，改 <code>tools/art/redraw_trinkets.py</code> 里的 ART 表再重跑即可。</p>
<div class="grid">
%s
</div></body></html>
""" % rows
    with open(PREVIEW, "w", encoding="utf-8") as handle:
        handle.write(html)
    print("预览页：", os.path.relpath(PREVIEW, ROOT))


if __name__ == "__main__":
    main()
