"""Read eligible original states before deciding whether a whole visual study is justified."""
import json,sys,hashlib
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
assert not (P/'RECEIPT.json').exists()
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
put('previous-checkpoint.json',{'receipt':bind(P.parent/'research-20261104-smithy-173/RECEIPT.json')})
put('protected-inputs.json',{'files':[bind(p) for p in [R/'modpack/mods/dynasty-1.4.0.jar',R/'docs/cod4/audit-20261022/pending-tasks.json',R/'docs/cod4/audit-20261022/task-ownership-20261026.json']+sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))]})
rows=[]
for r in json.loads((P/'pre-render-history-screen.json').read_text())['rows']:
 if not r['eligible_for_new_source_study']:continue
 assert bind(r['source_archive'])==r['fixed_archive']
 with ZipFile(r['source_archive']) as z:
  b=z.read(r['member']);assert hashlib.sha256(b).hexdigest()==r['nbt_sha256'];d=read(b);pal=d['palette'];counts=Counter(pal[x['state']]['Name'] for x in d['blocks']);cells={tuple(x['pos']):x['state'] for x in d['blocks']}
  location=r['member'][5:-4].replace('/structures/',':',1)
  selected=[]
  for n in z.namelist():
   if '/worldgen/template_pool/' not in n or not n.endswith('.json'):continue
   bb=z.read(n)
   if location.encode() not in bb:continue
   j=json.loads(bb)
   for e in j.get('elements',[]):
    if e.get('element',{}).get('location')==location:selected.append({'member':n,'JSON_sha256':hashlib.sha256(bb).hexdigest(),'selected_element_only':e})
  rows.append({'id':r['id'],'source_archive':r['source_archive'],'member':r['member'],'original':d,'material_counts':dict(counts),'selected_pool_snippets':selected,'full_context_read':False})
  print(r['id'],r['member'],'size',d['size'],'DV',d['DataVersion'],'stored',len(d['blocks']),'counts',dict(counts))
  print('PALETTE',json.dumps(list(enumerate(pal)),ensure_ascii=False))
  print('BE',json.dumps([x for x in d['blocks'] if 'nbt' in x],ensure_ascii=False),'ENTITIES',json.dumps(d.get('entities',[]),ensure_ascii=False))
  print('SELECTED_POOL_ONLY',json.dumps(selected,ensure_ascii=False))
  print('FUNCTIONAL_POSITIONS',json.dumps([x for x in d['blocks'] if any(k in pal[x['state']]['Name'] for k in ['furnace','anvil','smithing','grindstone','ladder','door','bed','chest','barrel','jigsaw'])],ensure_ascii=False))
put('preassessment-original-sources.json',{'rows':rows,'machine_parser_not_credit':True,'PNG_generated':0,'full_context_study':False})
