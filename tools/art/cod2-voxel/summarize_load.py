"""Summarize real native drawing samples without inferring natural AI or TPS."""
import argparse
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

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
samples = json.loads(raw)
phases = [row for row in samples if "phase" in row]
assert [row["phase"] for row in phases] == [0, 1, 2, 3]
assert len([row for row in samples if "reload" in row]) == 1
assert len(list(folder.glob("[0-9][0-9]-*.png"))) == 4


def distribution(values):
    assert values and all(math.isfinite(v) and v > 0 for v in values)
    return dict(samples=len(values), median_ms=float(np.median(values)),
                p95_ms=float(np.percentile(values, 95)), mean_ms=float(np.mean(values)))


ids = list(phases[1]["actualRegisteredIds"].values())
assert len(set(ids)) == 18
initial = {name: ((i % 6 - 2.5) * 5.5, -60.0, -(i // 6) * 5.0)
           for i, name in enumerate([
               "zuwu_daoshou", "juma_changqiangbing", "liannu_zhenzu", "ludun_jiashi",
               "tiesuo_chihou", "zhenwang_zhangqiguan", "kuijun_sishi", "pijia_panjiang_huwei",
               "shibian_lishi", "fufa_jijiu", "xianzhen_duantoujiang", "qianji_bailian_yanshi",
               "jubi_shigandang", "juli_bixi_kuilei", "tongbi_feitian_yecha", "bazu_digongzhu",
               "baimu_mowu", "mingsha_shixie"])}
assert set(ids) == set(initial)
scenarios = []
for row in phases:
    phase = row["phase"]
    frames = row["frames"]
    expected = 0 if phase == 0 else 18
    assert len(frames) >= 300
    assert all(frame["actualRendered"] == expected for frame in frames)
    assert len(row["actualRegisteredIds"]) == expected
    walks = {frame["actualWalkClips"] for frame in frames}
    if phase == 2:
        assert walks == {18}
        assert len(row["walkPostRenderObservations"]) == 18
    scenario = dict(phase=phase, actual_submitted_geo_renders_every_frame=expected,
                    frame_interval=distribution([frame["milliseconds"] for frame in frames]),
                    server_tick_work=distribution(row["serverTickMilliseconds"]),
                    actual_walk_clips_per_frame=sorted(walks))
    if phase == 2:
        distances = row["actualDrivenDistance"]
        assert set(distances) == set(row["actualRegisteredIds"])
        physical = []
        for mob in row["actualServerPositions"]:
            uuid = mob["uuid"]
            name = row["actualRegisteredIds"][uuid]
            end = tuple(float(v) for v in mob["position"].strip("()").split(","))
            cumulative = distances[uuid]
            displacement = math.dist(initial[name], end)
            assert mob["alive"] and cumulative >= 1 and displacement > .1
            physical.append(dict(id=name, uuid=uuid, initial=list(initial[name]), final=list(end),
                                 cumulative_collision_engine_distance=cumulative,
                                 endpoint_displacement=displacement))
        assert len(physical) == 18
        scenario["physical_motion"] = sorted(physical, key=lambda mob: mob["id"])
    scenarios.append(scenario)

report = dict(passed=True, run=args.run, physical_motion_verified=True,
              scope="Actual native geometry drawing and QA-driven physical walking through Entity.move. "
                    "NoAI fixture; no natural AI, player combat, production TPS or unoccluded visibility claim.",
              window_client_ticks=300, warmup_client_ticks=80, seed=77,
              camera_z=24, fov=65, render_distance=4, source_samples_sha256=hashlib.sha256(raw).hexdigest(),
              ids=sorted(ids), screenshots_inspected="4 original native PNGs including empty and after actual reload",
              scenarios=scenarios, verified_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat())
(OUT / "mixed-load-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print("PASS actual18 draws / actual18 walk clips every measured moving frame / actual18 physical distances / resource reload")
for scenario in scenarios:
    print(scenario["phase"], scenario["frame_interval"], scenario["server_tick_work"])
