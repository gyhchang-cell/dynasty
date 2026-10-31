"""Compare native angular samples; this does not replace reviewing video."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/experiments-190'))
from summarize_app_trials import summarize

parser = argparse.ArgumentParser()
parser.add_argument('labels', nargs='+')
parser.add_argument('--out', type=Path)
args = parser.parse_args()
reports = []
for label in args.labels:
    log = ROOT / '.build/state-live' / f'xiaocai190-app-diag192-{label}.log'
    summary = summarize(log)
    frames = []
    for line in log.read_text().splitlines():
        if ' FRAME ' in line:
            stamp, packet = line.split(' FRAME ', 1)
            frame = json.loads(packet)
            frames.append((float(stamp), frame['angle'][0]))
    deltas = []
    for before, after in zip(frames, frames[1:]):
        delta = (after[1] - before[1] + 180) % 360 - 180
        if delta > 10 and 0 < after[0] - before[0] <= .05:
            deltas.append(delta)
    deltas.sort()
    reports.append(dict(label=label,
        speed_BPS=summary['net_horizontal_blocks_per_second_after_first_takeoff'],
        contacts=summary['landing_contacts'],
        ground_dwell_ms=summary['continuity']['median_ground_dwell_ms'],
        positive_large_yaw_sample_p95=deltas[int((len(deltas)-1)*.95)] if deltas else None,
        positive_large_yaw_sample_max=max(deltas, default=None),
        angular_sample_count=len(deltas),
        safe_finish=(summary['finish_audit'] or {}).get('safe_aligned_finish')))
result = dict(trials=reports, caveat='Positive yaw steps >10 degrees at <=50ms intervals approximate return sweeps. Different sample timing can change extrema; they are not video-frame angles or creator measurements.')
if args.out:
    args.out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
