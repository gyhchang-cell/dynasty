"""Measure the current dock, river separation and rear-hall walk from source."""
import json
from collections import Counter

from build_wangsi import AIR, JAVA, RED, STONE, WATER, outputs


def main():
    java, geometry = outputs()
    assert java == JAVA.read_text(encoding="utf-8")
    definition = (JAVA.parent / "DungeonDefinition.java").read_text(encoding="utf-8")
    wangsi = definition.split("public static final DungeonDefinition WANGSI", 1)[1]
    assert '"UNBOUND_RIVER_DOCK",List.of(),List.of()' in wangsi

    def cell(x, y, z):
        for entry in reversed(geometry["boxes"]):
            a, b, c, d, e, f = entry["bounds"]
            if a <= x <= d and b <= y <= e and c <= z <= f:
                return entry["palette"]
        return None

    deck = ((x, 16, z) for x in range(40, 57) for z in range(120, 126))
    assert all(cell(*p) == STONE for p in deck)
    route = [(48, 17, z) for z in range(117, 126)]
    assert all(
        cell(x, y - 1, z) == STONE and cell(x, y, z) == cell(x, y + 1, z) == AIR
        for x, y, z in route
    )
    dock_layers = Counter(
        cell(x, y, z)
        for x in range(23, 76) for z in range(120, 126) for y in range(5, 18)
    )
    water_by_z = {
        z: sum(cell(x, y, z) == WATER for x in range(2, 94) for y in range(5, 13))
        for z in range(64, 127)
    }
    water_bands = {
        "main_river": [z for z in range(64, 90) if water_by_z[z]],
        "sump": [z for z in range(90, 120) if water_by_z[z]],
        "dock_and_rear_wall": [z for z in range(120, 127) if water_by_z[z]],
    }
    assert water_bands == {
        "main_river": list(range(67, 85)), "sump": list(range(94, 100)),
        "dock_and_rear_wall": [],
    }
    print(json.dumps({
        "platform_floor_bounds_inclusive": [40, 16, 120, 56, 16, 125],
        "platform_floor_cells": 17 * 6,
        "rear_door_to_dock_dry_foot_positions": route,
        "red_nether_brick_cells_in_dock_box_y5_to_y17": dock_layers[RED],
        "water_band_z_inclusive": water_bands,
        "main_river_to_dock_z_difference": 120 - 84,
        "boss_arena_marker": "UNBOUND_RIVER_DOCK",
        "scope": "Authored blocks and current dungeon definition. No live-fluid or world-state simulation.",
    }, indent=2))


if __name__ == "__main__":
    main()
