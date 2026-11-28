"""Inspect two-form Kite interlocks using transformed cuboids and source action clocks."""
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
import itertools
import json
from pathlib import Path
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("boss_probe", HERE / "t36-boss-contact-probe.py")
base = module_from_spec(SPEC)
SPEC.loader.exec_module(base)

SIDES = ("left", "right")
BASIS = np.array([-1, 1, -1])
CORNER_SIGNS = np.array(list(itertools.product((-1, 1), repeat=3)))
NORMAL_PAIRS = ((0, 1), (1, 2), (2, 0))
AIRFRAME = "mortise_airframe"
HATCHES = tuple(f"{s}_bomb_hatch" for s in SIDES)
TOES = tuple(f"{s}_claw_{i}_tip" for s in SIDES for i in range(4))
RAILS = {side: tuple(f"{side}_folding_rail_{i}" for i in range(5)) for side in SIDES}
BOMB_POS = np.array([0, .35, -.1875])
BOMB_HALF_SIZE = np.array([.325, .35, .325])
EPSILON = 1e-7


def box(name, index, center, edges):
    radius = np.sum(np.abs(edges), axis=0)
    return name, index, center, edges, center - radius, center + radius


def shape_boxes(bones, world):
    for bone in bones:
        transform = world[bone["name"]]
        bone_pivot = np.array(bone["pivot"])
        for number, raw in enumerate(bone.get("cubes", [])):
            pivot = np.array(raw.get("pivot", bone_pivot))
            basis = transform @ base.r.transform(pivot - bone_pivot, raw.get("rotation", (0, 0, 0)))
            size = np.array(raw["size"]) + 2 * raw.get("inflate", 0)
            if np.min(size) <= 0 or abs(np.linalg.det(basis[:3, :3])) <= EPSILON:
                continue
            offset = (np.array(raw["origin"]) + np.array(raw["size"]) / 2 - pivot) * [-1, 1, 1]
            center = (basis @ np.append(offset, 1))[:3] * BASIS / 16
            edges = (basis[:3, :3] @ np.diag(size / 2)).T * BASIS / 16
            yield box(bone["name"], number, center, edges)


def signed_overlap(left, right):
    a, b = left[3], right[3]
    axes = [np.cross(edges[i], edges[j]) for edges in (a, b) for i, j in NORMAL_PAIRS]
    axes.extend(np.cross(u, v) for u in a for v in b)
    axes = np.array(axes)
    lengths = np.linalg.norm(axes, axis=1)
    nonzero = lengths > EPSILON
    directions = (axes[nonzero].T / lengths[nonzero]).T
    overlap = (np.abs(directions @ a.T).sum(axis=1) + np.abs(directions @ b.T).sum(axis=1)
               - np.abs(directions @ (left[2] - right[2])))
    return float(overlap.min())


def positive_depth(left, right):
    if np.any(np.minimum(left[5], right[5]) - np.maximum(left[4], right[4]) <= EPSILON):
        return 0.0
    return max(0, signed_overlap(left, right))


def worst(groups, name_pairs):
    result = None
    max_depth = EPSILON
    for a, b in name_pairs:
        for left in groups.get(a, ()):
            for right in groups.get(b, ()):
                depth = positive_depth(left, right)
                if depth > max_depth:
                    result = {"first": list(left[:2]), "second": list(right[:2]), "sat_depth": round(depth, 6)}
                    max_depth = depth
    return result


def closest(groups, first, second):
    rows = ((signed_overlap(a, b), a, b)
            for n in first for m in second
            for a in groups.get(n, ()) for b in groups.get(m, ()))
    winner = max(rows, key=lambda row: row[0], default=None)
    if winner is None:
        return None
    value, a, b = winner
    return {"first": list(a[:2]), "second": list(b[:2]), "separation_projection": round(-value, 6)}


def pivot(world, name):
    return world[name][:3, 3] * BASIS / 16


