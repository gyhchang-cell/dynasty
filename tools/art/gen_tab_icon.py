"""创造栏封面：把成品画（ChatGPT 出的「金龙抱玉印」）转成模组的封面贴图。

为什么要走这一步 ——
  * 1.20.1 的创造模式物品栏标签页 `icon(...)` 只吃 `ItemStack`（也就是「一件物品」），
    没有「标签页直接贴一张大图」的接口。所以「封面」= 一件专门的物品 + 一张贴图；
  * 源图是**像素画**，但被导成了 784×1168 的 JPEG：原生像素块 ≈ 8×8，也就是说
    原作真正的分辨率只有 ≈ 98×146，其余全是 JPEG 糊出来的过渡色。
    直接把它缩到 32×32，等于每个输出像素要吞掉 2.5 个原作像素 —— 出来就是一坨，
    所以这里**先按 8×8 网格平均一次，把画面还原成 1:1 的像素画**，再谈缩放；
  * 模组的物品贴图是 32×32，但那套规格是为「画出来的一件小东西」定的。
    封面是整幅画的缩略图，按原作网格近 1:1 出图（96×96）才看得出龙鳞与玉印的云雷纹；
    想守规格就用 `--size 32`。

流程：8×8 网格还原 → 抠背景（亮度软阈值）→ 按方案裁成正方形 →
      （必要时）面积平均缩放 → 反预乘还原边缘色 → 调色板收敛 → 透明区补色（防 mipmap 黑边）。

用法：
  python3 tools/art/gen_tab_icon.py                  # 默认方案（整幅 / 96×96），覆盖写入正式贴图
  python3 tools/art/gen_tab_icon.py --sheet          # 只出「方案对比图」，不动正式贴图
  python3 tools/art/gen_tab_icon.py --variant head --size 64
  python3 tools/art/gen_tab_icon.py --list           # 看有哪些方案
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_SOURCE = os.path.join(ROOT, "tools/art/sources/tab_cover_source.jpg")
DEFAULT_OUT = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/item/dynasty_emblem.png")
DEFAULT_PREVIEW_DIR = os.path.join(ROOT, "build/art-preview")

NATIVE_BLOCK = 8     # 源图原生像素块边长（784/98、1168/146）/ the artwork's native pixel block
FG_THRESHOLD = 52    # 亮度阈值：背景 L≈4~38，主体 L≈100+ / background vs subject luminance
FG_SOFT = 26         # 软过渡带宽 / soft ramp width, avoids stair-stepped silhouette
SHEET_BG = (60, 60, 66, 255)   # 预览底色：接近创造栏标签页的灰 / tab-button-ish grey

# 裁切方案（比例都相对「主体外接矩形」）/ crop presets, relative to the subject bbox
VARIANTS = {
    "full": dict(side=1.00, dx=0.00, dy=0.00, label="整幅（龙+印全收）"),
    "zoom": dict(side=0.84, dx=0.02, dy=-0.04, label="近景（稍放大）"),
    "head": dict(side=0.74, dx=0.05, dy=-0.07, label="龙头+玉印特写"),
}


def snap_to_native(rgb, block=NATIVE_BLOCK):
    """把 JPEG 糊过的源图按原生像素网格平均，还原 1:1 像素画。/ de-JPEG back to the art grid."""
    w, h = rgb.size
    return rgb.resize((max(1, round(w / float(block))), max(1, round(h / float(block)))), Image.BOX)


def subject(art, threshold=FG_THRESHOLD, soft=FG_SOFT):
    """返回 (像素画, 软 alpha 掩膜)。/ returns the art image and a soft subject mask."""
    grey = art.convert("L")
    low = threshold - soft
    span = 2.0 * soft

    def ramp(v):
        return 0 if v <= low else (255 if v >= threshold + soft else int((v - low) * 255.0 / span))

    return art, grey.point(ramp)


def fit_box(mask, preset, threshold=24):
    """算出方案对应的正方形裁切框（像素画坐标，尽量留在画内）。/ square crop box on the art grid."""
    solid = mask.point(lambda v: 255 if v > threshold else 0)
    bbox = solid.getbbox()
    if bbox is None:
        raise SystemExit("源图里找不到主体（全是背景？）—— 检查 %s" % (mask.size,))
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    side = int(round(max(w, h) * preset["side"]))     # 取整后再算左上角，保证是正方形
    cx += w * preset["dx"]
    cy += h * preset["dy"]
    left = int(round(cx - side / 2.0))
    top = int(round(cy - side / 2.0))
    box = (left, top, left + side, top + side)
    # 压回画内：正方形不能变形，只能整体平移 / keep it square, just slide it back inside
    iw, ih = mask.size
    bx0, by0, bx1, by1 = box
    if bx0 < 0:
        bx1 -= bx0
        bx0 = 0
    if by0 < 0:
        by1 -= by0
        by0 = 0
    if bx1 > iw:
        bx0 -= bx1 - iw
        bx1 = iw
    if by1 > ih:
        by0 -= by1 - ih
        by1 = ih
    return (max(0, bx0), max(0, by0), min(iw, bx1), min(ih, by1))


def background_color(art):
    """取四角像素的中位数当背景色估计。/ median of the four corners = background estimate."""
    w, h = art.size
    corners = [art.getpixel((2, 2)), art.getpixel((w - 5, 2)),
               art.getpixel((2, h - 5)), art.getpixel((w - 5, h - 5))]
    return tuple(sorted(c[i] for c in corners)[1] for i in range(3))


def body_color(rgb, alpha):
    """主体平均色，用来给透明区补色。/ average subject colour, used to bleed into transparent pixels."""
    px, ap = rgb.load(), alpha.load()
    acc, n = [0, 0, 0], 0
    for y in range(rgb.height):
        for x in range(rgb.width):
            if ap[x, y] > 200:
                c = px[x, y]
                acc[0] += c[0]
                acc[1] += c[1]
                acc[2] += c[2]
                n += 1
    return tuple(v // max(1, n) for v in acc)


def bleed(icon, rounds=2):
    """给全透明像素补上邻近颜色（alpha 仍为 0）。

    Minecraft 的物品贴图会走 mipmap 缩小：透明像素若是纯黑，(R,G,B,A) 平均之后
    会把轮廓压出一圈黑边。补色（dilate）是标准解法。/ dilate colour into transparent area.
    """
    w, h = icon.size
    px = icon.load()
    for _ in range(rounds):
        fills = []
        for y in range(h):
            for x in range(w):
                if px[x, y][3] != 0:
                    continue
                acc, n = [0, 0, 0], 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] != 0:
                        c = px[nx, ny]
                        acc[0] += c[0]
                        acc[1] += c[1]
                        acc[2] += c[2]
                        n += 1
                if n:
                    fills.append((x, y, (acc[0] // n, acc[1] // n, acc[2] // n, 0)))
        for x, y, c in fills:
            px[x, y] = c
    return icon


def render(source, preset, size=96, colors=20, bleed_rounds=2,
           threshold=FG_THRESHOLD, soft=FG_SOFT):
    """按方案把源图转成 size×size 的封面贴图。

    size ≥ 画面网格边长时**不做任何缩放**（1:1 保留原作像素）；
    size 更小时走面积平均降采样。/ 1:1 when size is big enough, area-average otherwise.
    """
    art, mask = subject(snap_to_native(source), threshold, soft)
    box = fit_box(mask, preset)
    sprite = art.crop(box)
    alpha = mask.crop(box)
    side = sprite.width
    bg = background_color(art)

    canvas = size if size else side
    if canvas < side:
        sprite = sprite.resize((canvas, canvas), Image.BOX)
        alpha = alpha.resize((canvas, canvas), Image.BOX)
        side = canvas

    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    src_px, a_px, dst_px = sprite.load(), alpha.load(), out.load()
    for y in range(side):
        for x in range(side):
            a = a_px[x, y]
            if a < 26:                       # 基本是背景 / mostly background
                continue
            if a >= 240:                     # 实心像素，原样 / solid pixel, untouched
                dst_px[x, y] = src_px[x, y] + (255,)
                continue
            cov = a / 255.0                  # 反预乘：c = (mix - (1-cov)*bg) / cov
            dst_px[x, y] = tuple(
                max(0, min(255, int((src_px[x, y][i] - (1 - cov) * bg[i]) / cov))) for i in range(3)
            ) + (a,)

    if colors and colors > 0:
        # 调色板收敛：去掉 JPEG 残留的杂色（中位切分、不抖动，避免边缘起噪点）
        flat = out.convert("RGB").quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
        out = Image.merge("RGBA", (*flat.convert("RGB").split(), out.getchannel("A")))

    bleed(out, bleed_rounds)
    if canvas == side:
        return out

    padded = Image.new("RGBA", (canvas, canvas), (*body_color(out.convert("RGB"), out.getchannel("A")), 0))
    off = (canvas - side) // 2
    padded.paste(out, (off, off))
    bleed(padded, bleed_rounds)
    return padded


def stats(icon):
    """颜色数 / 实心像素数（只数 RGB，跟 ChatGPT 那 6 张同一口径：14~17 色、200~450 实心）。"""
    px = [icon.getpixel((x, y)) for y in range(icon.height) for x in range(icon.width)]
    solid = [p for p in px if p[3] > 200]
    return len({p[:3] for p in solid}), len(solid)


def simulate(icon, logical=16, gui_scale=2):
    """模拟游戏里标签页上的实际观感：逻辑 16px × GUI 缩放。/ how it looks in the tab."""
    return icon.resize((logical * gui_scale, logical * gui_scale), Image.LANCZOS)


def contact_sheet(source, out_dir, size, colors):
    """画一张对比图：源图 + 三个方案的大图 + 标签页里 16×16 的实际观感。

    注：预览底色调成接近标签页的灰，且用 alpha 合成 —— 不然透明区会被存成黑方块，
    根本看不出「贴到游戏里是什么样」。/ composites over tab-like grey, labels stay ASCII
    because PIL's default font has no CJK glyphs.
    """
    scale, pad, thumb_w, sim_cell = 4, 14, 110, 32 * 4
    cell = size * scale
    width = pad + thumb_w + pad + len(VARIANTS) * (cell + pad)
    height = pad + cell + 46 + sim_cell + pad
    sheet = Image.new("RGBA", (width, height), SHEET_BG)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(14)

    thumb = source.convert("RGB").copy()
    thumb.thumbnail((thumb_w, cell))
    sheet.paste(thumb, (pad, pad + (cell - thumb.height) // 2))
    draw.text((pad, pad + cell + 8), "source", fill=(235, 235, 235, 255), font=font)

    for i, name in enumerate(sorted(VARIANTS)):
        icon = render(source, VARIANTS[name], size=size, colors=colors)
        icon.save(os.path.join(out_dir, "variants", "tab_icon_%s.png" % name))
        x = pad + thumb_w + pad + i * (cell + pad)
        big = icon.resize((cell, cell), Image.NEAREST)
        sheet.alpha_composite(big, (x, pad))
        colors_n, solid_n = stats(icon)
        draw.text((x, pad + cell + 8), "%s  %d colours / %d px / %dpx" % (name, colors_n, solid_n, size),
                  fill=(235, 235, 235, 255), font=font)
        gui = simulate(icon).resize((sim_cell, sim_cell), Image.NEAREST)
        sheet.alpha_composite(gui, (x, pad + cell + 30))

    path = os.path.join(out_dir, "tab-icon-sheet.png")
    sheet.convert("RGB").save(path)
    return path


def main():
    parser = argparse.ArgumentParser(description="成品画 → 创造栏封面贴图")
    parser.add_argument("--source", default=DEFAULT_SOURCE,
                        help="源图（默认 tools/art/sources/tab_cover_source.jpg）")
    parser.add_argument("--out", default=DEFAULT_OUT, help="正式贴图输出路径")
    parser.add_argument("--variant", default="full", choices=sorted(VARIANTS), help="裁切方案")
    parser.add_argument("--size", type=int, default=96,
                        help="画布边长：≥ 画面网格时 1:1 不缩放（默认 96）；给 32 就是模组常规规格")
    parser.add_argument("--colors", type=int, default=20, help="调色板颜色数（0=不收敛）")
    parser.add_argument("--sheet", action="store_true", help="只出对比图，不覆盖正式贴图")
    parser.add_argument("--preview-dir", default=DEFAULT_PREVIEW_DIR)
    parser.add_argument("--list", action="store_true", help="列出方案")
    args = parser.parse_args()

    if args.list:
        for name in sorted(VARIANTS):
            preset = VARIANTS[name]
            print("%-6s %-24s side=%.2f dx=%+.2f dy=%+.2f"
                  % (name, preset["label"], preset["side"], preset["dx"], preset["dy"]))
        return

    if not os.path.exists(args.source):
        raise SystemExit("源图不存在：%s" % args.source)
    source = Image.open(args.source).convert("RGB")
    os.makedirs(os.path.join(args.preview_dir, "variants"), exist_ok=True)

    sheet = contact_sheet(source, args.preview_dir, args.size, args.colors)
    print("方案对比图：%s" % os.path.relpath(sheet, ROOT))

    if args.sheet:
        return
    icon = render(source, VARIANTS[args.variant], size=args.size, colors=args.colors)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    icon.save(args.out)
    colors_n, solid_n = stats(icon)
    print("封面贴图：%s（%d×%d，%d 色，%d 实心像素，方案 %s）"
          % (os.path.relpath(args.out, ROOT), icon.width, icon.height, colors_n, solid_n, args.variant))


if __name__ == "__main__":
    sys.exit(main())
