"""Summarize native trial evidence; a short pass is never release acceptance."""
import json
import math
import pathlib
import re
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[2]
POSE = re.compile(r"^([\d.]+) pose ([-\d.]+) ([-\d.]+) ([-\d.]+).*ground (true|false)")


def summarize(path):
    lines = path.read_text().splitlines()
    poses = [(float(m[1]), float(m[2]), float(m[3]), float(m[4]), m[5] == 'true')
             for line in lines if (m := POSE.match(line))]
    clicks = [float(line.split()[0]) for line in lines if re.match(r'^[\d.]+ CLICK$', line)]
    contacts = [b for a, b in zip(poses, poses[1:]) if not a[4] and b[4]]
    status = next((line[6:] for line in reversed(lines) if line.startswith('FINAL ')), 'incomplete')
    releases = [float(line.split()[1]) for line in lines if line.startswith('RELEASE ')]
    takeoffs = [float(line.split()[0]) for line in lines if re.match(r'^[\d.]+ key 49 down$', line)]
    start = takeoffs[0] if takeoffs else None
    stop = releases[0] if releases else poses[-1][0] if poses else 0
    active_poses = [p for p in poses if start is not None and start <= p[0] <= stop]
    distance = speed = None
    if len(active_poses) >= 2:
        a, b = active_poses[0], active_poses[-1]
        distance = math.hypot(b[1]-a[1], b[3]-a[3])
        speed = distance / (b[0]-a[0])
    peak = 0
    left = 0
    for right, t in enumerate(clicks):
        while t-clicks[left] >= 1:
            left += 1
        peak = max(peak, right-left+1)
    cycle_times = [b[0]-a[0] for a, b in zip(contacts, contacts[1:])]
    views = [(float(m[1]),float(m[2])) for line in lines if POSE.match(line)
             and (m := re.search(r'yaw ([-\d.]+) pitch ([-\d.]+)',line))]
    heading_error = pitch_error = None
    if views:
        heading = views[0][0]
        cardinal = round(heading/90)*90
        if abs((heading-cardinal+180)%360-180) <= 5:
            heading = cardinal
        heading_error = abs((views[-1][0]-heading+180)%360-180)
        pitch_error = abs(views[-1][1]-45)
    held_keys = set()
    for line in lines:
        if m := re.match(r'^[\d.]+ key (\d+) (up|down)$',line):
            if m[2] == 'down': held_keys.add(int(m[1]))
            else: held_keys.discard(int(m[1]))
    explicit_finish = next((json.loads(line[12:]) for line in reversed(lines)
                            if line.startswith('FINAL_CHECK ')),None)
    if status == '本跳已完成，已落地并回正。':
        outcome = 'native_short_pass_not_app_acceptance'
    elif explicit_finish and explicit_finish.get('safe_aligned_finish') and '无法安全续接' in status:
        outcome = 'protected_stop_not_continuous_pass'
    elif not poses or '前台' in status or '读数' in status or (not takeoffs and '完整方块' in status):
        outcome = 'interrupted_or_no_valid_trial'
    else:
        outcome = 'failed'
    return {
        'log': str(path.relative_to(ROOT)), 'outcome': outcome,
        'final_status': status, 'landing_contacts': len(contacts),
        'first_pose': poses[0] if poses else None, 'last_pose': poses[-1] if poses else None,
        'native_clicks': len(clicks), 'peak_clicks_in_half_open_one_second': peak,
        'minimum_click_interval_ms': round(min((b-a for a,b in zip(clicks,clicks[1:])),default=0)*1000,3),
        'median_landing_interval_seconds': round(statistics.median(cycle_times),3) if cycle_times else None,
        'net_horizontal_distance_after_first_takeoff': round(distance,3) if distance is not None else None,
        'net_horizontal_blocks_per_second_after_first_takeoff': round(speed,3) if speed is not None else None,
        'final_yaw_error_degrees': heading_error,
        'final_pitch_error_from_configured_45_degrees': pitch_error,
        'keys_remaining_down_in_event_log': sorted(held_keys),
        'explicit_final_check': explicit_finish,
        'metric_caveat': '20Hz pose samples; speed excludes preparation and post-release settling. Failed-run speed includes falling and is not comparable acceptance evidence.'
    }


if __name__ == '__main__':
    trials = [summarize(p) for p in sorted((ROOT/'.build/state-live').glob('xiaocai190-*.log'))
              if not p.name.startswith('xiaocai190-app-') and not p.name.endswith(('-record.log','-probe.log'))]
    report = {'updated':'2026-10-27', 'desktop_unchanged':'1.8.9',
              'acceptance':'No diagonal candidate is accepted for release.', 'trials':trials}
    destination = pathlib.Path(__file__).with_name('xiaocai-native-trials.json')
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for trial in trials:
        print(pathlib.Path(trial['log']).stem, trial['outcome'], 'landings',trial['landing_contacts'],
              'CPS_peak',trial['peak_clicks_in_half_open_one_second'],
              'net_blocks/s',trial['net_horizontal_blocks_per_second_after_first_takeoff'])
