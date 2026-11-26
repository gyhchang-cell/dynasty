"""Inspect the authored dry stone crossing and water below it without a JVM."""
import json
from collections import deque

from build_wangsi import AIR, JAVA, RED, STONE, WATER, WHITE, geometry, outputs


def main():
    source, _ = outputs()
    assert source == JAVA.read_text(encoding="utf-8")
    cuboids, _ = geometry()
    boxes = [(entry["bounds"], entry["palette"]) for entry in reversed(cuboids)]

    def cell(x, y, z):
        for (a, b, c, d, e, f), state in boxes:
            if a <= x <= d and b <= y <= e and c <= z <= f:
                return state
        return None

    surface = {}
    for x in range(44, 53):
        for z in range(62, 92):
            surface[x, z] = [
                y
                for y in range(13, 23)
                if cell(x, y - 1, z) in (STONE, WHITE)
                and cell(x, y, z) == cell(x, y + 1, z) == AIR
            ]
    center_profile = {z: surface[48, z] for z in range(62, 92)}

    start = (48, 13, 63)
    end = (48, 17, 89)
    assert start[1] in surface[start[0], start[2]]
    assert end[1] in surface[end[0], end[2]]
    predecessors = {start: None}
    pending = deque([start])
    while pending:
        x, y, z = pending.popleft()
        for a, b in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
            for step in surface.get((a, b), []):
                node = (a, step, b)
                if abs(step - y) <= 1 and node not in predecessors:
                    predecessors[node] = (x, y, z)
                    pending.append(node)

    route = []
    if end in predecessors:
        node = end
        while node is not None:
            route.append(node)
            node = predecessors[node]
        route.reverse()

    samples = [(48, 10, 75), (43, 10, 75), (35, 7, 75), (35, 10, 75)]
    names = {AIR: "air", RED: "red_nether_bricks", WATER: "water"}
    assert [cell(*sample) for sample in samples] == [AIR, WATER, RED, WATER]
    arch_channels = []
    for z in range(68, 83):
        for y in range(8, 12):
            if all(cell(x, y, z) == AIR for x in range(44, 53)):
                if cell(43, y, z) == cell(53, y, z) == WATER:
                    arch_channels.append([y, z])

    print(json.dumps({
        "coordinate_system": "structure-local x,y,z",
        "movement": "Dry one-block rises and drops within x44..52, z62..91, with two air blocks at each landing. No fluid ticks, trap behavior or runtime collision simulation.",
        "start": start,
        "target": end,
        "found_dry_route": bool(route),
        "route": route,
        "centerline_foot_y_by_z": center_profile,
        "highest_reachable_z_by_x": {
            x: max((z for a, _, z in predecessors if a == x), default=None)
            for x in range(44, 53)
        },
        "water_bed_samples": [
            {"xyz": sample, "state": names[cell(*sample)]}
            for sample in samples
        ],
        "arch_air_channels_flanked_by_source_water_yz": arch_channels,
    }, indent=2))


if __name__ == "__main__":
    main()
