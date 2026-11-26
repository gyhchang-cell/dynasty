"""Check the existing production floors under open seals. Run from project root.

Use the dependencies pinned in tools/blueprint/chensha-review-requirements.txt.
This script prints evidence and never writes the historical review directory.
"""
from collections import deque
from functools import lru_cache
import json

from review_chensha_architecture import load_coordinates


def main():
    _, piece, _, _, _ = load_coordinates()
    cell = lru_cache(None)(piece.cell)

    def standable(x, z):
        floor = cell(x, 24, z)
        return (
            all(cell(x, y, z) == "AIR" for y in (25, 26))
            and floor not in (None, "AIR", "WATER")
            and not floor.startswith("CHAIN")
        )

    start = (32, 60)
    assert standable(*start)
    seen = {start}
    queue = deque([start])
    while queue:
        x, z = queue.popleft()
        for next_x, next_z in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            point = (next_x, next_z)
            if (
                5 <= next_x <= 58
                and 33 <= next_z <= 86
                and point not in seen
                and standable(*point)
            ):
                seen.add(point)
                queue.append(point)

    goals = [
        (12, 40), (32, 40), (52, 40),
        (12, 53), (32, 60), (52, 53),
        (12, 80), (32, 84), (52, 80),
    ]
    assert all(point in seen for point in goals)
    print(json.dumps({
        "foot_y": 25,
        "start_xz": start,
        "dry_reachable_positions": len(seen),
        "all_nine_reached": True,
        "room_points": [
            {"xz": point, "below_deck_y23": cell(point[0], 23, point[1])}
            for point in goals
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
