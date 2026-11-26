"""Read the actual T45 body clips at stage boundaries with fixed example world transforms."""
import json
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("boss", HERE / "t36-boss-contact-probe.py")
boss = module_from_spec(SPEC)
SPEC.loader.exec_module(boss)

BOSSES = (
    ("taoyan_zhishi", "_phase2", "transition", 64, (4.8, 4.5),
     ("cauldron_maw", "maw_lower_hinge", "siege_piston", "siege_ram"),
     ("tripod_", "old_tripod_", "bone_strut_")),
    ("gongsun_wuwang", "_foot", "morph", 60, (5.2, 3.8),
     ("glaive_bearing", "two_grip_yoke", "four_metre_glaive"),
     ("front_", "rear_", "old_front_", "old_rear_", "left_rocker", "right_rocker")),
)
ORIGIN = np.array([12.5, 80, -8.5])


def active_geometry(form, clip, age, world):
    path = boss.RES / "assets/dynasty"
    mesh = boss.r.geometry(
        form, clip, age, geo_path=path / f"geo/blueprint/boss/{form}.geo.json",
        animation_path=path / f"animations/blueprint/boss/{form}.animation.json")
    grouped = {}
    for vertices, _, name in mesh:
        # Exclude a zero-scaled subtree and degenerate faces from the physical silhouette.
        if abs(np.linalg.det(world[name][:3, :3])) < 1e-9:
            continue
        if np.linalg.norm(np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])) < 1e-6:
            continue
        grouped.setdefault(name, []).extend(vertices * [-1, 1, -1] / 16)
    return grouped


def positive_extensions(points, low, high):
    return boss.xyz(np.maximum(0, np.maximum(low - points.min(axis=0), points.max(axis=0) - high)))


def sample(actor, form, motion, age, local_age, bones, clips, dimensions, anchors, prefixes):
    name = f"animation.{actor}.{motion}"
    world = boss.matrices(bones, clips[name]["bones"], local_age / 20)
    regions = active_geometry(form, name, local_age, world)
    values = np.concatenate([np.array(regions[k]) for k in regions])
    half, height = dimensions[0] / 2, dimensions[1]
    lower = np.array([-half, 0, -half])
    upper = np.array([half, height, half])
    physical_anchors = {b: world[b][:3, 3] * [-1, 1, -1] / 16 for b in anchors}
    landmarks = {
        label: (bone, authored)
        for label, bone, authored in (
            ("mouth_reference", "cauldron_maw", (0, 34, -31)),
            ("ram_outer_face_center", "siege_ram", (-30, 36, -53)),
        )
        if bone in physical_anchors
    }
    by_name = {bone["name"]: bone for bone in bones}
    for label, (bone, authored) in landmarks.items():
        physical_anchors[label] = boss.point(world, by_name[bone], authored)
    body_groups = ("war_cauldron", "cauldron_maw", "siege_ram", "ram_burning_cast",
                   "oath_shrine", "four_metre_glaive", "old_bone_horse")
    return {
        "age_from_stage_switch": age, "model": form, "clip": name, "clip_tick": local_age,
        "mesh_min": boss.xyz(values.min(axis=0)), "mesh_max": boss.xyz(values.max(axis=0)),
        "mesh_overhang_relative_to_collision_xyz": positive_extensions(values, lower, upper),
        "selected_region_overhang_xyz": {
            k: positive_extensions(np.array(regions[k]), lower, upper)
            for k in body_groups if k in regions
        },
        "visible_supports": {
            key: {"lowest_y": round(min(p[1] for p in points), 6),
                  "pivot": boss.xyz(world[key][:3, 3] * [-1, 1, -1] / 16)}
            for key, points in regions.items()
            if key.startswith(prefixes) and key.endswith(("_foot", "_hoof", "_rocker"))
        },
        "anchors_at_example_world_origin_facing_plus_z": {b: boss.xyz(ORIGIN + p) for b, p in physical_anchors.items()},
        "anchors_at_example_world_origin_facing_minus_x": {
            b: boss.xyz(ORIGIN + np.array([-p[2], p[1], p[0]])) for b, p in physical_anchors.items()},
    }


def main():
    release = json.loads(boss.PRIVATE.read_text())
    pack = boss.ROOT / release["package"]["path"]
    assert boss.file_sha(pack) == release["package"]["sha256"]
    assert boss.file_sha(boss.REBUILD) == boss.REBUILD_SHA256
    result = {}
    with zipfile.ZipFile(pack) as archive:
        core = archive.read("overrides/mods/dynasty-1.4.0.jar")
    assert boss.sha(core) == release["core_sha256"]
    with zipfile.ZipFile(BytesIO(core)) as jar, zipfile.ZipFile(boss.REBUILD) as rebuild:
        classes = {}
        for owner, registry in (("TaoyanCauldron", "CauldronPitContent"),
                                ("BlindMarshal", "BlindMarshalContent")):
            for cls in (owner, registry, f"client/{owner}Renderer$1"):
                key = f"com/dynasty/blueprint/boss/{cls}.class"
                data = jar.read(key)
                assert data == rebuild.read(key)
                classes[key] = boss.sha(data)
        for base, suffix, stage, total, dims, anchors, supports in BOSSES:
            before_bones, before_clips, old_meta = boss.load_form(jar, rebuild, base, base + "_body")
            after_bones, after_clips, metadata = boss.load_form(jar, rebuild, base + suffix, base + suffix + "_body")
            assert after_clips[f"animation.{base}.{stage}"]["animation_length"] * 20 == total
            records = []
            edges = [31.99, 63.99] if total == 64 else [59.99]
            for age in [-1, *range(total + 1), *edges]:
                form, motion, time, bones, clips = base + suffix, stage, age, after_bones, after_clips
                if age < 0:
                    form, motion, time, bones, clips = base, "idle", 0, before_bones, before_clips
                if age == total:
                    motion, time = "idle", 0
                row = sample(base, form, motion, age, time, bones, clips, dims, anchors, supports)
                row["renderer_atlas"] = (base if base == "taoyan_zhishi" and age < 32 else form) + "_body"
                records.append(row)
            result[base] = {
                "registered_collision_width_and_height": dims,
                "geometry_and_material_hashes": {**old_meta, **metadata},
                "rows": sorted(records, key=lambda x: x["age_from_stage_switch"]),
            }
    print(json.dumps({
        "pack": release["package"], "core_sha256": release["core_sha256"],
        "example_origin": boss.xyz(ORIGIN),
        "source_chain_bytecode_sha256": classes,
        "scope": "Offline package model vertices and registered common actor dimensions. "
                 "Idle before switch is a reference pose; real actor location, animation before switch, "
                 "packet order, collisions and contact not measured.",
        "bosses": result,
    }, indent=2))


if __name__ == "__main__":
    main()
