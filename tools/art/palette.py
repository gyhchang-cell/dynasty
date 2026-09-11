"""王朝调色板：全局统一的材质色。/ Dynasty global material palettes."""
from artlib import hx, ramp

# ---- 石材 / stone ----
MARBLE = ramp(hx("E9E5DB"), 6)          # 汉白玉
MARBLE_VEIN = hx("BFB6A4")
PALACE_BRICK = ramp(hx("9C332A"), 6)    # 宫墙砖（朱红）
STONE_GREY = ramp(hx("8A8A88"), 6)      # 普通石
DEEPSLATE = ramp(hx("54545A"), 6)       # 深板岩
BRICK_MORTAR = hx("5E1D18")

# ---- 金属 / metals ----
BRONZE = ramp(hx("B07A3C"), 6)
BRONZE_PATINA = hx("4E7C63")
SILVER = ramp(hx("C6CBD1"), 6)
GOLD = ramp(hx("E8C24A"), 6)
GOLD_DARK = hx("8A6A16")
IRON = ramp(hx("D8D8D8"), 5)

# ---- 玉石与宝石 / jade & gems ----
JADE = ramp(hx("58B477"), 6)
JADE_LIGHT = hx("A9E8BC")
DRAGON_CRYSTAL = ramp(hx("A44FE0"), 6)
CINNABAR = ramp(hx("C0392B"), 5)

# ---- 木材与织物 / wood & cloth ----
WOOD = ramp(hx("8A5A32"), 6)
DARK_WOOD = ramp(hx("5A3A22"), 5)
RED_LACQUER = ramp(hx("A82C24"), 6)
RED_SILK = ramp(hx("C8402F"), 6)
GOLD_TRIM = hx("E8C86A")
PURPLE_SILK = ramp(hx("6B3E8F"), 5)
BLACK_CLOTH = ramp(hx("3A3A44"), 5)
GREEN_CLOTH = ramp(hx("4E7A4A"), 5)
LEATHER = ramp(hx("8A6440"), 5)
BONE = ramp(hx("D8CDA8"), 5)

# ---- 光与焰 / light & flame ----
LAMP_GLOW = hx("FFE9A8")
FIRE = ramp(hx("F0803A"), 5)
PORTAL_JADE = hx("7CE8B0")
PORTAL_UNDERWORLD = hx("8A3FD0")

# ---- 皮肤 / skin ----
SKIN = ramp(hx("D9A57A"), 5)
SKIN_ASH = ramp(hx("9A8B7A"), 5)
SKIN_JADE = ramp(hx("8FBF9A"), 5)


def tint(base_ramp, color, amount=0.35):
    """给色阶整体偏向某色 / tints a ramp towards a colour."""
    from artlib import mix
    return [mix(c, color, amount) for c in base_ramp]
