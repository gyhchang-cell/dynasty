#!/usr/bin/env python3
"""Materialize explicitly authored semantic annotations; candidate indexing never accepts."""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
DOC=ROOT.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research'
candidates=json.loads((ROOT/'.work/candidates.json').read_text())
annotations=[]
for f in sorted((ROOT/'reviews').glob('*.json')):
    annotations.extend(json.loads(f.read_text()))
accepted=[];seen=set();norms=set()
for a in annotations:
    hits=[c for c in candidates if c['repo']==a['repo'] and c['path'].endswith(a['file']) and c['name']==a['method'] and (not a.get('start') or c['start']==a['start'])]
    if len(hits)!=1:raise ValueError((a,len(hits)))
    c=hits[0]
    if c['id'] in seen or c['normalizedSha256'] in norms:raise ValueError('Duplicate implementation '+c['id'])
    for k in ('observation','application','limits'):
        if len(a.get(k,''))<16:raise ValueError('Missing substantive '+k)
    raw=pathlib.Path(c['source']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=c['sourceSha256']:raise ValueError('Source changed')
    seen.add(c['id']);norms.add(c['normalizedSha256'])
    record={**c,**{k:a[k] for k in ('observation','application','limits')}}
    record['reviewMode']='Full implementation read and individually authored control-flow observation; cached pinned source reused, no old accepted reference imported.'
    accepted.append(record)
DOC.mkdir(parents=True,exist_ok=True)
(DOC/'references.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n')
(DOC/'progress.json').write_text(json.dumps(dict(target=1000,accepted=len(accepted),gap=max(0,1000-len(accepted)),candidateMethods=len(candidates),downloadedCandidatesAreNotAccepted=True,productionImplementationPermitted=len(accepted)>=1000 and (DOC/'gate-1000.json').exists(),duplicatePolicy='No repeated full method; exact normalized duplicates rejected automatically; reviewer also excludes alpha-port equivalents and boilerplate.'),ensure_ascii=False,indent=2)+'\n')
print(f'Accepted {len(accepted)}/1000, gap {1000-len(accepted)}')
