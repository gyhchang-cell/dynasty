"""Inspect the existing hall's column rows and dry route in production voxels."""
import json
import re

from build_wangsi import AIR, JAVA, RED, STONE, WOOD, outputs


def main():
    source, _ = outputs()
    assert source == JAVA.read_text()
    boxes = [
        tuple(map(int, row.split(",")))
        for row in re.findall(r"\{(\d+,\d+,\d+,\d+,\d+,\d+,\d+)\}", source)
    ]

    def cell(x, y, z):
        for a, b, c, d, e, f, state in reversed(boxes):
            if a <= x <= d and b <= y <= e and c <= z <= f:
                return state
        return None

    rows = []
    for x in (32, 64):
        for z in (104, 108, 112, 116):
            assert all(
                cell(a, 17, b) == STONE
                for a in range(x - 1, x + 2) for b in range(z - 1, z + 2)
            )
            assert [cell(x, y, z) for y in range(18, 26)] == [RED] * 8
            assert all(
                cell(a, 26, b) == WOOD
                for a in range(x - 1, x + 2) for b in range(z - 1, z + 2)
            )
            rows.append([x, z])

    route = (
        [(48, z) for z in range(102, 111)]
        + [(x, 110) for x in range(47, 27, -1)]
        + [(28, z) for z in range(111, 119)]
        + [(x, 118) for x in range(29, 49)]
        + [(48, z) for z in range(119, 121)]
    )
    assert all(
        abs(x - a) + abs(z - b) == 1
        for (x, z), (a, b) in zip(route, route[1:])
    )
    assert all(
        cell(x, 16, z) == STONE
        and cell(x, 17, z) == AIR
        and cell(x, 18, z) == AIR
        for x, z in route
    )
    obstructions = [z for z in range(113, 117) if cell(48, 17, z) != AIR]
    assert obstructions == [113, 114, 115, 116]
    print(json.dumps({
        "columns_xz": rows,
        "stone_base_y": 17,
        "red_nether_brick_shaft_y_inclusive": [18, 25],
        "wood_cap_y": 26,
        "dry_route_foot_y": 17,
        "dry_route_xz": route,
        "central_axis_obstructions_z": obstructions,
        "blocked_inside_crossing_at_z117_x": [
            x for x in range(40, 46) if cell(x, 17, 117) != AIR
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
