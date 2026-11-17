"""Fetch explicitly named missing Java files at an existing fixed revision; zero credit."""
from pathlib import Path
import sys, json, re, subprocess, hashlib, datetime

B = Path(__file__).resolve().parent
R = B.parents[2]
meta = json.loads((R / sys.argv[1]).read_text())
repo, revision = meta['repo'], meta['sha']
assert re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo)
assert re.fullmatch(r'[0-9a-f]{40}', revision)
root = B / '.work/research-sources' / (repo.replace('/', '__') + '__' + revision[:12])
root.mkdir(parents=True, exist_ok=True)
record = root / 'source.json'
data = json.loads(record.read_text()) if record.exists() else dict(
    repo=repo, sha=revision, research_credit=0, files=[],
    source_metadata=str(Path(sys.argv[1])), upstream_code_executed=False)
for rel in sys.argv[2:]:
    assert rel.endswith('.java') and not Path(rel).is_absolute() and '..' not in Path(rel).parts
    url = f'https://raw.githubusercontent.com/{repo}/{revision}/{rel}'
    result = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                             '--max-time', '30', url], capture_output=True)
    if result.returncode:
        print(json.dumps(dict(path=rel, error=result.stderr.decode(errors='replace')[:300], credit=0)))
        continue
    target = root / rel
    if target.exists():
        assert target.read_bytes() == result.stdout, 'Never overwrite changed cached source'
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result.stdout)
    receipt = dict(path=rel, url=url, sha256=hashlib.sha256(result.stdout).hexdigest(),
                   retrieved_at=datetime.datetime.now().astimezone().isoformat(), credit=0)
    data['files'] = [x for x in data['files'] if x['path'] != rel] + [receipt]
    print(json.dumps(receipt))
record.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
