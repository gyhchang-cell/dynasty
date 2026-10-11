"""Confirm native hurt/death pose values, shared grip rotation and real skill bones."""
import argparse
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/art/cod2-voxel-v1"
parser = argparse.ArgumentParser()
parser.add_argument("run")
args = parser.parse_args()
assert re.fullmatch(r"[\w-]+", args.run)
folder = OUT / "native" / args.run
assert (folder / "PASS.txt").exists()
assert not any((folder / mark).exists() for mark in ("FAIL.txt", "PARTIAL.txt", "ABORTED.txt"))
raw = (folder / "samples.json").read_bytes()
rows = [row for row in json.loads(raw) if "actualBakedBones" in row]
assert len(rows) == 40
poses = []
for row in rows:
    bones = row["actualBakedBones"]
    assert all(len(values) in (3, 9) and all(math.isfinite(v) for v in values)
               for values in bones.values())
    if row["id"] == "xianzhen_duantoujiang":
        assert bones["right_grip"] == bones["greatblade"]
    if row["view"] == "hurt":
        angle = abs(math.degrees(bones["chest"][0]))
        assert angle > .5 and row["hurtTime"] > 0 and row["health"] > 0
        assert row["clip"].endswith(".hurt")
        poses.append(dict(id=row["id"], view="hurt", age=row["age"],
                          chest_rotation_x_degrees=math.degrees(bones["chest"][0]),
                          hurt_time=row["hurtTime"]))
    elif row["view"] == "death":
        assert row["health"] == 0 and row["deathTime"] > 0
        assert row["clip"].endswith(".death")
        assert abs(math.degrees(bones["right_knee"][0])) > 10
        poses.append(dict(id=row["id"], view="death", age=row["age"],
                          right_knee_rotation_x_degrees=math.degrees(bones["right_knee"][0]),
                          death_time=row["deathTime"]))
assert len(poses) == 4
throw = next(row for row in rows if row["view"] == "throw-contact")
assert throw["actualBakedBones"]["held_head"][6:] == [.001] * 3
summon = next(row for row in rows if row["view"] == "spiders-contact")
assert summon["actualSpiders"] == 4
assert abs(math.degrees(summon["actualBakedBones"]["box_lid"][0])) > 60
fuse = [row for row in rows if row["view"] in ("actual-fuse-tell", "actual-fuse-8")]
assert len(fuse) == 2 and all(row["clip"].endswith(".fuse") and row["actualOwnerLaunch"] for row in fuse)
assert abs(fuse[0]["boilerScaleY"] - fuse[1]["boilerScaleY"]) > .01
result = dict(passed=True, run=args.run, actual_pose_samples=len(rows),
              scope="Actual native baked-bone supplement, same accepted resources as elites5; no gameplay rewrite.",
              source_samples_sha256=hashlib.sha256(raw).hexdigest(),
              pose_values=poses, headless_grip_blade_baked_transforms_equal=True,
              headless_views_checked=sum(row["id"] == "xianzhen_duantoujiang" for row in rows),
              thrown_head_scale=throw["actualBakedBones"]["held_head"][6:],
              real_four_spiders=summon["actualSpiders"],
              lid_rotation_x_degrees=math.degrees(summon["actualBakedBones"]["box_lid"][0]),
              fuse_boiler_scale_y=[row["boilerScaleY"] for row in fuse],
              screenshots_inspected="All40 originals via5 nearest-neighbour inspection sheets",
              units="Bone rotation XYZ radians; positions model units; scale unitless. Chest/knee record rotation XYZ only.",
              verified_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat())
(OUT / "elite-baked-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print("PASS native hurt/death chest/knee poses, grip/blade transforms, real throw/lid/fuse bones")
for pose in poses:
    print(pose)
