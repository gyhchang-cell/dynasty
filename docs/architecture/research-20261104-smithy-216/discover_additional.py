import json,hashlib,sys,zipfile
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
meta=json.loads((R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json').read_text());ib=Path(meta['fixed_archive_inventory']['path']).read_bytes();assert hashlib.sha256(ib).hexdigest()==meta['fixed_archive_inventory']['sha256'];fixed={x['path']:x for x in json.loads(ib)['archives']};rows=json.loads((P/'additional-discovery-inputs.json').read_text())['rows'];verified={};scanned=[];matches=[]
for a in rows:
 jar=a['source_archive']
 if jar not in verified:
  b=Path(jar).read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha==fixed[jar]['sha256'];verified[jar]={'path':jar,'sha256':sha,'bytes':len(b)}
 with zipfile.ZipFile(jar)as z:b=z.read(a['member'])
 assert hashlib.sha256(b).hexdigest()==a['nbt_sha256'];d=read(b);pal=d.get('palette')or d['palettes'][0];c=Counter(pal[v['state']]['Name']for v in d['blocks']);dev={n:v for n,v in c.items()if any(k in n for k in ['stonecutter','anvil','smithing_table','grindstone','blast_furnace','brewing_stand','cauldron'])};r={**a,'devices':dev,'furnaces':c.get('minecraft:furnace',0),'smokers':c.get('minecraft:smoker',0),'jigsaws':c.get('minecraft:jigsaw',0),'entities':len(d.get('entities',[])),'BE':sum('nbt'in v for v in d['blocks']),'manual_reading':False,'credit':0};scanned.append(r)
 if dev:matches.append(r)
out={'purpose':'New bounded frozen-local dimensions outside prior2230. Device co-presence only, no semantic or whole completeness credit. All local sources not exhausted.','scanned':scanned,'device_candidates':matches,'verified_archives':list(verified.values()),'formal_credit_added':0};(P/'additional-device-candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('SCANNED',len(scanned),'device candidates',len(matches))
for v in matches:print(v['member'],v['size'],v['devices'],'furnaces',v['furnaces'],'jigsaws',v['jigsaws'])
