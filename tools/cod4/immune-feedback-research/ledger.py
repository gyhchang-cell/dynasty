"""Curated research ledger IO and integrity checks; never auto-promotes candidates."""
from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/immune-feedback-research'
def record(key,repo,files,chain,observation,lesson,limits,category='floating_combat_text'):
 source=B/'sources'/repo.replace('/','__');meta=json.loads((source/'source.json').read_text());refs=[]
 for rel,start,end in files:
  p=source/rel;lines=p.read_text().splitlines();assert 1<=start<=end<=len(lines),(rel,start,end,len(lines))
  refs.append({'path':str(p.relative_to(R)),'source_path':rel,'lines':[start,end],'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{rel}#L{start}-L{end}'})
 item={'id':key,'status':'reviewed_effective','repo':repo,'commit':meta['commit'],'category':category,'semantic_dedup_key':key,'count_unit':'one semantically distinct game implementation site with complete containing methods and call-chain context; wrappers/ports/constant-only variants merged','source_refs':refs,'full_chain_observation':chain,'concrete_observation':observation,'application_to_boss_immune':lesson,'limitations':limits,'research_credit':1,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 f=O/'reviewed.json';old=json.loads(f.read_text()) if f.exists() else [];assert key not in {x['id'] for x in old};old.append(item);f.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');return item

def verify():
 f=O/'reviewed.json';rows=json.loads(f.read_text()) if f.exists() else [];keys=[]
 for x in rows:
  assert x['status']=='reviewed_effective' and x['research_credit']==1
  keys.append(x['semantic_dedup_key'])
  for ref in x['source_refs']+x.get('auxiliary_refs',[]):assert hashlib.sha256((R/ref['path']).read_bytes()).hexdigest()==ref['file_sha256']
 assert len(keys)==len(set(keys))
 sources=json.loads((O/'sources.json').read_text());p={'target':1000,'reviewed_effective_semantic_dedup':len(rows),'remaining':max(0,1000-len(rows)),'source_projects_acquired':sum('commit' in x for x in sources),'acquisition_credit':0,'formal_design_gate_satisfied':len(rows)>=1000,'production_changes':False,'game_started':False,'counting_note':'Each manually reviewed semantically independent game implementation site earns 1; full containing methods and native chain context are evidence, not extra credits. Method/file counts, wrappers, ports, constant-only variants and candidate hits earn 0. Semantic cross-project review still requires human-agent judgment; verifier checks key uniqueness and hashes only.'};(O/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');print(json.dumps(p,ensure_ascii=False))
def attach_auxiliary(key,repo,files,note):
 source=B/'sources'/repo.replace('/','__');meta=json.loads((source/'source.json').read_text());refs=[]
 for rel,start,end in files:
  p=source/rel;assert 1<=start<=end<=len(p.read_text().splitlines())
  refs.append({'repo':repo,'commit':meta['commit'],'path':str(p.relative_to(R)),'source_path':rel,'lines':[start,end],'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{meta["commit"]}/{rel}#L{start}-L{end}','research_credit':0,'role':'auxiliary generic dependency, not an extra implementation','note':note})
 f=O/'reviewed.json';rows=json.loads(f.read_text());row=next(x for x in rows if x['id']==key);row.setdefault('auxiliary_refs',[]).extend(refs);f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':verify()
