"""Examine existing Boss geometry and numeric poses in the private candidate."""
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import re
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/art/boss-forms"))
from ground import matrices, r

DOCS = ROOT / "docs/cod4/audit-20261022"
RES = ROOT / "src/main/resources"
PRIVATE = DOCS / "resume-20261122/t45-v43-private-pack.json"
REBUILD = ROOT / "build/dynasty-gradle-offline-check-20261122/output/libs/dynasty-1.4.0.jar"
REBUILD_SHA256 = "6af93944a9059913213977218430a875a80b5087e62dcd0645d3774bafa4e3fa"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def xyz(points):
    return np.round(points, 6).tolist()


def point(world, bone, authored):
    local = (np.array(authored) - np.array(bone["pivot"])) * [-1, 1, 1]
    return (world[bone["name"]] @ np.append(local, 1))[:3] * [-1, 1, -1] / 16


def load_form(jar, rebuild, entity, atlas):
    paths = (f"geo/blueprint/boss/{entity}.geo.json",
             f"animations/blueprint/boss/{entity}.animation.json",
             f"textures/entity/blueprint/boss/{atlas}.png")
    data = {}
    metadata = {}
    for path in paths:
        key = "assets/dynasty/" + path
        data[path] = jar.read(key)
        metadata[key] = {
            "private": sha(data[path]), "rebuild": sha(rebuild.read(key)),
            "workspace": file_sha(RES / key),
        }
    geo, anim = [json.loads(data[key]) for key in paths[:2]]
    assert all(len(set(metadata["assets/dynasty/" + p].values())) == 1 for p in paths[:2]), entity
    return geo["minecraft:geometry"][0]["bones"], anim["animations"], metadata


def marshal(bones, clip, age, event_age, mounted):
    world = matrices(bones, clip["bones"], age / 20)
    by_name = {b["name"]: b for b in bones}
    yoke_y = 43 if mounted else 27
    angle = math.radians(120 if mounted else 100)
    anchor = point(world, by_name["four_metre_glaive"], (0, yoke_y + 50, -18))
    fixed = np.array([0, (yoke_y + 50 * math.cos(angle)) / 16, (18 + 50 * math.sin(angle)) / 16])
    return {
        "local_clip_age": age, "server_age": event_age, "authored_tip_world_axes": xyz(anchor),
        "server_blade_port_world_axes": xyz(fixed),
        "separation_blocks": round(float(np.linalg.norm(anchor - fixed)), 6),
    }


def floor_by_bone(form, clip_name, age, selected):
    mesh = r.geometry(
        form, clip_name, age, geo_path=RES / f"assets/dynasty/geo/blueprint/boss/{form}.geo.json",
        animation_path=RES / f"assets/dynasty/animations/blueprint/boss/{form}.animation.json")
    return {name: round(min(float(vertices[:, 1].min()) / 16
                            for vertices, _, bone in mesh if bone == name), 6)
            for name in selected}


def taoyan(bones, clip, age, motion):
    world = matrices(bones, clip["bones"], age / 20)
    by_name = {b["name"]: b for b in bones}
    row = {"age": age}
    if motion == "drink":
        mouth = point(world, by_name["cauldron_maw"], (0, 34, -31))
        row["model_mouth_reference"] = xyz(mouth)
        row["server_mouth"] = xyz(np.array([0, 34 / 16, 31 / 16]))
    elif motion == "slam":
        normalized = min(1, max(0, (age - 15) / 20))
        row["unobstructed_entity_y_above_flat_floor"] = round(4 * math.sin(math.pi * normalized), 6)
        row["strut_pivot_y_model_blocks"] = {
            b["name"]: round(float(world[b["name"]][1, 3] / 16), 6)
            for b in bones if b["name"].startswith("bone_strut_") and b["name"].endswith("_foot")
        }
        row["strut_mesh_lowest_y_model_blocks"] = floor_by_bone(
            "taoyan_zhishi_phase2", "animation.taoyan_zhishi.slam", age,
            row["strut_pivot_y_model_blocks"])
    return row


def kite(bones, clip, age, motion):
    world = matrices(bones, clip["bones"], age / 20)
    by_name = {b["name"]: b for b in bones}
    row = {"age": age}
    if motion == "meteor":
        alpha = 1 if age < 28 else 1 - (age - 28) / 8 if age < 36 else (
            0 if age < 60 else (age - 60) / 4 if age < 64 else 1)
        row["renderer_alpha"] = alpha
        row["ground_wave_attempt"] = age in range(68, 81, 2)
        row["last_target_height_above_arena"] = round(50 * (1 - (age - 60) / 8), 6) if 60 < age <= 68 else None
    for name in ("forehead_thunder_core", "left_folding_rail_4", "right_folding_rail_4",
                 "left_claw_1_tip", "right_claw_1_tip"):
        row[name] = xyz(point(world, by_name[name], by_name[name]["pivot"]))
    if age in range(28, 49) and motion == "claws":
        row["claw_mesh_lowest_y_model_blocks"] = floor_by_bone(
            "luban_yisha", "animation.luban_yisha.claws", age,
            ("left_claw_1_tip", "right_claw_1_tip"))
    return row


