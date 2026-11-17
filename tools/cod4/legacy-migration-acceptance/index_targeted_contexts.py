"""Index explicit pinned files as candidate contexts only. Never accepts research credit.
Useful for real JSON persistence not captured by the initial NBT-oriented scan.
"""
from pathlib import Path
import sys,json,hashlib,collections
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';sys.path.insert(0,str(B/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
p=Parser(Language(tree_sitter_java.language()))
meta=json.loads((O/'sources.json').read_text());idx={x['candidate_id']:x for x in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())}
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
def structural(n,raw):
 out=[];ids={}
 for x in walk(n):
  if x.type in ('line_comment','block_comment'):continue
  if not x.children:
   token=raw[x.start_byte:x.end_byte].decode(errors='replace')
   if x.type=='identifier':token=ids.setdefault(token,'I'+str(len(ids)))
   if 'literal' in x.type or x.type=='string_fragment':token=x.type
   out.append(token)
 return hashlib.sha256(' '.join(out).encode()).hexdigest()
include_assembly="--include-assembly" in sys.argv
explicit_methods={x.split("=",1)[1] for x in sys.argv[1:] if x.startswith("--method=")}
added=0
for f in [x for x in sys.argv[1:] if x!="--include-assembly" and not x.startswith("--method=")]:
 path=(R/f).resolve();source=next(x for x in meta if path.is_relative_to((R/x['private_source']).resolve()));root=R/source['private_source'];rel=str(path.relative_to(root));raw=path.read_bytes();tree=p.parse(raw)
 for n in walk(tree.root_node):
  if n.type not in ('method_declaration','constructor_declaration') or not n.child_by_field_name('body'):continue
  nm=n.child_by_field_name('name');method=raw[nm.start_byte:nm.end_byte].decode();code=raw[n.start_byte:n.end_byte].decode()
  if method not in explicit_methods and not method.lower().startswith(('read','load','deserial','restore')) and not (include_assembly and method=='assemble'):continue
  key=hashlib.sha256((source['repo']+source['sha']+rel+str(n.start_byte)).encode()).hexdigest()[:20]
  if key in idx:continue
  calls=[];guards=[]
  for z in walk(n.child_by_field_name('body')):
   if z.type=='method_invocation':a=z.child_by_field_name('name');calls.append(raw[a.start_byte:a.end_byte].decode())
   elif z.type in ('if_statement','ternary_expression'):
    a=z.child_by_field_name('condition')
    if a:guards.append(raw[a.start_byte:a.end_byte].decode())
  idx[key]=dict(candidate_id=key,status='candidate_not_reviewed',repo=source['repo'],revision=source['sha'],path=rel,private_file=str(path.relative_to(R)),method=method,start_line=n.start_point.row+1,end_line=n.end_point.row+1,file_sha256=hashlib.sha256(raw).hexdigest(),method_sha256=hashlib.sha256(code.encode()).hexdigest(),structural_fingerprint=structural(n,raw),source_url_or_coordinate=f'https://github.com/{source["repo"]}/blob/{source["sha"]}/{rel}#L{n.start_point.row+1}-L{n.end_point.row+1}',ast_calls=calls,ast_guards=guards,context=code,class_has_migration_marker=False,parse_has_error=tree.root_node.has_error,targeted_index_reason='explicit pinned durable owner reader (JSON/NBT), no automatic study credit');added+=1
(O/'candidates.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in idx.values()))
summary=json.loads((O/'candidate-index-summary.json').read_text());summary.update(candidate_methods=len(idx),structurally_distinct_candidates=len({x['structural_fingerprint'] for x in idx.values()}),research_credit_granted_by_indexer=0)
(O/'candidate-index-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print({'added_candidate_contexts':added,'research_credit':0})
