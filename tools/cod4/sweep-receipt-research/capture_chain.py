"""Snapshot manually selected, already-read full Java methods; always zero extra credit.
Input JSON contains chains with candidate_indices and supporting_methods pairs
[source path, method name]. This does not review or accept candidates.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,sys
assert sys.version_info[:2]==(3,12)
B=Path(__file__).resolve().parent; R=B.parents[2]
sys.path.insert(0,str(R/'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
p=argparse.ArgumentParser();p.add_argument('spec');p.add_argument('output');a=p.parse_args()
O=R/'docs/cod4/audit-20261022/sweep-receipt-research'; dest=R/a.output
assert dest.parent==O and not dest.exists()
cs=[json.loads(x) for x in (O/'candidates.jsonl').read_text().splitlines()]
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
sha=lambda b:hashlib.sha256(b).hexdigest()
chains=json.loads((R/a.spec).read_text())
for ch in chains:
 nodes=[]
 for i in ch.pop('candidate_indices',[]):
  c=cs[i];nodes.append({k:c[k] for k in ('candidate_id','repo','revision','path','method','line','end_line','source_local','source_sha256','snippet_sha256','url','excerpt')})
 for selection in ch.pop('supporting_methods',[]):
  local,name=selection[:2]; at_line=selection[2] if len(selection)>2 else None
  f=R/local;root=next((q for q in f.parents if (q/'source.json').exists()),None)
  if root is not None:meta=json.loads((root/'source.json').read_text())
  else:
   inherited=[c for c in cs if (R/c['source_root']) in f.parents]
   assert inherited,('no fixed source metadata',local)
   pins={(c['repo'],c['revision'],c['source_root']) for c in inherited};assert len(pins)==1,(local,pins)
   repo,revision,local_root=pins.pop();root=R/local_root;meta={'repo':repo,'sha':revision}
  raw=f.read_bytes();matches=[]
  for n in walk(parser.parse(raw).root_node):
   if n.type=='method_declaration' and raw[n.child_by_field_name('name').start_byte:n.child_by_field_name('name').end_byte].decode()==name and (at_line is None or n.start_point.row+1<=at_line<=n.end_point.row+1):matches.append(n)
  assert len(matches)==1,(local,name,len(matches))
  n=matches[0];assert not n.has_error;code=raw[n.start_byte:n.end_byte];rel=str(f.relative_to(root));line=n.start_point.row+1;end=n.end_point.row+1
  nodes.append(dict(repo=meta['repo'],revision=meta['sha'],path=rel,method=name,line=line,end_line=end,source_local=local,source_sha256=sha(raw),snippet_sha256=sha(code),url=f"https://github.com/{meta['repo']}/blob/{meta['sha']}/{rel}#L{line}-L{end}",excerpt=code.decode()))
 ch['additional_credit']=0;ch['nodes']=nodes
out=dict(purpose='人工全文审阅后的具体玩法使用链；支持方法不额外计数。',reviewed_at=datetime.datetime.now().astimezone().isoformat(),additional_credit=0,external_runtime_tested=False,chains=chains)
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Captured',len(chains),'manual chains;',sum(len(c['nodes']) for c in chains),'full methods; zero additional credit')
