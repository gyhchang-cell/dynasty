"""Audit actual ground-to-air transitions, not sparse POSE phase samples."""
import argparse
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("log", type=Path)
parser.add_argument("--out", type=Path)
args = parser.parse_args()
frames = []
for line in args.log.read_text().splitlines():
    if " FRAME " not in line:
        continue
    stamp, packet = line.split(" FRAME ", 1)
    frame = json.loads(packet)
    if frames and frame["tick"] == frames[-1]["tick"]:
        continue
    frame["time"] = float(stamp)
    frames.append(frame)

jumps = []
active = None
for before, after in zip(frames, frames[1:]):
    if before["ground"] and not after["ground"]:
        active = {
            "start_time": after["time"], "start_tick": after["tick"],
            "takeoff": before["p"], "first_air_position": after["p"],
            "first_air_angle": after["angle"],
            "native_sprint": after["sprint"],
            "first_dy": after["p"][1] - before["p"][1],
            "first_horizontal_bps": math.hypot(after["v"][0], after["v"][2]) * 20,
            "launch_horizontal_increment": math.hypot(
                after['p'][0] - before['p'][0] - before['v'][0],
                after['p'][2] - before['p'][2] - before['v'][2]),
            "skipped_ticks_at_start": after["tick"] - before["tick"] - 1,
            "starting_solids": before["solid"],
        }
        jumps.append(active)
    if active is not None and not before["ground"] and after["ground"]:
        p = after["p"]
        active.update({
            "landing": p, "landing_time": after["time"],
            "rise": p[1] - active["takeoff"][1],
            "horizontal_span": math.hypot(p[0]-active["takeoff"][0], p[2]-active["takeoff"][2]),
            "newly_seen_cells_at_contact": sorted(set(map(tuple, after["solid"])) - set(map(tuple, active.pop("starting_solids")))),
            "post_movement_support": [b for b in after["solid"]
                if abs(p[1] - b[1] - 1) < .03
                and b[0] - .299999 < p[0] < b[0] + 1.299999
                and b[2] - .299999 < p[2] < b[2] + 1.299999],
        })
        active = None

# Contact can precede server confirmation by a tick. Report the completed
# segment separately so a late fourth cell is neither omitted nor described
# as having existed at first contact. This assumes a fresh test fixture.
for index, jump in enumerate(jumps):
    start = next(i for i, frame in enumerate(frames) if frame['tick'] == jump['start_tick'])
    end_tick = jumps[index + 1]['start_tick'] if index + 1 < len(jumps) else float('inf')
    baseline = set(map(tuple, frames[max(0, start - 1)]['solid']))
    segment = [frame for frame in frames[start:] if frame['tick'] < end_tick]
    seen = set().union(*(set(map(tuple, frame['solid'])) for frame in segment))
    jump['confirmed_cells_before_next_takeoff_or_finish'] = sorted(seen - baseline)

summary = {
    "log": str(args.log), "native_tick_samples": len(frames),
    "ground_to_air_transitions": len(jumps),
    "native_sprint_at_first_air": sum(j["native_sprint"] for j in jumps),
    "confirmed_landings": sum("landing" in j for j in jumps),
    "post_movement_unsupported_contacts": sum(not j["post_movement_support"] for j in jumps if "landing" in j),
    "first_span": jumps[0].get("horizontal_span") if jumps else None,
    "launch_increment_caveat": "Displacement minus prior velocity, only interpretable for an unskipped jump in the controlled fixture. It includes movement acceleration and jump impulse; it is not the sprint flag.",
    "jumps": jumps,
    "caveat": "Read-only native samples. A ground-to-air transition can also be a fall; inspect first_dy and skipped ticks. Landing contact alone does not establish continued support.",
}
if args.out:
    args.out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k != "jumps"}, ensure_ascii=False))
