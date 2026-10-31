"""Import explicit helper proposals as zero-credit unreviewed AST candidates.
Does not import helper judgments or accept any implementation.
"""
from pathlib import Path
import argparse,json,hashlib,sys
assert sys.version_info[:2]==(3,12)
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
sys.path.insert(0,str(R/'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()));sha=lambda x:hashlib.sha256(x).hexdigest()
def walk(n):
 yield n
 for child in n.children:yield from walk(child)
def structural(n,raw):
 out=[];ids={}
 for z in walk(n):
  if z.type in ('line_comment','block_comment'):continue
  if not z.children:
   t=raw[z.start_byte:z.end_byte].decode()
   if z.type=='identifier':t=ids.setdefault(t,'I'+str(len(ids)))
   if 'literal' in z.type or z.type=='string_fragment':t=z.type
   out.append(t)
 return sha(' '.join(out).encode())
p=argparse.ArgumentParser();p.add_argument('batch');p.add_argument('--indices',required=True);a=p.parse_args();bp=R/a.batch;assert O/'helpers' in bp.parents
payload=json.loads(bp.read_text())
if isinstance(payload,list):
 records=[]
 for original in payload:
  r=dict(original)
  local=Path(r['source']).relative_to(R)
  assert str(local).endswith('/'+r['path'])
  r.update(revision=r['commit'],source_local=str(local),source_sha256=r['sourceSha256'],line=r['start'],end_line=r['end'],excerpt=r['text'],snippet_sha256=r['excerptSha256'],helper_id=r['id'],support_evidence={'prior_guard_review_provenance':r.get('prior_guard_review_provenance'),'helper_credit_transferred':0})
  r['source_root']=str(local)[:-len(r['path'])-1]
  r['source_metadata']=a.batch
  records.append(r)
elif 'records' in payload:
 records=payload['records']
else:
 # The second helper supplies complete evidence records under entries.
 # Normalize metadata only; none of its proposed judgments become credit.
 records=[]
 for original in payload['entries']:
  r=dict(original)
  assert r['source_local'].endswith('/'+r['path'])
  r['source_root']=r['source_local'][:-len(r['path'])-1]
  root_name=Path(r['source_root']).name
  metadata_name={'behavior-tree-003':'behavior-commit-003.json',
                 'next-tree-003':'next-commit-003.json',
                 'architectury116-tree-004':'architectury116-commit-004.json'}.get(root_name,'commit.json')
  r['source_metadata']=str(Path(r['source_root']).parent/metadata_name)
  metadata=json.loads((R/r['source_metadata']).read_text())
  assert metadata['sha']==r['revision'], 'Helper source root must match its exact revision'
  r['helper_id']=r['chain_id']
  r['support_evidence']=r['evidence']
  records.append(r)
cs=[json.loads(x) for x in (O/'candidates.jsonl').read_text().splitlines()];seen={c['candidate_id'] for c in cs}
for i in map(int,a.indices.split(',')):
 r=records[i];raw=(R/r['source_local']).read_bytes();assert sha(raw)==r['source_sha256'];nodes=[n for n in walk(parser.parse(raw).root_node) if n.type=='method_declaration' and n.start_point.row+1<=r['line']<=n.end_point.row+1 and n.end_point.row+1==r['end_line']];assert len(nodes)==1,(i,'not exact full method');n=nodes[0];assert not n.has_error
 assert sha(r['excerpt'].encode())==r['snippet_sha256'];assert '\n'.join(raw.decode().splitlines()[r['line']-1:r['end_line']]).strip()=='\n'.join(r['excerpt'].splitlines()).strip()
 code=raw[n.start_byte:n.end_byte].decode();ident=sha((r['repo']+r['revision']+r['path']+str(n.start_byte)).encode())[:20]
 if ident in seen:print('Already indexed',i,ident);continue
 c={k:r[k] for k in ('repo','revision','path','source_local','source_metadata','source_root','line','end_line','source_sha256','url')};c.update(candidate_id=ident,method=raw[n.child_by_field_name('name').start_byte:n.child_by_field_name('name').end_byte].decode(),excerpt=code,snippet_sha256=sha(code.encode()),structural_fingerprint=structural(n,raw),parse_error=False,discovery_tags=['helper_proposal_unreviewed_zero_credit'],ast_calls=[],ast_guards=[],status='unreviewed',helper_provenance=dict(batch=a.batch,batch_sha256=sha(bp.read_bytes()),helper_id=r['helper_id'],record_index=i,support_evidence=r['support_evidence'],helper_credit_transferred=0));c['line']=n.start_point.row+1;c['end_line']=n.end_point.row+1;c['url']=f"https://github.com/{r['repo']}/blob/{r['revision']}/{r['path']}#L{c['line']}-L{c['end_line']}";print('Imported',len(cs),r['helper_id']);cs.append(c);seen.add(ident)
(O/'candidates.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cs))
