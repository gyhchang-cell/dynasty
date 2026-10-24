"""Capture a complete native run, its exit code, source hashes and finish time."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, subprocess
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
p = argparse.ArgumentParser()
p.add_argument('--label', default='rerun')
p.add_argument('--world', default='after')
a = p.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9_-]+', a.label) and re.fullmatch(r'[a-zA-Z0-9_-]+', a.world)
log = BASE / 'evidence' / (a.label + '.log')
receipt = BASE / 'evidence' / (a.label + '-receipt.json')
assert not log.exists() and not receipt.exists(), 'Choose a new label to preserve earlier evidence'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = [BASE / 'evidence/frozen-source-sha256.json', BASE / 'armor.init.gradle', BASE / 'run.sh', *sorted((BASE / 'src').glob('*.java'))]
record = {'started': datetime.datetime.now().astimezone().isoformat(), 'finished': None, 'exit_code': None,
    'command': ['tools/cod4/armor-acceptance/run.sh', a.world],
    'inputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
    'headless': True, 'gui_client_launched': False, 'real_human_multiplayer': False}
receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
with log.open('w') as stream:
    run = subprocess.run(record['command'], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
text = log.read_text()
match = re.search(r'All (\d+) required tests passed', text)
record.update({'finished': datetime.datetime.now().astimezone().isoformat(), 'exit_code': run.returncode,
    'completed_required_tests': int(match[1]) if match else None,
    'build_successful': 'BUILD SUCCESSFUL' in text,
    'log_sha256': sha(log), 'inputs_unchanged': all(sha(ROOT / p) == digest for p, digest in record['inputs_sha256'].items())})
receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(record, ensure_ascii=False, indent=2))
raise SystemExit(run.returncode)
