import json,sys,hashlib
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import iso,AIR
from PIL import Image
out=[]
for a in json.loads((P/'pre-render-history-screen.json').read_text())['rows']:
 if not a['eligible_for_new_source_study']:continue
 with ZipFile(a['source_archive'])as z:
  bb=z.read(a['member']);assert hashlib.sha256(bb).hexdigest()==a['nbt_sha256'];d=read(bb);pal=d['palette'];counts=Counter(pal[b['state']]['Name']for b in d['blocks']);cells={tuple(b['pos']):pal[b['state']]['Name']for b in d['blocks']if pal[b['state']]['Name']not in AIR}
  for kind,cut in [('whole',None),('cutaway',4)]:
   im=Image.new('RGB',(1520,680),'#edf0f2')
   for r in range(2):im.paste(iso(cells,d['size'],r,f"{a['id']} bounded {kind} not whole-building qualification",cutoff=cut),(760*r,0))
   im.save(P/f"{a['id']}-{kind}.png")
  loc=a['member'][5:].replace('/structures/',':')[:-4];refs=[]
  for n in z.namelist():
   if n.endswith('.json')and('/template_pool/'in n or '/worldgen/structure/'in n):
    b=z.read(n)
    if loc in b.decode(errors='replace'):
     try:j=json.loads(b)
     except json.JSONDecodeError as e:j={'strict_parse_error':str(e),'original_text':b.decode()}
     refs.append({'member':n,'sha256':hashlib.sha256(b).hexdigest(),'json':j})
  out.append({'id':a['id'],'source':a,'DataVersion':d['DataVersion'],'size':d['size'],'stored':len(d['blocks']),'materials':dict(counts),'palette_saved_not_full_manual_read':pal,'block_entities_saved_not_full_manual_read':[b for b in d['blocks']if 'nbt'in b],'entities_saved_not_full_manual_read':d.get('entities',[]),'direct_references':refs,'raw_decoded_original':d,'whole_building_credit':0})
  print(a['id'],a['member'],d['size'],'stored',len(d['blocks']),'materials',dict(counts),'BE',sum('nbt'in b for b in d['blocks']),'entities',len(d.get('entities',[])),'refs',[(r['member'],len(str(r['json'])))for r in refs])
(P/'bounded-source-audit.json').write_text(json.dumps({'rows':out,'complete_whole_studies':0,'credit':0},ensure_ascii=False,indent=2)+'\n')
