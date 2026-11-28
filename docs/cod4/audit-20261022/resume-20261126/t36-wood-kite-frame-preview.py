"""Render comparable current-asset frames with the existing v43 offline rasterizer."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
spec = spec_from_file_location("wood_kite_preview", ROOT / "tools/art/bestiary-v43/review_wood_kite.py")
preview = module_from_spec(spec)
spec.loader.exec_module(preview)
WOOD = "luban_yisha"
METAL = "luban_yisha_metal"


def strip(selections, yaw, elevation, subset=None):
    output = Image.new("RGB", (1440, 270), "#edf0e9")
    slices = []
    for name, clip, tick, label in selections:
        mesh = preview.q(name, clip, tick)
        if subset:
            mesh = [quad for quad in mesh if subset(quad[2])]
        slices.append((name, mesh, label))
    frame_points = np.concatenate([q[0] for _, mesh, _ in slices for q in mesh])
    for col, (name, mesh, label) in enumerate(slices):
        tex = preview.ASSET / f"textures/entity/blueprint/boss/{name}.png"
        with Image.open(tex) as image:
            atlas = np.array(image.convert("RGB"))
        view = preview.raster(mesh, atlas, yaw=yaw, elevation=elevation, size=(360, 234),
                              mode="lit", frame_points=frame_points)
        output.paste(view, (col * 360, 0))
        ImageDraw.Draw(output).text((col * 360 + 14, 242), label, font=preview.font(17), fill="#263335")
    return output


def main():
    output = Image.new("RGB", (1440, 605), "#edf0e9")
    output.paste(strip([
        (WOOD, "overheat", 0, "0 tick  木壳完整"),
        (WOOD, "overheat", 24, "24 tick  折翼与脱壳起点"),
        (WOOD, "overheat", 47.5, "47.5 tick  木壳将收完"),
        (METAL, "fly", 0, "48 tick  金属飞行首帧基准"),
    ], 37, 6), (0, 40))
    output.paste(strip([
        (WOOD, "bombs", 0, "木形 0 tick  舱门闭合"),
        (WOOD, "bombs", 24, "木形 24 tick  首次投弹"),
        (METAL, "bombs", 24, "金属形 24 tick  舱口敞开"),
        (METAL, "claws", 36, "金属形 36 tick  八爪伸足"),
    ], 19, -24, lambda n: (
        "cassette" in n or "hatch" in n or "claw" in n or "landing" in n)), (0, 318))
    draw = ImageDraw.Draw(output)
    draw.text((16, 7), "鲁班遗煞 · 脱壳与腹部机构 · 软件预览", font=preview.font(22), fill="#263335")
    output.save(OUT / "t36-wood-kite-transition-and-bay.png")


if __name__ == "__main__":
    main()
