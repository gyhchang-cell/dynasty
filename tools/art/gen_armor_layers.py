"""护甲层贴图（64x32，兼容原版人形护甲 UV 布局）。"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/armor")
os.makedirs(OUT, exist_ok=True)


def armor_layer(name, main, trim, accent, plate_lines=True):
    """整幅覆盖：任何 UV 区域都会得到合理配色 + 甲片纹路。"""
    cv = Cv(64, 32)
    for y in range(32):
        for x in range(64):
            t = y / 31.0
            cv.px(x, y, mix(lighten(main[1], 0.18), darken(main[3], 0.15), t))
    if plate_lines:
        for y in range(0, 32, 6):                      # 甲片分界 / plate seams
            for x in range(64):
                cv.px(x, y, darken(main[3], 0.35))
                if y + 1 < 32:
                    cv.px(x, y + 1, lighten(main[1], 0.2))
    for y in range(2, 32, 8):                          # 铆钉 / studs
        for x in range(2, 64, 8):
            cv.px(x, y, trim[0])
            cv.px(x, y + 1, darken(trim[2], 0.2))
    for x in range(0, 64, 16):                         # 纵向高光 / vertical sheen
        for y in range(32):
            if x + 1 < 64:
                cv.px(x, y, lighten(cv.get(x, y), 0.12))
    # 腰带 / 束带带（v=18..20 会落在躯干下部与腿部）
    for x in range(64):
        cv.px(x, 18, trim[1])
        cv.px(x, 19, trim[0])
        cv.px(x, 20, darken(trim[2], 0.25))
    # 胸口纹章（body front 区域 20..27 x 20..31）
    for y in range(23, 29):
        for x in range(21, 27):
            cv.px(x, y, accent)
    for x in range(21, 27):
        cv.px(x, 23, lighten(accent, 0.35))
        cv.px(x, 28, darken(accent, 0.3))
    # 肩甲加亮（arm 区域 40..55 x 16..31）
    for y in range(16, 32):
        for x in range(40, 56):
            cv.px(x, y, lighten(cv.get(x, y), 0.08))
    rnd = random.Random(7)
    for _ in range(60):                                # 磨损 / wear
        cv.px(rnd.randrange(64), rnd.randrange(32), darken(main[3], 0.3))
    cv.save(os.path.join(OUT, name + ".png"))


if __name__ == "__main__":
    sets = {
        "jade": (JADE, GOLD, hx("A9E8BC")),
        "dragon_scale": (DRAGON_CRYSTAL, BRONZE, lighten(DRAGON_CRYSTAL[0], 0.4)),
        "general": (ramp(hx("5A6472"), 5), GOLD, hx("C0392B")),
    }
    for prefix, (main, trim, accent) in sets.items():
        armor_layer(prefix + "_layer_1", main, trim, accent)
        armor_layer(prefix + "_layer_2", main, trim, accent, plate_lines=False)
    print("armor layers done:", len(os.listdir(OUT)))
