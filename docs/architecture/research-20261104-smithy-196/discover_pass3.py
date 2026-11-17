"""Bounded machine discovery only: device and bed co-presence is not semantic credit."""
import json,hashlib,sys,re,importlib.util
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
idx=json.loads((P.parent/'research-20261104-smithy-195/pre-render-history-screen.json').read_text());h={};sp=importlib.util.spec_from_file_location('dedup',R/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');dm=importlib.util.module_from_spec(sp);sp.loader.exec_module(dm)
for n in idx['historical_indices']:dm.find_records(json.loads(Path(n).read_text()),n,h)
mp=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';meta=json.loads(mp.read_text());iv=Path(meta['fixed_archive_inventory']['path']);ib=iv.read_bytes();assert hashlib.sha256(ib).hexdigest()==meta['fixed_archive_inventory']['sha256'];inventory=json.loads(ib);fixed={f['path']:f for f in inventory['archives']};c=[]
for a in meta['entries']:
 s=a.get('size',[]);n=a['member']
 if len(s)!=3 or (a['source_archive'],n)in h:continue
 if not(10<=s[0]<=35 and 10<=s[2]<=35 and 8<=s[1]<=40 and s[0]*s[1]*s[2]<=25000):continue
 if re.search(r'(corridor|terminator|crossing|passage|stairway|/rooms?/|/foundry/|/stoneworks/|/streets?/|/roads?/|/bridges?/)',n):continue
 c.append(a)
c.sort(key=lambda a:(0 if '/houses/'in a['member']else 1 if 'village'in a['member']else 2,a['source_archive'],a['member']))
old=json.loads((P.parent/'research-20261104-smithy-193/unread-production-living-machine-discovery.json').read_text());already={(v['source_archive'],v['member']) for v in old['scanned']};c=[v for v in c if (v['source_archive'],v['member']) not in already];already.update((v['source_archive'],v['member']) for v in json.loads((P/'unread-production-living-machine-discovery.json').read_text())['scanned']);c=[v for v in c if (v['source_archive'],v['member']) not in already];already.update((v['source_archive'],v['member']) for v in json.loads((P/'unread-production-living-machine-discovery-pass2.json').read_text())['scanned']);c=[v for v in c if (v['source_archive'],v['member']) not in already];selected=c[:240];scanned=[];matches=[];verified={};errors=[]
for a in selected:
 jar=a['source_archive']
 if jar not in verified:
  b=Path(jar).read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha==fixed[jar]['sha256'];verified[jar]={'path':jar,'sha256':sha,'bytes':len(b)}
 try:
  with ZipFile(jar)as z:b=z.read(a['member'])
  assert hashlib.sha256(b).hexdigest()==a['nbt_sha256'];d=read(b);pal=d.get('palette')or d['palettes'][0];cnt=Counter(pal[x['state']]['Name']for x in d['blocks']);dev={n:v for n,v in cnt.items()if any(k in n for k in ['stonecutter','anvil','smithing_table','grindstone','blast_furnace'])};beds={n:v for n,v in cnt.items()if n.endswith('_bed')};rows={'source_archive':jar,'member':a['member'],'nbt_sha256':a['nbt_sha256'],'size':d['size'],'device_counts':dev,'bed_state_cells':beds,'jigsaw_count':cnt.get('minecraft:jigsaw',0),'block_records':len(d['blocks']),'actual_manual_semantic_read':False,'building_credit':0};scanned.append(rows)
  if dev and beds:matches.append(rows)
 except Exception as e:errors.append({'member':a['member'],'error':repr(e)})
out={'purpose':'New device+bed co-presence candidate discovery only, no semantic/read/image/whole-family credit. Does not prove completeness, room organization, source relevance or usable beds.','metadata_eligible_unread':len(c),'bounded_selection_limit':240,'scanned':scanned,'co_presence_candidates':matches,'verified_archives':list(verified.values()),'errors':errors,'source_exhausted':False,'formal_credit_added':0};(P/'unread-production-living-machine-discovery-pass3.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'eligible':len(c),'scanned':len(scanned),'matches':matches,'errors':errors},ensure_ascii=False))
