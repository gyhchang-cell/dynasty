"""Measure the existing market alley and read the loop's marker coordinates."""
import json
import re

from build_wangsi import AIR, JAVA, STONE, outputs


def main():
    java, data = outputs()
    assert java == JAVA.read_text(encoding="utf-8")
    source = (JAVA.parent / "WangsiLoop.java").read_text(encoding="utf-8")

    def coordinates(name):
        match = re.search(rf"{name}=new BlockPos\((\d+),(\d+),(\d+)\)", source)
        assert match is not None, name
        return tuple(map(int, match.groups()))

    def cell(x, y, z):
        for entry in reversed(data["boxes"]):
            a, b, c, d, e, f = entry["bounds"]
            if a <= x <= d and b <= y <= e and c <= z <= f:
                return entry["palette"]
        return None

    markers = {name: coordinates(name) for name in ("CORE", "LAMP", "ARRIVAL")}
    trigger = re.search(
        r"new AABB\(origin.offset\((\d+),(\d+),(\d+)\),origin.offset\((\d+),(\d+),(\d+)\)\)",
        source,
    )
    assert trigger is not None
    low_x, low_y, low_z, high_x, high_y, high_z = map(int, trigger.groups())

    def dry_stone_landing(p):
        x, y, z = p
        return cell(x, y - 1, z) == STONE and cell(x, y, z) == cell(x, y + 1, z) == AIR

    assert dry_stone_landing(markers["ARRIVAL"])
    x, y, z = markers["LAMP"]
    assert cell(x, y - 1, z) == STONE
    assert all(cell(a, y, b) == AIR for a, b in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)))

    outside_lanes = []
    assumed_half_width = 0.3
    for x in (low_x - 1, high_x):
        route = [(x, low_y, z) for z in range(low_z - 1, high_z + 1)]
        if all(dry_stone_landing(p) for p in route):
            center = x + 0.5
            assert center + assumed_half_width <= low_x or center - assumed_half_width >= high_x
            outside_lanes.append(route)

    print(json.dumps({
        "markers": markers,
        "trigger_bounds": [low_x, low_y, low_z, high_x, high_y, high_z],
        "return_square_has_two_air_blocks_and_stone_floor": True,
        "lamp_stone_pedestal_with_lateral_air_at_lamp_height": True,
        "outside_lanes_for_0_6_block_wide_grounded_player": outside_lanes,
        "scope": "Structure-local initial blocks and declared trigger AABB. No teleport, live collision, save/reopen or client timing simulation.",
    }, indent=2))


if __name__ == "__main__":
    main()
