"""Display full candidates or save explicit, context-specific review decisions."""
from pathlib import Path
import argparse,json,sys,hashlib,datetime,re
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=10);p.add_argument('--indices');p.add_argument('--batch');p.add_argument('--focus',action='store_true');a=p.parse_args()
cs=[json.loads(x) for x in (O/'candidates.jsonl').read_text().splitlines()]
rp=O/'reviews';rp.mkdir(exist_ok=True);notes=[r for f in sorted(rp.glob('*.json')) for r in json.loads(f.read_text())];seen={r['candidate_id'] for r in notes}
if a.batch:
 out=rp/(a.batch+'.json');assert not out.exists(),out;rows=[]
 for line in sys.stdin.read().splitlines():
  if not line.strip():continue
  i,d,n=line.split('|',2);i=int(i);assert d in ('a','x','p') and len(n)>20
  c=cs[i];assert c['candidate_id'] not in seen,(i,'already reviewed');seen.add(c['candidate_id'])
  rows.append(dict(candidate_index=i,candidate_id=c['candidate_id'],decision={'a':'accepted','x':'excluded','p':'pending'}[d],observation=n,snippet_sha256=c['snippet_sha256'],reviewed_at=datetime.datetime.now().astimezone().isoformat()))
 out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('Saved',len(rows),'explicit decisions',out)
else:
 def eligible(c):
  return not a.focus or (10<=len(c['excerpt'].splitlines())<=90 and re.search(r'queue|schedul|delayed|tracker|task|network|packet|message',c['path'],re.I) and c['method'] not in ('encode','decode','write','read','init','register','registerPackets'))
 indices=[int(x) for x in a.indices.split(',')] if a.indices else [i for i in range(a.start,len(cs)) if cs[i]['candidate_id'] not in seen and eligible(cs[i])][:a.count]
 for i in indices:
  c=cs[i];print('\n###',i,c['candidate_id'],c['repo'],c['path'],c['method'],f"{c['line']}-{c['end_line']}",c['discovery_tags']);print(c['excerpt'])
