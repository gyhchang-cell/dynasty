"""Read-only review/pin/dedup validation; outputs are confined to this independent directory."""
from pathlib import Path
import json,hashlib,sys,datetime,subprocess
D=Path(__file__).resolve().parent;A=D.parent;R=A.parents[2]
sys.path.insert(0,str(A));import record_source_methods as M
baseline=json.loads((A/'consolidated-reviewed.json').read_text())
identities=set();semantic=set();files={};rows=[];context_count=0
for r in baseline['rows']+baseline['excluded']:
 identities.add((r.get('repo'),r.get('path'),r.get('method'),r.get('start',r.get('lineStart'))))
 if r.get('semanticHash'):semantic.add(r['semanticHash'])
for f in sorted(D.glob('batch-*.json')):
 d=json.loads(f.read_text());assert d['reviewed']==len(d['rows'])
 for r in d['rows']:
  k=(r['repo'],r['path'],r['method'],r['start']);assert k not in identities,(f,k,'identity duplicate');assert r['semanticHash'] not in semantic,(f,k,'semantic duplicate')
  identities.add(k);semantic.add(r['semanticHash']);rows.append(r)
  for c in [r]+r.get('callContext',[])+r.get('supportingMethods',[])+r.get('contextEvidence',[]):
   b=(R/c['local']).read_bytes();assert hashlib.sha256(b).hexdigest()==c.get('sourceSha256',c.get('sha256'))
   root=R/'build/item-use-references'/c['repo'].replace('/','__');meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());assert tree['sha']==meta['sha']==c['revision'];assert not tree.get('truncated')
   ent=next(e for e in tree['tree'] if e['path']==c['path']);blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert ent['sha']==blob
   files[c['local']]={'repo':c['repo'],'revision':c['revision'],'path':c['path'],'sha256':hashlib.sha256(b).hexdigest(),'gitBlob':blob,'sourceMetadataSha256':hashlib.sha256((root/'source.json').read_bytes()).hexdigest(),'treeSha256':hashlib.sha256((root/'tree.json').read_bytes()).hexdigest()}
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
out={'status':'PASS_SOURCE_PINS_BOUNDARIES_AND_HASH_DEDUP','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baselineAcceptedPool':227,'locallyReviewedNewImplementations':len(rows),'locallyReviewedScopeDeltas':counts,'fullMethodContexts':context_count,'sourceFiles':len(files),'files':list(files.values()),'qualitativeDedup':'See each observation; semantic hash cannot alone establish mechanism independence. Coordinator acceptance still pending.','productionAllowed':False,'mainLedgerUpdated':False,'game':'NOT_RUN','visualAcceptance':'NOT_RUN','referencePngsCopied':False}
(D/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
p=json.loads((D/'progress.json').read_text());p.update(batches=[f.name for f in sorted(D.glob('batch-*.json'))],newLocallyReviewedImplementations=len(rows),newLocallyReviewedScopeDeltas=counts,lastValidation='validation.json',lastValidatedAt=out['recordedAt']);(D/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='files'},ensure_ascii=False))
