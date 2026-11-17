#!/usr/bin/env python3
"""Static source binding and saved decision consistency, not independent approval."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def verify():
 p=H/'immune-reference-batch-045.json';raw=p.read_bytes();d=json.loads(raw)
 assert d['research_credit']==0 and d['maximum_proposed_credit']==1
 assert not d['production_changes'] and not d['runtime_executed']
 v=d['provenances'][0];mr=(R/v['manifest_path']).read_bytes();assert sha(mr)==v['manifest_sha256']
 m=next(x for x in json.loads(mr) if x['repo']==v['repo'])
 cr=(R/v['commit_metadata_path']).read_bytes();tr=(R/v['tree_metadata_path']).read_bytes()
 assert sha(cr)==m['commit_metadata_sha256'] and sha(tr)==m['tree_metadata_sha256']
 c=json.loads(cr);t=json.loads(tr)
 assert c['sha']==m['commit']==v['commit'] and m['branch']==v['branch'] and m.get('tag')==v['tag']
 assert c['tree']['sha']==t['sha']==m['git_tree']==v['git_tree'] and not t['truncated']
 entries={x['source']:x for x in m['files']};blobs={x['path']:x['sha'] for x in t['tree'] if x['type']=='blob'}
 covered={};full=set();ranges=[]
 for x in d['source_refs']:
  e=entries[x['path']];p0=(R/x['path']).resolve();assert p0.is_relative_to(R)
  sr=p0.read_bytes();assert sha(sr)==x['file_sha256']==e['sourceSha256']
  blob=hashlib.sha1(b'blob '+str(len(sr)).encode()+b'\0'+sr).hexdigest()
  assert blob==x['git_blob_sha1']==e['source_blob']==blobs[e['path']]
  assert x['upstream_path']==e['path'] and x['commit']==m['commit'] and x['repo']==m['repo']
  lines=sr.decode().splitlines();a,b=x['lines'];assert 1<=a<=b<=len(lines)
  assert sha('\n'.join(lines[a-1:b]).encode())==x['range_text_sha256']
  prev=covered.setdefault(x['path'],set());now=set(range(a,b+1));assert not prev.intersection(now);prev.update(now)
  if len(prev)==len(lines):full.add(x['path'])
  ranges.append({'path':x['path'],'lines':x['lines'],'range_text_sha256':x['range_text_sha256']})
 assert len(covered)==d['unique_files'] and len(full)==d['full_files'] and len(ranges)==d['source_ranges']
 total=sum(len(s) for s in covered.values());assert total==d['cited_lines']
 s=d['dedup_snapshot'];lr=(R/s['path']).read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
 assert len(s['comparisons'])==6
 for x in s['comparisons']:
  assert x['full_semantic_decision_read']=={k:v for k,v in by[x['accepted_id']].items() if k not in ['source_refs','auxiliary_refs']}
  assert x['distinction']
 q=d['migration_overlap_screen'];mlraw=(R/q['path']).read_bytes()
 mi={x['candidate_id']:x for x in [json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]}
 assert len(q['comparisons'])==5
 for x in q['comparisons']:
  old=mi[x['accepted_id']];assert old['credit']==1 and old['status']=='accepted'
  assert all(old[k]==v for k,v in x['complete_semantic_decision_read'].items()) and x['distinction']
 for k in ['accepted042_receipt','044_zero']:
  r=d['baseline'][k];assert sha((R/r['path']).read_bytes())==r['sha256']
 assert json.loads((R/d['baseline']['044_zero']['path']).read_text())['research_credit']==0
 aux_lines=0
 for x in d['auxiliary_refs']:
  e=entries[x['path']];sr=(R/x['path']).read_bytes();lines=sr.decode().splitlines()
  assert x['lines']==[1,len(lines)] and x['repo']==m['repo'] and x['commit']==m['commit'] and x['upstream_path']==e['path']
  assert sha(sr)==x['file_sha256']==e['sourceSha256']
  assert hashlib.sha1(b'blob '+str(len(sr)).encode()+b'\0'+sr).hexdigest()==x['git_blob_sha1']==e['source_blob']==blobs[e['path']]
  assert sha('\n'.join(lines).encode())==x['range_text_sha256'];aux_lines+=len(lines)
 return {'status':'PASS','proposal_path':str(p.relative_to(R)),'proposal_sha256':sha(raw),
  'auxiliary_full_files_verified':len(d['auxiliary_refs']),'auxiliary_lines':aux_lines,'source_ranges_verified':len(ranges),'unique_files_verified':len(covered),'full_files_cited':len(full),
  'unique_cited_source_lines':total,'ranges':ranges,'complete_semantic_decisions_verified':6,
  'whole_migration_owner_decisions_verified':5,'formal_count_observed':len(rows),
  'ledger_changed_since_snapshot':sha(lr)!=s['sha256'],'migration_ledger_changed_since_snapshot':sha(mlraw)!=q['sha256'],
  'maximum_pending_credit':1,'research_credit_awarded':0,'network_requests':0,'upstream_or_game_execution':False,
  'production_or_master_edits':False,'limits':['Cached provenance/ranges/decision equality only, not independent semantic acceptance.',
  'Fixed AstralSorcery1.16-indev; ObserverLib tick scheduler and native engine/network/physics/transfer behavior not executed or adopted.',
  'One Vortex renewable object timeout/dimension-ID membership/control and receipt lifecycle max1. Area-time-stop mode, render helpers, five existing persistent owners0 new credit.']}

if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
