"""Read-only review/pin/dedup validation; outputs are confined to this independent directory."""
from pathlib import Path
import json,hashlib,sys,datetime,subprocess
D=Path(__file__).resolve().parent;A=D.parent;R=A.parents[2]
sys.path.insert(0,str(A));import record_source_methods as M
baseline_bytes=(A/'consolidated-reviewed.json').read_bytes();baseline=json.loads(baseline_bytes)
identities=set();semantic=set();files={};rows=[];excluded=[];pending=[];supplementary=[];context_count=0;pin_gaps=[]
selected=sys.argv[1:]
selected_files=[D/name for name in selected] if selected else sorted(D.glob('batch-*.json'))+sorted(D.glob('supplement-*.json'))
for path in selected_files:
 assert path.parent==D and path.name.startswith(('batch-','supplement-')) and path.suffix=='.json'
for r in baseline['rows']+baseline['excluded']:
 identities.add((r.get('repo'),r.get('path'),r.get('method'),r.get('start',r.get('lineStart'))))
 if r.get('semanticHash'):semantic.add(r['semanticHash'])
if selected:
 # Check new proposals against prior local proposals without rehashing old sources.
 for prior_file in D.glob('batch-*.json'):
  if prior_file in selected_files:continue
  for prior in json.loads(prior_file.read_text()).get('rows',[]):
   identities.add((prior.get('repo'),prior.get('path'),prior.get('method'),prior.get('start')))
   if prior.get('semanticHash'):semantic.add(prior['semanticHash'])
for f in selected_files:
 d=json.loads(f.read_text());assert d.get('reviewed',0)==len(d.get('rows',[]))
 for role,r in [('accepted',r) for r in d.get('rows',[])]+[('excluded',r) for r in d.get('excluded',[])]+[('pending',r) for r in d.get('pending',[])]+[('supplement',r) for r in d.get('records',[])]:
  if role=='accepted':
   k=(r['repo'],r['path'],r['method'],r['start']);assert k not in identities,(f,k,'identity duplicate');assert r['semanticHash'] not in semantic,(f,k,'semantic duplicate')
   identities.add(k);semantic.add(r['semanticHash']);rows.append(r)
  elif role=='excluded':
   assert r.get('countsTowardReferenceGate') is False;excluded.append(r)
  elif role=='pending':
   assert r.get('countsTowardReferenceGate') is False;pending.append(r)
  else:
   assert r['targetScope']=='CONTEXT_ONLY_NO_COUNT';supplementary.append(r)
  for c in [r]+r.get('callContext',[])+r.get('supportingMethods',[])+r.get('contextEvidence',[]):
   b=(R/c['local']).read_bytes();assert hashlib.sha256(b).hexdigest()==c.get('sourceSha256',c.get('sha256'))
   root=R/c['local'][:-len(c['path'])].rstrip('/');meta=json.loads((root/'source.json').read_text());treepath=root/'tree.json' if (root/'tree.json').exists() else root/'research-tree.json';assert meta['sha']==c['revision']
   blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   if treepath.exists():
    tree=json.loads(treepath.read_text());assert tree['sha']==meta['sha'];assert not tree.get('truncated');ent=next(e for e in tree['tree'] if e['path']==c['path']);assert ent['sha']==blob
   else:
    assert role!='accepted',('accepted source lacks pinned tree',c['local'])
    pin_gaps.append({'local':c['local'],'role':role,'reason':'Cached source metadata declares revision but no matching local Git tree; cannot verify remote blob pin. Zero gate credit.'})
   files[c['local']]={'repo':c['repo'],'revision':c['revision'],'path':c['path'],'sha256':hashlib.sha256(b).hexdigest(),'gitBlob':blob,'sourceMetadataSha256':hashlib.sha256((root/'source.json').read_bytes()).hexdigest(),'treeSha256':hashlib.sha256(treepath.read_bytes()).hexdigest() if treepath.exists() else None,'pinVerified':treepath.exists()}
   if 'method' in c:
    t=M.parser.parse(b);todo=[t.root_node];matches=[]
    while todo:
     n=todo.pop();todo.extend(n.children)
     if n.type in ('method_declaration','constructor_declaration') and n.start_point.row+1==c['start'] and n.end_point.row+1==c['end']:matches.append(n)
    assert len(matches)==1; n=matches[0];assert not n.has_error;assert n.child_by_field_name('name').text.decode()==c['method'];assert b[n.start_byte:n.end_byte].decode()==c['source'];context_count+=int(c is not r)
   elif c.get('start'):
    assert '\n'.join(b.decode().splitlines()[c['start']-1:c['end']])==c['source']
   else:assert b.decode()==c['source']
counts={}
for r in rows:counts[r['targetScope']]=counts.get(r['targetScope'],0)+1
out={'status':'PASS_SOURCE_PINS_BOUNDARIES_AND_HASH_DEDUP','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baselineAcceptedPool':227,'baselineConsolidatedSha256':hashlib.sha256(baseline_bytes).hexdigest(),'locallyReviewedNewImplementations':len(rows),'locallyExcludedImplementations':len(excluded),'pendingIncompleteImplementations':len(pending),'supplementaryEvidenceRecords':len(supplementary),'locallyReviewedScopeDeltas':counts,'fullMethodContexts':context_count,'sourceFiles':len(files),'files':list(files.values()),'qualitativeDedup':'See each observation; semantic hash cannot alone establish mechanism independence. Coordinator acceptance still pending.','productionAllowed':False,'mainLedgerUpdated':False,'game':'NOT_RUN','visualAcceptance':'NOT_RUN','referencePngsCopied':False}
output_name='validation-delta-'+selected_files[0].stem+'.json' if selected else 'validation.json'
out['pinGaps']=list({x['local']:x for x in pin_gaps}.values())
if pin_gaps:out['status']='PASS_LOCAL_BOUNDARIES_WITH_EXCLUDED_SOURCE_PIN_GAPS'
out['validatedBatches']=[f.name for f in selected_files];out['validationMode']='DELTA_ONLY' if selected else 'FULL'
(D/output_name).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if not selected:
 p=json.loads((D/'progress.json').read_text());p.update(batches=[f.name for f in sorted(D.glob('batch-*.json'))],newLocallyReviewedImplementations=len(rows),newRejectedImplementations=len(excluded),pendingIncompleteImplementations=len(pending),newLocallyReviewedScopeDeltas=counts,lastValidation='validation.json',lastValidatedAt=out['recordedAt']);(D/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='files'},ensure_ascii=False))
