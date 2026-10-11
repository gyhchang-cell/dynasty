"""Software cuboid views from actual Java vertices, plus separate native contacts.

These diagnostic views are NOT native-game captures. No production PNG texture
is created or changed. Vanilla held item layers are checked in native images.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/art/guard-proportion-v3"
FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def body_view(mesh, angle, black=False):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    all_vertices = [p for cube in mesh["cubes"] for p in cube["vertices"]]
    low, high = min(p[1] for p in all_vertices), max(p[1] for p in all_vertices)
    radius = max(math.hypot(p[0], p[2]) for p in all_vertices)
    scale = min(340 / (radius * 2), 420 / (high - low))
    y_offset = (480 - (high - low) * scale) / 2 - low * scale
    faces = []
    for cube in mesh["cubes"]:
        points = [(p[0] * c - p[2] * s, p[1], p[0] * s + p[2] * c) for p in cube["vertices"]]
        color = tuple((cube["color"] >> shift) & 255 for shift in [16, 8, 0])
        for face in FACES:
            v = [points[i] for i in face]
            faces.append((sum(p[2] for p in v) / 4, v, color))
    img = Image.new("RGB", (380, 480), "white" if black else (235, 237, 239))
    draw = ImageDraw.Draw(img)
    for _, vertices, color in sorted(faces, reverse=True, key=lambda f: f[0]):
        draw.polygon([(190 + p[0] * scale, y_offset + p[1] * scale) for p in vertices], fill=(0, 0, 0) if black else color)
    return img


def main():
    (OUT / "views").mkdir(exist_ok=True)
    native = OUT / "native/guard-proportion-final-02"
    sheet = Image.new("RGB", (1900, 2040), "white")
    draw = ImageDraw.Draw(sheet)
    for row, gear in enumerate(["sword", "crossbow", "shield", "spear"]):
        mesh = json.loads((native / f"{row * 4:02d}-mesh.json").read_text())
        for col, (name, angle, black) in enumerate([("front", 0, False), ("45", 45, False), ("side", 90, False), ("back", 180, False), ("silhouette", 45, True)]):
            img = body_view(mesh, angle, black)
            img.save(OUT / "views" / f"{gear}-{name}.png")
            sheet.paste(img, (col * 380, row * 510 + 30))
            draw.text((col * 380 + 8, row * 510 + 10), f"{gear}: {name} (software body mesh)", fill="black")
    sheet.save(OUT / "views/body-five-views-contact.png")
    stages = [(native, i) for i in range(16)] + [(OUT / "native/guard-proportion-final-02", i) for i in range(19, 29)]
    contact = Image.new("RGB", (2080, 7 * 480), "white")
    draw = ImageDraw.Draw(contact)
    for j, (folder, i) in enumerate(stages):
        f = next(folder.glob(f"{i:02d}-*.png"))
        with Image.open(f) as src:
            # A reversible crop for inspection; raw native capture remains intact.
            crop = src.crop((720, 220, 2080, 1500)).resize((510, 450), Image.Resampling.NEAREST)
        x, y = j % 4 * 520, j // 4 * 480
        contact.paste(crop, (x, y + 25))
        draw.text((x + 6, y + 7), f"Native {folder.name}/{f.name}", fill="black")
    contact.save(OUT / "views/native-contact.png")
    print("Created separate software five-view body diagnostics and native contact sheet; no texture edits.")


if __name__ == "__main__":
    main()
