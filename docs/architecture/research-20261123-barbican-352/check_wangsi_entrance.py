"""Check the present Wangsi entry axis, lighting palette and generation height."""
import json

from build_wangsi import AIR, JAVA, LAMP, STONE, outputs


def main():
    java, generated = outputs()
    assert java == JAVA.read_text(encoding="utf-8")
    piece = (JAVA.parent / "WangsiPiece.java").read_text(encoding="utf-8")
    structure = (JAVA.parent / "WangsiStructure.java").read_text(encoding="utf-8")
    assert 'new BlockPos(48,44,0),"阴阳界"' in piece
    assert "setColor(net.minecraft.world.item.DyeColor.RED)" in piece
    assert "new BlockPos(x,high-40,z)" in structure
    assert "origin.offset(48,41,3)" in structure

    def cell(x, y, z):
        for box in reversed(generated["boxes"]):
            a, b, c, d, e, f = box["bounds"]
            if a <= x <= d and b <= y <= e and c <= z <= f:
                return box["palette"]
        return None

    route = [(48, 41, z) for z in range(1, 8)]
    route += [(48, 49 - z, z) for z in range(8, 37)]
    route += [(48, 13, z) for z in range(37, 41)]
    assert all(
        cell(x, y - 1, z) == STONE and cell(x, y, z) == cell(x, y + 1, z) == AIR
        for x, y, z in route
    )
    assert all(
        z + 1 == d and abs(y - b) <= 1
        for (_, y, z), (_, b, d) in zip(route, route[1:])
    )
    lamps = [(42, 41, 3), (54, 41, 3)]
    assert all(cell(*lamp) == LAMP for lamp in lamps)
    assert generated["palette"][LAMP] == "Blocks.PEARLESCENT_FROGLIGHT.defaultBlockState()"
    print(json.dumps({
        "route": route,
        "descent_blocks": 28,
        "route_note": "Geometry through mouth and stair to market at x48. Outside terrain and runtime generation are untested.",
        "sign_local_xyz": [48, 44, 0],
        "sign_lines": ["阴阳界", "生魂止步", "酆都外郭", "枉死城"],
        "sign_text_dye": "red",
        "mouth_lamp_local_xyz": lamps,
        "mouth_lamp_block": "minecraft:pearlescent_froglight",
        "entry_stub_world_y": "highest_of_nine_sampled_first_free_heights + 1",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
