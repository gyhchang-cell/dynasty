"""Pin additional upstream source archives. Acquisition alone gives zero credit."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sys, json, subprocess, tarfile, hashlib, datetime
B=Path(__file__).resolve().parent
R=B.parents[2]
O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
W=B/'.work/research-sources'
W.mkdir(parents=True,exist_ok=True)
def curl(url):
    result=subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','50','--retry','1',url],capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace')[:400])
    return result.stdout
def fetch(repo):
    root=W/repo.replace('/','__')
    if (root/'source.json').exists(): return json.loads((root/'source.json').read_text())
    commit=json.loads(curl(f'https://api.github.com/repos/{repo}/commits/HEAD'))
    revision=commit['sha']
    tree=json.loads(curl(f'https://api.github.com/repos/{repo}/git/trees/{revision}?recursive=1'))
    assert tree['sha']==revision and not tree.get('truncated'),repo
    archive=curl(f'https://codeload.github.com/{repo}/tar.gz/{revision}')
    tarpath=W/(repo.replace('/','__')+'.tar.gz')
    tarpath.write_bytes(archive)
    root.mkdir(exist_ok=True)
    with tarfile.open(tarpath) as tar:
        for member in tar:
            parts=Path(member.name).parts[1:]
            if not member.isfile() or not parts or '..' in parts: continue
            # No scripts are executed. Retain source text and license information only.
            if not (member.name.endswith(('.java','.patch','.kt')) or Path(member.name).name.upper().startswith(('LICENSE','COPYING'))): continue
            target=root.joinpath(*parts)
            assert target.resolve().is_relative_to(root.resolve())
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    (root/'tree.json').write_text(json.dumps(tree))
    data={'repo':repo,'sha':revision,'private_source':str(root.relative_to(R)),
          'archive_url':f'https://codeload.github.com/{repo}/tar.gz/{revision}',
          'archive_sha256':hashlib.sha256(archive).hexdigest(),
          'tree_sha256':hashlib.sha256((root/'tree.json').read_bytes()).hexdigest(),
          'fetched_at':datetime.datetime.now().astimezone().isoformat(),'research_credit':0}
    (root/'source.json').write_text(json.dumps(data,indent=2)+'\n')
    return data
def safe(repo):
    try: return fetch(repo)
    except Exception as e: return {'repo':repo,'error':str(e),'research_credit':0}
with ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(safe,sys.argv[1:]))
p=O/'additional-sources.json'
old=json.loads(p.read_text()) if p.exists() else []
by={d['repo']:d for d in old}
by.update({d['repo']:d for d in results})
p.write_text(json.dumps(list(by.values()),indent=2)+'\n')
for d in results: print(json.dumps({k:v for k,v in d.items() if k in ('repo','sha','error','research_credit')},ensure_ascii=False),flush=True)
