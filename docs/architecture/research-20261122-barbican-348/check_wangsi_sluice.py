"""Read current Wangsi voxel coordinates and compare closed and drained route states."""
from collections import deque
from pathlib import Path
import json
import re

from build_wangsi import AIR, D, H, JAVA, W, WATER, outputs


def voxel_index(x, y, z):
    return (y * D + z) * W + x


def reachable(grid, start):
    # Full-block support, two air cells, at most one block of vertical change.
    def standable(x, y, z):
        return (
            0 <= x < W and 0 < y < H - 2 and 0 <= z < D
            and grid[voxel_index(x, y - 1, z)] in range(2, 8)
            and grid[voxel_index(x, y, z)] == AIR
            and grid[voxel_index(x, y + 1, z)] == AIR
        )

    assert standable(*start)
    seen = {start: None}
    queue = deque([start])
    while queue:
        x, y, z = queue.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (-1, 0, 1):
                point = (x + dx, y + dy, z + dz)
                if point in seen or not standable(*point):
                    continue
                if dy > 0 and grid[voxel_index(x, y + 2, z)] != AIR:
                    continue
                if dy < 0 and grid[voxel_index(x + dx, y + 1, z + dz)] != AIR:
                    continue
                seen[point] = (x, y, z)
                queue.append(point)
    return seen


def main():
    source, _ = outputs()
    assert JAVA.read_text() == source
    grid = bytearray(W * H * D)
    rows = re.findall(r"\{(\d+,\d+,\d+,\d+,\d+,\d+,\d+)\}", source)
    for row in rows:
        x, y, z, end_x, end_y, end_z, state = map(int, row.split(","))
        run = bytes([state]) * (end_x - x + 1)
        for level in range(y, end_y + 1):
            for depth in range(z, end_z + 1):
                at = voxel_index(x, level, depth)
                grid[at:at + len(run)] = run
    piece = (JAVA.parent / "WangsiPiece.java").read_text()
    sluice = (JAVA.parent / "WangsiSluice.java").read_text()
    for required in (
        "positions.add(new BlockPos(13,y,95));",
        "for(int x=14;x<=16;x++)positions.add(new BlockPos(x,y,100));",
        "for(int y=6;y<=8;y++)",
    ):
        assert required in piece
    assert "for(int y=6;y<=8;y++)for(int z=94;z<=99;z++)for(int x=14;x<=16;x++)" in sluice
    sump = {(x, y, z) for x in range(14, 17) for y in range(6, 9) for z in range(94, 100)}
    gates = {(13, y, 95) for y in range(6, 9)}
    gates |= {(x, y, 100) for x in range(14, 17) for y in range(6, 9)}
    assert all(grid[voxel_index(*p)] == WATER for p in sump)
    assert all(grid[voxel_index(*p)] not in (0, AIR, WATER) for p in gates)
    river = [voxel_index(x, y, z) for x in range(W) for y in range(H) for z in range(66, 86)]
    drained = grid.copy()
    for point in sump | gates:
        drained[voxel_index(*point)] = AIR
    assert all(drained[i] == grid[i] for i in river)
    start = (11, 6, 95)
    closed = reachable(grid, start)
    opened = reachable(drained, start)
    goals = {
        "inside_sump": (15, 6, 97),
        "return_stair_foot": (15, 6, 106),
        "west_court": (24, 17, 101),
        "deep_tunnel_end": (48, 6, 123),
        "behind_hall_grade": (48, 17, 120),
    }
    def witness(seen, end):
        route = []
        if end in seen:
            while end is not None:
                route.append(end)
                end = seen[end]
        return route[::-1]

    print(json.dumps({
        "java_geometry_matches_generator": True, "sump_water_cells": len(sump),
        "gate_cells": len(gates), "main_river_band_water_cells": sum(grid[i] == WATER for i in river),
        "river_band_changed_cells": 0, "approach_start": start,
        "closed_route_to_west_court": witness(closed, goals["west_court"]),
        "open_path_to_sump": witness(opened, goals["inside_sump"]),
        "reachable": {name: {"point": point, "closed": point in closed, "drained_open": point in opened}
                      for name, point in goals.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
