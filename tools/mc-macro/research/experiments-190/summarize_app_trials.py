"""Evidence from physical R/T entry. Partial contacts do not imply a pass."""
import json
import math
import pathlib
import re
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[2]
POSE = re.compile(r"^([\d.]+) POSE ([-\d.]+) ([-\d.]+) ([-\d.]+) yaw ([-\d.]+) pitch ([-\d.]+) ground (true|false) phase=(\w+)")


def continuity(poses, places, released):
    """Measure interruptions separately from surviving and facing forward.

    Ground contact itself isn't failure: a moving run-up can be continuous.
    Returning to placement AFTER starting the forward return is the specific
    repair loop rejected by the user. Exclude opening alignment and R-up finish.
    Samples are ~20Hz, so unobserved short events cannot be declared absent.
    """
    first_air = next((p[0] for p in poses if not p[6]), None)
    active = [p for p in poses if first_air is not None and p[0] >= first_air
              and (released is None or p[0] < released)]
    returns_to_placement = [b[0] for a, b in zip(active, active[1:])
                            if a[7] == 'landing' and b[7] == 'flight']
    backing = [b[0] for a, b in zip(active, active[1:])
               if a[7] != 'backing' and b[7] == 'backing']
    ground_clicks, unknown_clicks = [], []
    for t in places:
        if first_air is None or t < first_air or (released is not None and t >= released):
            continue
        pose = next((p for p in reversed(active) if p[0] <= t), None)
        if pose is None or t - pose[0] > 0.08:
            unknown_clicks.append(t)
        elif pose[6]:
            ground_clicks.append(t)
    dwell, contact_at = [], None
    stationary = 0.0
    for a, b in zip(active, active[1:]):
        if not a[6] and b[6]:
            contact_at = b[0]
        if a[6] and not b[6] and contact_at is not None:
            dwell.append(b[0] - contact_at)
            contact_at = None
        dt = b[0] - a[0]
        if a[6] and b[6] and 0 < dt <= 0.1 and math.hypot(b[1]-a[1], b[3]-a[3])/dt < 0.15:
            stationary += dt
    return dict(return_to_placement_count=len(returns_to_placement),
                return_to_placement_times=returns_to_placement,
                repeat_runup_count=len(backing), repeat_runup_times=backing,
                grounded_clicks_observed=len(ground_clicks),
                clicks_without_fresh_ground_sample=len(unknown_clicks),
                completed_ground_dwell_count=len(dwell),
                median_ground_dwell_ms=round(statistics.median(dwell)*1000, 1) if dwell else None,
                maximum_ground_dwell_ms=round(max(dwell)*1000, 1) if dwell else None,
                stationary_ground_seconds=round(stationary, 3),
                continuous_acceptance=False,
                caveat='20Hz sampled evidence; grounded clicks alone do not prove a stop. Zero observed repair loops does not establish continuous success.')


def summarize(path):
    lines = path.read_text().splitlines()
    poses = [(float(m[1]), *map(float, m.group(2, 3, 4, 5, 6)), m[7] == 'true', m[8])
             for line in lines if (m := POSE.match(line))]
    contacts = [b for a, b in zip(poses, poses[1:]) if not a[6] and b[6]]
    status = next((line.split(' STATE ', 1)[1] for line in reversed(lines) if ' STATE ' in line), 'no status')
    audit = next((json.loads(line.split(' FINISH ', 1)[1]) for line in lines if ' FINISH ' in line), None)
    if audit:
        status = audit['reason']
    places = [float(line.split()[0]) for line in lines if ' PLACE ' in line]
    peak = max((sum(t <= other < t+1 for other in places) for t in places), default=0)
    first_takeoff = next((p[0] for p in poses if p[7] == 'takeoff'), None)
    released = next((float(line.split()[0]) for line in lines if line.endswith(' R up')), None)
    moving = [p for p in poses if first_takeoff is not None and p[0] >= first_takeoff
              and (released is None or p[0] <= released)]
    speed = None
    if len(moving)>1 and moving[-1][0]>moving[0][0]:
        speed=math.hypot(moving[-1][1]-moving[0][1],moving[-1][3]-moving[0][3])/(moving[-1][0]-moving[0][0])
    safe = audit.get('safe_aligned_finish') if audit else None
    motion = continuity(poses, places, released)
    if status == '本跳已完成，已落地并回正。' and safe:
        outcome = ('survived_with_discontinuous_recovery' if motion['return_to_placement_count'] or motion['repeat_runup_count']
                   else 'survived_short_trial_continuity_unverified')
    elif '无法安全续接' in status and safe:
        outcome = 'protected_stop_not_continuous_pass'
    elif '空间不足' in status and safe:
        outcome = 'protected_obstacle_stop_not_continuous_pass'
    elif '前台' in status or '切出游戏' in status or '权限' in status or not poses:
        outcome = 'interrupted_or_no_valid_trial'
    else:
        outcome = 'failed_or_incomplete'
    return dict(log=str(path.relative_to(ROOT)), outcome=outcome, final_status=status,
                landing_contacts=len(contacts), first_pose=poses[0] if poses else None,
                last_pose=poses[-1] if poses else None, finish_audit=audit,
                continuity=motion,
                requested_clicks=len(places), requested_peak_cps=peak,
                net_horizontal_blocks_per_second_after_first_takeoff=round(speed,3) if speed is not None else None,
                minimum_requested_click_interval_ms=round(min((b-a for a,b in zip(places,places[1:])),default=0)*1000,3),
                modes=[line.split(' MODE ',1)[1] for line in lines if ' MODE ' in line],
                caveat='Controller audit confirms emitted releases, not OS delivery; pose is the latest observed game state. Terminal launch does not validate LaunchServices permissions.')


if __name__ == '__main__':
    trials=[summarize(p) for p in sorted((ROOT/'.build/state-live').glob('xiaocai190-app-*.log'))
            if not p.name.endswith(('-probe.log','-record.log'))]
    pathlib.Path(__file__).with_name('xiaocai-app-trials.json').write_text(
        json.dumps({'updated':'2026-10-27','trials':trials},ensure_ascii=False,indent=2)+'\n')
    for t in trials:
        print(pathlib.Path(t['log']).stem, t['outcome'], 'contacts',t['landing_contacts'],t['final_status'])
