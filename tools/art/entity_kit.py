"""生物贴图工具：按模型 UV 逐面绘制。"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *

OUT = os.path.join(os.path.dirname(__file__), "out/entity")
os.makedirs(OUT, exist_ok=True)
INK = (18, 12, 10, 255)


def box(cv, u, v, w, h, d, faces, front_detail=None, side_shade=0.14, top_light=0.2, bottom_dark=0.28):
    """绘制一个立方体展开（前/后/左/右/上/下），front_detail(cv,x0,y0) 可画细节。"""
    top = lighten(faces["main"], top_light)
    bottom = darken(faces["main"], bottom_dark)
    right = darken(faces["main"], side_shade)
    left = darken(faces["main"], side_shade * 1.5)
    back = darken(faces["main"], side_shade * 0.7)
    cv.rect(u + d, v, u + d + w - 1, v + d - 1, top)
    cv.rect(u + d + w, v, u + d + 2 * w - 1, v + d - 1, bottom)
    cv.rect(u, v + d, u + d - 1, v + d + h - 1, right)
    cv.rect(u + d, v + d, u + d + w - 1, v + d + h - 1, faces.get("front", faces["main"]))
    cv.rect(u + d + w, v + d, u + d + w + d - 1, v + d + h - 1, left)
    cv.rect(u + d + w + d, v + d, u + d + w + d + w - 1, v + d + h - 1, back)
    if front_detail:
        front_detail(cv, u + d, v + d)


def face(cv, x, y, eye, brow=None, mouth=None, blush=None, skin=None):
    """在 8x8 头部正面画五官 / paints a face onto an 8x8 head front."""
    cv.rect(x + 1, y + 2, x + 2, y + 3, eye)          # 左眼
    cv.rect(x + 5, y + 2, x + 6, y + 3, eye)
    cv.px(x + 2, y + 2, (255, 255, 255, 200))
    cv.px(x + 6, y + 2, (255, 255, 255, 200))
    if brow:
        cv.line(x + 1, y + 1, x + 2, y + 1, brow)
        cv.line(x + 5, y + 1, x + 6, y + 1, brow)
    if mouth:
        cv.line(x + 3, y + 6, x + 4, y + 6, mouth)
    if blush:
        cv.px(x + 1, y + 5, blush)
        cv.px(x + 6, y + 5, blush)


def humanoid_skin(name, skin_ramp, robe, trim, style, hat_color=None, hair=None, eye=None,
                  armor=False, lamellae=False):
    """生成 64x64 人形生物贴图（对齐原版 HumanoidModel UV）。"""
    cv = Cv(64, 64)
    skin_c = skin_ramp[1] if isinstance(skin_ramp, list) else skin_ramp
    hair_c = hair if hair else skin_ramp[3]
    if isinstance(hair_c, list):
        hair_c = hair_c[3]
    if isinstance(hat_color, list):
        hat_color = hat_color
    eye_c = eye or (30, 30, 40, 255)

    # ---- 头 / head (0,0) 8x8x8 + 帽层 (32,0)
    box(cv, 0, 0, 8, 8, 8, {"main": skin_c, "front": lighten(skin_c, 0.08)})
    cv.rect(0, 0, 31, 15, hair_c)                       # 头发打底
    box(cv, 0, 0, 8, 8, 8, {"main": skin_c, "front": lighten(skin_c, 0.08)})
    cv.rect(0, 0, 7, 1, hair_c)                        # 头顶发
    face(cv, 8, 8, eye_c, brow=hair_c, mouth=(120, 60, 50, 255) if not armor else (90, 50, 45, 255))
    if style == "beard":
        cv.rect(9, 13, 14, 15, hair_c)
    if style == "mustache":
        cv.rect(9, 12, 10, 12, hair_c)
        cv.rect(13, 12, 14, 12, hair_c)
    if style == "mask":                                # 蒙面 / masked
        cv.rect(8, 11, 15, 15, robe[3])
        cv.rect(8, 11, 15, 12, robe[2])
    if style == "honor_guard":                         # 锦衣卫帽 / imperial hat
        cv.rect(32, 0, 63, 15, hat_color[1] if hat_color else robe[2])
        cv.rect(32, 0, 63, 15, darken(robe[2], 0.35))
        cv.rect(40, 8, 47, 15, trim[1])                # 帽檐
        cv.rect(40, 8, 47, 9, trim[0])
        cv.rect(36, 4, 43, 7, trim[2])
    elif style == "crown":                             # 冕冠 / crown
        cv.rect(32, 0, 63, 15, darken(robe[3], 0.4))
        cv.rect(40, 8, 47, 15, GOLD[1])
        cv.rect(40, 8, 47, 9, GOLD[0])
        for x in range(40, 48, 2):
            cv.px(x, 8, lighten(GOLD[0], 0.5))
        cv.rect(36, 2, 43, 5, GOLD_TRIM)               # 冕板
    elif style == "hood":                              # 兜帽
        cv.rect(32, 0, 63, 15, darken(robe[2], 0.3))
        cv.rect(40, 8, 47, 15, darken(robe[3], 0.25))
    elif style == "topknot":                           # 发髻
        cv.rect(32, 0, 63, 15, hair_c)
        cv.rect(42, 2, 45, 4, darken(hair_c, 0.25))
        cv.px(43, 1, lighten(hair_c, 0.3))
    elif style == "helmet":                            # 头盔
        cv.rect(32, 0, 63, 15, trim[1])
        cv.rect(40, 8, 47, 15, trim[1])
        cv.rect(40, 10, 47, 15, darken(trim[2], 0.35))
        cv.rect(41, 9, 46, 9, lighten(trim[0], 0.4))
        cv.rect(37, 3, 42, 6, robe[1])

    # ---- 躯干 / body (16,16) 8x12x4
    def body_detail(c, x, y):
        c.rect(x, y, x + 7, y + 1, robe[1])            # 衣领
        c.rect(x + 2, y + 2, x + 5, y + 9, robe[2])    # 前襟
        c.line(x + 4, y + 2, x + 4, y + 11, trim[1])   # 中缝
        if armor:
            for i in range(3):                          # 甲片 / lamellar rows
                c.rect(x, y + 3 + i * 3, x + 7, y + 4 + i * 3, darken(trim[3], 0.3))
                c.line(x + 1, y + 5 + i * 3, x + 6, y + 5 + i * 3, trim[1])
        if lamellae:
            for i in range(4):
                c.rect(x + 1, y + 3 + i * 2, x + 6, y + 3 + i * 2, darken(robe[3], 0.2))
        c.rect(x, y + 10, x + 7, y + 11, trim[1])      # 腰带
        c.rect(x + 3, y + 10, x + 4, y + 11, trim[0])
    box(cv, 16, 16, 8, 12, 4, {"main": robe[2]}, front_detail=body_detail)

    # ---- 手臂 / arms (40,16) 4x12x4
    def arm_detail(c, x, y):
        c.rect(x, y, x + 3, y + 6, robe[2])            # 袖
        c.rect(x, y + 7, x + 3, y + 11, skin_c)        # 手 / hand
        c.line(x, y + 7, x + 3, y + 7, trim[1])
        c.px(x, y + 8, lighten(skin_c, 0.2))
    box(cv, 40, 16, 4, 12, 4, {"main": robe[2]}, front_detail=arm_detail)

    # ---- 腿 / legs (0,16) 4x12x4
    def leg_detail(c, x, y):
        c.rect(x, y, x + 3, y + 8, robe[3])            # 裤
        c.rect(x, y + 9, x + 3, y + 11, darken(trim[3], 0.4))   # 靴 / boots
        c.line(x, y + 9, x + 3, y + 9, trim[2])
    box(cv, 0, 16, 4, 12, 4, {"main": robe[3]}, front_detail=leg_detail)

    cv.outline(INK)
    cv.save(os.path.join(OUT, name + ".png"))
    return cv