def sample(bones, motion, age, form, clip_name):
    world = base.matrices(bones, motion["bones"], age / 20)
    bone_map = {row["name"]: row for row in bones}
    groups = {}
    for entry in shape_boxes(bones, world):
        groups.setdefault(entry[0], []).append(entry)
    legs = tuple(n for n in bone_map if "_claw_" in n or n.endswith("_landing_lower"))
    shells = tuple(n for n in bone_map if "redwood" in n or n in HATCHES)
    structural = [n for n in groups if n not in shells]
    structural_boxes = [part for n in structural for part in groups[n]]
    relative_low = np.min([part[4] for part in structural_boxes], axis=0)
    relative_high = np.max([part[5] for part in structural_boxes], axis=0)
    guides = {side: [f"{side}_wing_bearing", *RAILS[side]] for side in SIDES}
    adjacency = {
        side: [worst(groups, [(parent, child)]) is not None for parent, child in zip(seq, seq[1:])]
        for side, seq in guides.items()
    }
    rail_spans = {
        side: [round(float(np.linalg.norm(pivot(world, child) - pivot(world, parent))), 6)
               for parent, child in zip(seq, seq[1:])]
        for side, seq in guides.items()
    }
    nonadjacent = [(a, b) for seq in RAILS.values() for i, a in enumerate(seq) for b in seq[i + 2:]]
    nonadjacent.extend((a, b) for a in RAILS["left"] for b in RAILS["right"])
    rails = RAILS["left"] + RAILS["right"]
    groups["spawn_box"] = [box("spawn_box", 0, BOMB_POS + np.array([0, .35, 0]),
                               np.diag(BOMB_HALF_SIZE))]
    first_three_fall = .07 + .105 + .14
    half_drop = np.array([0, first_three_fall / 2, 0])
    groups["drop_envelope_3ticks"] = [box(
        "drop_envelope_3ticks", 0, BOMB_POS + np.array([0, .35, 0]) - half_drop,
        np.diag(BOMB_HALF_SIZE + half_drop))]
    result = {
        "age": age,
        "form": form,
        "visible_shell_cubes": sum(len(groups.get(n, [])) for n in shells),
        "structural_parts_with_geometry": len(structural),
        "structure_bounds": [base.xyz(relative_low), base.xyz(relative_high)],
        "rail_joint_length_blocks": rail_spans,
        "adjacent_structural_cuboids_overlap": adjacency,
        "nonadjacent_rail_overlap": worst(groups, nonadjacent),
        "legs_with_hatches_overlap": worst(groups, itertools.product(legs, HATCHES)),
        "legs_with_cassette_overlap": worst(groups, itertools.product(legs, ("open_bomb_cassette",))),
        "legs_with_drop_shell_overlap": worst(groups, itertools.product(legs, ("redwood_hull_panels",))),
        "legs_with_rails_overlap": worst(groups, itertools.product(legs, rails)),
        "hatches_with_rails_overlap": worst(groups, itertools.product(HATCHES, rails)),
        "leg_cross_side_overlap": worst(groups, itertools.product(
            [n for n in legs if n.startswith("left_")], [n for n in legs if n.startswith("right_")])),
        "shear_blades_overlap": worst(groups, (("upper_shear_beak", "lower_shear_beak"),)),
        "toe_tip_mesh_lowest_y": {n: round(min(part[4][1] for part in groups[n]), 6) for n in TOES},
        "toe_tip_pivots": {n: base.xyz(pivot(world, n)) for n in TOES},
        "blade_spot_and_wing_tip": {
            "upper_beak_outer_edge": base.xyz(base.point(world, bone_map["upper_shear_beak"], (0, 31, -40))),
            "lower_beak_outer_edge": base.xyz(base.point(world, bone_map["lower_shear_beak"], (0, 30, -38))),
            "left_outer_rail": base.xyz(base.point(world, bone_map["left_folding_rail_4"], (72, 29, 0))),
            "right_outer_rail": base.xyz(base.point(world, bone_map["right_folding_rail_4"], (-72, 29, 0))),
            "server_cut_mount_under_right_rail_2": base.xyz(
                base.point(world, bone_map["right_folding_rail_2"], (-44.8, 28, 13))),
        },
        "hatch_hinges_and_cassette": {n: base.xyz(pivot(world, n)) for n in (*HATCHES, "open_bomb_cassette")},
    }
    if clip_name == "bombs" and age in range(24, 67, 6):
        blockers = (*HATCHES, *legs, AIRFRAME, "open_bomb_cassette")
        result["release_box_overlap"] = worst(groups, itertools.product(("spawn_box",), blockers))
        result["first_three_drop_ticks_overlap"] = worst(groups, itertools.product(("drop_envelope_3ticks",), blockers))
        result["launch_points_actor_relative"] = {
            "server_bomb_feet": base.xyz(BOMB_POS),
            "cassette_pivot": base.xyz(pivot(world, "open_bomb_cassette")),
        }
        result["closest_piece_to_spawn_box"] = closest(groups, ("spawn_box",), blockers)
    if clip_name == "bombs":
        result["closest_hatch_and_landing_piece"] = closest(groups, HATCHES, legs)
    if clip_name == "overheat" or clip_name == "fly" and age == 0:
        result["airframe_attachment_overlap"] = {
            name: worst(groups, ((AIRFRAME, name),))
            for side in SIDES for name in (f"{side}_wing_bearing", f"{side}_landing_upper")
        }
    return result


