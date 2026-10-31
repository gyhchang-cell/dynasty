"""Read-only PNG/binding/standard-UV occupancy check, never a visual acceptance."""
from pathlib import Path
import datetime, hashlib, json, re
from PIL import Image
D=Path(__file__).resolve().parent
R=D.parents[2]
A=R/'src/main/resources/assets/dynasty/textures/models/armor'
source=R/'src/main/java/com/dynasty/DynastyArmorMaterials.java'
materials=re.findall(r'\bmake\("([a-z_]+)"',source.read_text())
errors=[]; rows=[]
for material in materials:
 for layer in (1,2):
  f=A/f'{material}_layer_{layer}.png'
  if not f.exists(): errors.append(str(f.relative_to(R)));continue
  with Image.open(f) as image:
   image.load(); w,h=image.size; alpha=image.convert('RGBA').getchannel('A')
   if w*32!=h*64: errors.append(f'{f.name}: not 64:32 aspect')
   zones={'body':(16,16,40,32),'leg':(0,16,16,32)} if layer==2 else {'head':(0,0,32,16),'body':(16,16,40,32),'arm':(40,16,56,32),'leg':(0,16,16,32)}
   coverage={}
   for name,b in zones.items():
    box=tuple(round(v*(w/64 if i%2==0 else h/32)) for i,v in enumerate(b))
    hist=alpha.crop(box).histogram(); coverage[name]=sum(hist[1:])
   empty=[name for name,n in coverage.items() if n==0]
   rows.append({'material':material,'layer':layer,'path':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':[w,h],'mode':image.mode,'nonzeroAlphaPixelsInStandardRegions':coverage,'emptyRegionsForManualReview':empty})
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_STATIC_BINDING_AND_PNG' if not errors else 'FAIL','materials':len(materials),'pngFiles':len(rows),'rows':rows,'errors':errors,'limits':['Region occupancy is not seam continuity or correct motif placement.','No wearing, gameplay, perspective, shader or live-world visual acceptance.','No texture, code, archive or save writes.'],'materialNamingSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()}
(D/'existing-armor-uv-static-20261028.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(report['status'],report['materials'],'materials',report['pngFiles'],'PNGs',len(errors),'errors',sum(bool(r['emptyRegionsForManualReview']) for r in rows),'maps with empty regions')
assert not errors
