"""预览拼图工具 / contact-sheet preview helper."""
import os
from PIL import Image, ImageDraw


def sheet(items, out, zoom=6, cols=8):
    """items: [(label, PIL.Image)] -> 生成带标签的预览图。"""
    if not items:
        return
    cellw = max(im.width for _, im in items) * zoom + 10
    cellh = max(im.height for _, im in items) * zoom + 22
    rows = (len(items) + cols - 1) // cols
    sheet_im = Image.new("RGBA", (cellw * cols, cellh * rows), (26, 26, 32, 255))
    dr = ImageDraw.Draw(sheet_im)
    for i, (label, im) in enumerate(items):
        cx = (i % cols) * cellw
        cy = (i // cols) * cellh
        # 棋盘底 / checkerboard backdrop
        for yy in range(0, im.height * zoom, zoom * 2):
            for xx in range(0, im.width * zoom, zoom * 2):
                dr.rectangle([cx + 5 + xx, cy + 5 + yy, cx + 5 + xx + zoom - 1, cy + 5 + yy + zoom - 1],
                             fill=(60, 60, 70, 255))
        big = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        sheet_im.alpha_composite(big, (cx + 5, cy + 5))
        dr.text((cx + 5, cy + 8 + im.height * zoom), label[:18], fill=(240, 240, 240, 255))
    sheet_im.save(out)
