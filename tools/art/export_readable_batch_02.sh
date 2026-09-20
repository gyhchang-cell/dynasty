#!/bin/sh
# Export only the three individually generated sprites in batch 02.
set -eu
ART_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ART_DEST=${1:-"$ART_REPO/src/main/resources/assets/dynasty/textures/item"}
mkdir -p "$ART_DEST"
for item in phoenix_hairpin bagua_mirror tiger_tally; do
    magick "$ART_REPO/docs/art/readable-batch-02/sources/$item.png" \
        -channel A -threshold 50% +channel -trim +repage \
        -sample 60x60 -gravity center -background none -extent 64x64 \
        +dither -colors 48 "PNG32:$ART_DEST/$item.png"
done
