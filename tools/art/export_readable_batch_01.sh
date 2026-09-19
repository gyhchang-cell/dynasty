#!/bin/sh
# Export exactly these three individually designed sprites; no other textures are touched.
set -eu
ART_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
for item in alchemy_furnace_charm jade_ruyi wine_gourd; do
    magick "$ART_REPO/docs/art/readable-batch-01/sources/$item.png" \
        -channel A -threshold 50% +channel -trim +repage \
        -sample 28x28 -gravity center -background none -extent 32x32 \
        +dither -colors 20 \
        "PNG32:$ART_REPO/src/main/resources/assets/dynasty/textures/item/$item.png"
done