def death_path_sample(bones, motion, age):
    world = base.matrices(bones, motion["bones"], age / 20)
    boxes = list(shape_boxes(bones, world))
    projected_centre = np.array([21 * age / 220,
                                 8 * age / 40 if age < 40 else 8 - 80 * ((age - 40) / 180) ** 2,
                                 0])
    model_bounds = None
    outside_frustum = None
    if boxes:
        low = np.min([cube[4] for cube in boxes], axis=0)
        high = np.max([cube[5] for cube in boxes], axis=0)
        model_bounds = [base.xyz(low), base.xyz(high)]
        outside_frustum = bool(np.any(low < [-12, -9, -12]) or np.any(high > [12, 13, 12]))
    return {
        "age": age,
        "model_nonzero_cuboids": len(boxes),
        "model_bounds": model_bounds,
        "beyond_culling_box": outside_frustum,
        "requested_entity_displacement_from_arena_center": base.xyz(projected_centre),
        "core_pivot_relative_to_actor": base.xyz(pivot(world, "forehead_thunder_core")),
        "server_remove_boundary": age == 220,
    }


def main():
    note = json.loads(base.PRIVATE.read_text())
    pack = base.ROOT / note["package"]["path"]
    assert base.file_sha(pack) == note["package"]["sha256"]
    assert base.file_sha(base.REBUILD) == base.REBUILD_SHA256
    with zipfile.ZipFile(pack) as archive:
        core = archive.read("overrides/mods/dynasty-1.4.0.jar")
    assert base.sha(core) == note["core_sha256"]
    actor = "luban_yisha"
    result = {}
    with zipfile.ZipFile(BytesIO(core)) as jar, zipfile.ZipFile(base.REBUILD) as rebuild:
        for form in (actor, actor + "_metal"):
            bones, clips, resources = base.load_form(jar, rebuild, form, form)
            rows = {}
            for clip_name in ("overheat", "fly", "wing_cut", "bombs", "claws"):
                if form.endswith("_metal") and clip_name == "overheat":
                    continue
                clip = clips[f"animation.{actor}.{clip_name}"]
                last = int(round(clip["animation_length"] * 40))
                rows[clip_name] = [sample(bones, clip, half / 2, form, clip_name) for half in range(last + 1)]
            death = clips[f"animation.{actor}.death"]
            assert death["animation_length"] * 20 == 220
            result[form] = {"resources": resources, "samples": rows,
                            "death_each_tick": [death_path_sample(bones, death, age) for age in range(221)]}
    print(json.dumps({
        "pack": note["package"], "jar_sha256": note["core_sha256"], "forms": result,
        "axes": "Blocks relative to actor bottom-center, body facing +Z; SAT depth ignores texture cutouts.",
        "bomb": {"first_feet": base.xyz(BOMB_POS), "size": [.65, .7],
                 "first_three_tick_motion": [-.07, -.105, -.14],
                 "note": "Drop envelope is a conservative visual position probe, not a collision against the attacker."},
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
