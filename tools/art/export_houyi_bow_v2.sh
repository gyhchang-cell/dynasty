#!/bin/sh
# Export the four matching Houyi bow frames; preserve hard pixel edges and alpha.
set -eu
ART_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ART_DEST=${1:-"$ART_REPO/src/main/resources/assets/dynasty/textures/item"}
mkdir -p "$ART_DEST"
for frame in houyi_bow houyi_bow_pulling_0 houyi_bow_pulling_1 houyi_bow_pulling_2; do
    magick "$ART_REPO/docs/art/houyi-bow-v2/sources/$frame.png" \
        -channel A -threshold 50% +channel -trim +repage \
        -sample 60x60 -gravity center -background none -extent 64x64 \
        +dither -colors 48 "PNG32:$ART_DEST/$frame.png"
done
