"""Show full still-unreviewed methods or apply explicitly authored decisions; never auto-accept."""
from pathlib import Path
import argparse,json,re
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=25);p.add_argument('--start',type=int,default=0);p.add_argument('--decisions');p.add_argument('--priority',action='store_true');p.add_argument('--focus',action='store_true');p.add_argument('--indices',help='Comma-separated explicit candidate IDs to read in full');a=p.parse_args()
cs=json.loads((B/'evidence/armor-reference-candidates.json').read_text());rp=B/'research/reviewed-sites.json';rs=json.loads(rp.read_text());known={r['candidate_index'] for r in rs}
if a.decisions:
 batch=json.loads(Path(a.decisions).read_text())
 for key,val in batch.items():
  i=int(key);assert i not in known,i;c=cs[i];decision,note=val
  assert decision in ['accepted','excluded'];assert len(note)>10
  rs.append({'candidate_index':i,'snippet_sha256':c['snippet_sha256'],'source_identity':f"{c['repo']}@{c['revision']}:{c['path']}:{c['line']}-{c['end_line']}",'decision':decision,'observation':note});known.add(i)
 rp.write_text(json.dumps(sorted(rs,key=lambda x:x['candidate_index']),ensure_ascii=False,indent=2)+'\n')
 print('Applied',len(batch),'remaining',len(cs)-len(known));raise SystemExit
selected=set(map(int,a.indices.split(','))) if a.indices else None
priority=set(json.loads((B/'research/priority-candidates.json').read_text())) if a.priority else None
for i,c in [(i,c) for i,c in enumerate(cs) if i not in known and i>=a.start and (selected is None or i in selected) and (priority is None or i in priority) and (not a.focus or (re.search(r'(?i)armor|armour|curio|capabilit|handler|item|module|perk|accessor|attribute|cooldown|effect|gear|potion',c['path']) and not re.search(r'(?i)/(?:block|blocks|block_entity|tile|tiles|recipe|recipes|ritual|rituals|entity|entities|gui|render|particles|particle|inventory|command|commands)/|Tooltip|Overlay|Renderer',c['path'])))][:a.count]:
 print('\nINDEX',i,c['repo'],c['path'],c['line'],c['method']);print(c['excerpt'])
