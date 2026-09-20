#!/bin/sh
# Export current versions of these three weapons; Houyi bow now has four V2 frames.
set -eu
ART_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ART_DEST=${1:-"$ART_REPO/src/main/resources/assets/dynasty/textures/item"}
mkdir -p "$ART_DEST"
for item in longyuan_sword leiting_hammer; do
    magick "$ART_REPO/docs/art/weapon-batch-01/sources/$item.png" \
        -channel A -threshold 50% +channel -trim +repage \
        -sample 60x60 -gravity center -background none -extent 64x64 \
        +dither -colors 48 "PNG32:$ART_DEST/$item.png"
done
sh "$ART_REPO/tools/art/export_houyi_bow_v2.sh" "$ART_DEST"
