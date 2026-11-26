"""Inspect production bridge and underfloor cells without launching Java."""
from collections import Counter
import json

from review_chensha_architecture import load_coordinates


def main():
    _, piece, _, _, _ = load_coordinates()
    spans = [(x, z, "X") for x in (20, 40) for z in (38, 58, 78)]
    spans.extend([(30, 68, "Z"), (8, 48, "Z"), (50, 48, "Z")])
    bridges = []
    for x, z, axis in spans:
        footprint = [(a, b) for a in range(x, x + 4) for b in range(z, z + 4)]
        deck = Counter(piece.cell(a, 24, b) for a, b in footprint)
        below = Counter(piece.cell(a, 23, b) for a, b in footprint)
        chains = Counter(
            state for a, b in footprint for y in range(25, 29)
            if (state := piece.cell(a, y, b)) and state.startswith("CHAIN")
        )
        lanes = [
            [(x + step, z + offset) if axis == "X" else (x + offset, z + step)
             for step in range(-1, 5)]
            for offset in (1, 2)
        ]
        assert all(
            piece.cell(a, 24, b) not in (None, "AIR", "WATER")
            and all(piece.cell(a, y, b) == "AIR" for y in (25, 26))
            for lane in lanes for a, b in lane
        )
        assert set(deck) <= {"MASONRY_3", "MASONRY_4"}
        assert below == {"AIR": 16}
        assert chains[f"CHAIN[AXIS={axis}]"] and chains["CHAIN[AXIS=Y]"]
        bridges.append({
            "origin_xz": [x, z], "axis": axis, "deck_y24": deck,
            "below_deck_y23": below, "chains": chains, "open_seal_dry_lane_xz": lanes,
        })

    rooms = []
    for z0 in (32, 52, 72):
        for x0 in (4, 24, 44):
            states = Counter(
                piece.cell(x, 23, z)
                for x in range(x0 + 1, x0 + 15)
                for z in range(z0 + 1, z0 + 15)
            )
            rooms.append({"room_corner_xz": [x0, z0], "interior_y23": states})
    print(json.dumps({"bridges": bridges, "room_interiors": rooms}, indent=2))


if __name__ == "__main__":
    main()
