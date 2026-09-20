#!/bin/sh
# Mechanical game-format export. Preserve generated alpha, keep a 2px safety border.
set -eu
ART_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
for item in tianzi_sword qinglong_dao; do
    magick "$ART_REPO/docs/art/guanyu-weapons-v1/sources/$item.png" \
        -trim +repage -filter point -resize 124x124 -gravity center \
        -background none -extent 128x128 \
        "PNG32:$ART_REPO/src/main/resources/assets/dynasty/textures/item/$item.png"
done
