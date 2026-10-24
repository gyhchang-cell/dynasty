"""Append explicitly selected full methods missed by discovery. Never accepts them."""
from pathlib import Path
import sys,json,hashlib,argparse
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
assert sys.version_info[:2]==(3,12)
sys.path.insert(0,str(R/'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()));sha=lambda b:hashlib.sha256(b).hexdigest()
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
def structural(n,raw):
 out=[];ids={}
 for z in walk(n):
  if z.type in ('line_comment','block_comment'):continue
  if not z.children:
   t=raw[z.start_byte:z.end_byte].decode(errors='replace')
   if z.type=='identifier':t=ids.setdefault(t,'I'+str(len(ids)))
   if 'literal' in z.type or z.type=='string_fragment':t=z.type
   out.append(t)
 return sha(' '.join(out).encode())
ap=argparse.ArgumentParser();ap.add_argument('path');ap.add_argument('methods',nargs='+');a=ap.parse_args()
p=R/a.path;root=next(q for q in p.parents if (q/'source.json').exists());meta=json.loads((root/'source.json').read_text());rel=str(p.relative_to(root));raw=p.read_bytes();tree=parser.parse(raw)
cs=[json.loads(x) for x in (O/'candidates.jsonl').read_text().splitlines()];seen={c['candidate_id'] for c in cs}
for n in walk(tree.root_node):
 if n.type!='method_declaration':continue
 nm=n.child_by_field_name('name');body=n.child_by_field_name('body')
 if nm is None or body is None:continue
 name=raw[nm.start_byte:nm.end_byte].decode()
 if name not in a.methods:continue
 ident=sha((meta['repo']+meta['sha']+rel+str(n.start_byte)).encode())[:20]
 if ident in seen:print('Already indexed',name);continue
 code=raw[n.start_byte:n.end_byte].decode();c=dict(candidate_id=ident,repo=meta['repo'],revision=meta['sha'],path=rel,method=name,source_local=str(p.relative_to(R)),source_root=str(root.relative_to(R)),source_metadata=str((root/'source.json').relative_to(R)),line=n.start_point.row+1,end_line=n.end_point.row+1,source_sha256=sha(raw),snippet_sha256=sha(code.encode()),structural_fingerprint=structural(n,raw),url=f"https://github.com/{meta['repo']}/blob/{meta['sha']}/{rel}#L{n.start_point.row+1}-L{n.end_point.row+1}",discovery_tags=['explicit_followup_full_method'],ast_calls=[],ast_guards=[],parse_error=n.has_error,excerpt=code,status='unreviewed');print('Appended',len(cs),name);cs.append(c);seen.add(ident)
(O/'candidates.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cs))