def show_data(jar, rebuild):
    output = {}
    for entity, base, atlas, motions in (
        ("gongsun_wuwang", "gongsun_wuwang", "gongsun_wuwang_body", {"slash": range(0, 60)}),
        ("gongsun_wuwang_foot", "gongsun_wuwang", "gongsun_wuwang_foot_body",
         {"slash": range(0, 60), "onslaught": range(0, 88)}),
        ("taoyan_zhishi_phase2", "taoyan_zhishi", "taoyan_zhishi_phase2_body",
         {"drink": range(0, 120), "slam": range(0, 84)}),
        ("luban_yisha", "luban_yisha", "luban_yisha", {"claws": range(0, 92)}),
        ("luban_yisha_metal", "luban_yisha", "luban_yisha_metal", {"meteor": range(0, 108)}),
    ):
        bones, clips, metadata = load_form(jar, rebuild, entity, atlas)
        rows = {}
        for motion, ages in motions.items():
            clip = clips[f"animation.{base}.{motion}"]
            assert clip["animation_length"] * 20 == len(ages), (entity, motion)
            assert {k for k in clip["bones"]} <= {b["name"] for b in bones}, (entity, motion)
            if base == "gongsun_wuwang":
                rows[motion] = [marshal(bones, clip, age, age, entity == base) for age in ages]
                if motion == "slash" and entity.endswith("_foot"):
                    rows["fast_slash"] = [marshal(bones, clip, age * 2, age, False) for age in range(30)]
                    rows["cue_slash"] = [marshal(bones, clip, age + 16, age, False) for age in range(20)]
            elif base == "taoyan_zhishi":
                rows[motion] = [taoyan(bones, clip, age, motion) for age in ages]
            else:
                rows[motion] = [kite(bones, clip, age, motion) for age in ages]
        output[entity] = {"assets": metadata, "motion_samples": rows}
    return output


def ghost_carriage(jar, rebuild):
    """Rebind the preserved strict16 pose evidence to the current three resource bytes."""
    actor = "guiche_jiushouniao"
    art = ROOT / "docs/art/guiche-v2"
    receipt = json.loads((art / "delivery.json").read_text())
    files = receipt["resourceHashes"]
    for repo_file, digest in files.items():
        key = repo_file.removeprefix("src/main/resources/")
        assert sha(jar.read(key)) == sha(rebuild.read(key)) == file_sha(ROOT / repo_file) == digest
    body = json.loads(next((ROOT / name).read_text() for name in files if name.endswith(".geo.json")))
    bones = body["minecraft:geometry"][0]["bones"]
    by_name = {bone["name"]: bone for bone in bones}
    anim = json.loads(next((ROOT / name).read_text() for name in files if name.endswith(".animation.json")))
    pecks = []
    contacts = range(12, 73, 4)
    clip = anim["animations"][f"animation.{actor}.peck"]["bones"]
    for strike, contact in enumerate(contacts):
        head = f"face_{strike % 8}"
        pivot = by_name[head]["pivot"]
        pecks.append({
            "contact_age": contact, "head": head,
            "head_pivot_world_axes": {
                age: xyz(point(matrices(bones, clip, age / 20), by_name[head], pivot))
                for age in range(contact - 2, contact + 3)
            },
        })
    native = art / "native/strict16-final/host"
    views = []
    for line in (native / "PASS.txt").read_text().splitlines():
        match = re.search(r"clip=animation\.guiche_jiushouniao\.(peck|bomb|dive), clientTime=(\d+), "
                          r"start=(\d+), role=host, stage=(\d+), entityUUID=([^,]+)", line)
        if not match:
            continue
        motion, tick, start, stage, uuid = match.groups()
        age = int(tick) - int(start)
        path, = native.glob(f"{int(stage):02d}-ghost-bird-*.png")
        views.append({
            "motion": motion, "skill_age": age, "uuid": uuid,
            "image": str(path.relative_to(ROOT)), "sha256": file_sha(path),
            "peck_contact_age": motion == "peck" and age in contacts,
        })
    assert len(views) == 7 and len({row["uuid"] for row in views}) == len(views)
    return {"assets": files, "historical_poses": views, "peck_contact_windows": pecks}


def main():
    receipt = json.loads(PRIVATE.read_text())
    package = ROOT / receipt["package"]["path"]
    assert file_sha(package) == receipt["package"]["sha256"]
    assert file_sha(REBUILD) == REBUILD_SHA256
    with zipfile.ZipFile(package) as outer:
        raw = outer.read("overrides/mods/dynasty-1.4.0.jar")
    assert sha(raw) == receipt["core_sha256"]
    with zipfile.ZipFile(BytesIO(raw)) as jar, zipfile.ZipFile(REBUILD) as rebuild:
        output = show_data(jar, rebuild)
        bird = ghost_carriage(jar, rebuild)
    print(json.dumps({
        "pack": receipt["package"], "core_sha256": receipt["core_sha256"],
        "scope": "Package keyframe/model-space math, fixed +Z, no world or Minecraft session.",
        "forms": output,
        "ghost_carriage_historical_readback": bird,
    }, indent=2))


if __name__ == "__main__":
    main()
