from pathlib import Path
import json,zipfile,hashlib,io
D=Path(__file__).resolve().parent;R=D.parents[2];report=json.loads((D/'DELIVERY.json').read_text());rows=json.loads((D/'selection.json').read_text());files={}
for row in rows:
 for sub,ext in [('textures/item','png'),('models/item','json')]:
  m='assets/dynasty/'+sub+'/'+row['id']+'.'+ext;files[m]=(R/'src/main/resources'/m).read_bytes()
m='assets/minecraft/atlases/blocks.json';files[m]=(R/'src/main/resources'/m).read_bytes();checks=[]
for entry in report['installed']:
 p=Path(entry['path']);blob=p.read_bytes();assert hashlib.sha256(blob).hexdigest()==entry['sha256'],p
 if p.suffix!='.jar':
  with zipfile.ZipFile(io.BytesIO(blob)) as outer:blob=outer.read('overrides/mods/dynasty-1.4.0.jar')
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  for batch in ['weapons-mc-v19','weapons-mc-v20','mixed-items-mc-v21']:
   for row in json.loads((R/'docs/art'/batch/'selection.json').read_text()):
    for sub,ext in [('textures/item','png'),('models/item','json')]:
     member='assets/dynasty/'+sub+'/'+row['id']+'.'+ext
     assert z.read(member)==(R/'src/main/resources'/member).read_bytes(),(p,member)
  for member,data in files.items():assert z.read(member)==data,(str(p),member)
  for member in ['assets/dynasty/textures/mob_effect/armor_break.png','assets/dynasty/textures/item/leiting_hammer.png','assets/dynasty/textures/item/taiyi_whisk.png','assets/dynasty/textures/item/chang_qiang.png','assets/dynasty/textures/item/thunder_spear.png','assets/dynasty/textures/item/sea_trident.png']:
   assert z.read(member)==(R/'src/main/resources'/member).read_bytes(),(p,member)
 checks.append({'path':str(p),'readback':'PASS','selectedResources':len(files),'previousIconsAndFineWeaponsAndV19V20':'PASS'})
(D/'installed-readback.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks),'files x',len(files),'selected resources; previous icons, fine weapons and V19/V20 preserved')
