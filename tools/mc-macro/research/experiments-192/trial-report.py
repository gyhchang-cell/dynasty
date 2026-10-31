"""Compact physical R/T trial report; preserve native details in a separate file."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/experiments-190'))
from summarize_app_trials import summarize

parser = argparse.ArgumentParser()
parser.add_argument('labels', nargs='+')
args = parser.parse_args()
for label in args.labels:
    log = ROOT / '.build/state-live' / f'xiaocai190-app-diag192-{label}.log'
    native = Path(__file__).with_name(f'{label}-native.json')
    subprocess.run([sys.executable, str(Path(__file__).with_name('audit-native-jumps.py')),
                    str(log), '--out', str(native)], check=True, stdout=subprocess.DEVNULL)
    audit = json.loads(native.read_text())
    report = summarize(log)
    report['native'] = {k: v for k, v in audit.items() if k not in ('jumps', 'caveat')}
    first = audit['jumps'][0] if audit['jumps'] else {}
    report['first_cells'] = len(first.get('newly_seen_cells_at_contact', []))
    report['first_segment_cells'] = len(first.get('confirmed_cells_before_next_takeoff_or_finish', []))
    report['nonjump_ground_to_air'] = [j['start_tick'] for j in audit['jumps']
                                      if abs(j['first_dy'] - .42) > .005 and not j['skipped_ticks_at_start']]
    path = Path(__file__).with_name(f'{label}-report.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({
        'label': label, 'contacts': audit['confirmed_landings'],
        'sprint_first_air': audit['native_sprint_at_first_air'],
        'first_cells_at_contact': report['first_cells'],
        'first_segment_cells': report['first_segment_cells'], 'first_span': audit['first_span'],
        'speed_BPS': report['net_horizontal_blocks_per_second_after_first_takeoff'],
        'peak_CPS': report['requested_peak_cps'],
        'status': report['final_status'],
        'finish': report['finish_audit'], 'continuity': report['continuity'],
        'nonjump_ground_to_air': report['nonjump_ground_to_air'],
    }, ensure_ascii=False))
