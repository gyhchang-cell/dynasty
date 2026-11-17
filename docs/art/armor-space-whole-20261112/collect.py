from pathlib import Path
import zipfile,hashlib,json,shutil
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;P=B/'ad-astra-fixed-source.zip';shutil.copyfile('/tmp/dynasty-adastra-d52.zip',P)
H=lambda b:hashlib.sha256(b).hexdigest();entries={};match_java=['AdAstra.java','AdAstraClient.java','AdAstraClientForge.java','ClientPlatformUtils.java','ClientPlatformUtilsImpl.java','ModItems.java','ModItemTags.java','PlayerRendererMixin.java','CustomDyeableArmorItemMixin.java']
items=['space_helmet','space_suit','space_pants','space_boots']
with zipfile.ZipFile(P) as z:
 prefix=z.namelist()[0]
 for n in z.namelist():
  rel=n.removeprefix(prefix)
  if n.endswith('/'):continue
  keep=rel in ['LICENSE','README.md','gradle.properties']
  keep|=rel.endswith('.java') and ('/items/armor/' in rel or rel.endswith('/SpaceSuitModel.java') or Path(rel).name in match_java)
  keep|=rel.endswith('.png') and any(rel.endswith('/'+x+'.png') for x in items)
  keep|=rel.endswith('.json') and (any(rel.endswith('/models/item/'+x+'.json') for x in items) or '/tags/items/space_suit' in rel or rel.endswith('mixins.json') or '/tags/items/space_suits' in rel)
  if not keep:continue
  f=B/'source'/rel;f.parent.mkdir(parents=True,exist_ok=True);b=z.read(n);f.write_bytes(b);entries[rel]=H(b)
prov={'official_repository':'https://github.com/terrarium-earth/Ad-Astra','branch_context':'1.20.1','commit':'5a986665e1d91e31c50321ff225a3fb23558ff35','url':'https://codeload.github.com/terrarium-earth/Ad-Astra/zip/5a986665e1d91e31c50321ff225a3fb23558ff35','archive':str(P),'archive_sha256':H(P.read_bytes()),'entries':entries,'not_executed':True}
(B/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
images=[]
for rel in entries:
 if rel.endswith('.png'):images.append(rel)
canvas=Image.new('RGB',(1100,700),'#555b60');d=ImageDraw.Draw(canvas)
for i,rel in enumerate(images):
 a=Image.open(B/'source'/rel).convert('RGBA');x=10+i%3*365;y=12+i//3*330;k=min(320//a.width,270//a.height);d.text((x,y),rel.split('/textures/')[-1]+' '+str(a.size),fill='white');a=a.resize((a.width*k,a.height*k),Image.Resampling.NEAREST);canvas.paste(a,(x,y+30),a)
canvas.save(B/'native-source-images.png');print('entries',len(entries),'png',len(images))
