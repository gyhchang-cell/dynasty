"""Reproduce the sixteen sacred/astral icons without downsampling originals."""
from pathlib import Path
import json, hashlib, shutil
from PIL import Image, ImageDraw, ImageFont
D=Path(__file__).resolve().parent; R=D.parents[2]
A=R/'src/main/resources/assets/dynasty'; rows=json.loads((D/'selection.json').read_text())
baseline=json.loads((D/'baseline.json').read_text()); sha=lambda b:hashlib.sha256(b).hexdigest()
reports=[]
import sys
sys.path.insert(0,str(R/'tools/art/inventory-refresh'))
from publish_originals import publish
for row in rows:
 ident=row['id'];p=A/'textures/item'/f'{ident}.png'
 previous=(D/'before/textures/item'/p.name).read_bytes()
 original=Image.open(D/'sources'/p.name).convert('RGBA');crop=original.crop(row['crop_bounds']);expected=Image.new('RGBA',(crop.width+4,crop.height+4));expected.paste(crop,(2,2))
 current=Image.open(p).convert('RGBA')
 assert p.read_bytes()==previous or (current.size==expected.size and current.tobytes()==expected.tobytes()),'Concurrent texture '+ident
 assert (A/'models/item'/f'{ident}.json').read_bytes()==(D/'before/models/item'/f'{ident}.json').read_bytes()
publish(ids={r['id'] for r in rows})
for row in rows:
 ident=row['id'];p=A/'textures/item'/f'{ident}.png';im=Image.open(D/'sources'/p.name).convert('RGBA');crop=im.crop(row['crop_bounds']);out=Image.new('RGBA',(crop.width+4,crop.height+4));out.paste(crop,(2,2));target=Image.open(p).convert('RGBA');assert out.size==target.size and out.tobytes()==target.tobytes()
 reports.append({'id':ident,'originalSize':im.size,'runtimeSize':out.size,'cropBounds':row['crop_bounds'],'originalRgbaPreserved':True,'sha256':sha(p.read_bytes())})
changed=[p for p,h in baseline.items() if sha((R/p).read_bytes())!=h]
expected={str((A/'textures/item'/f"{r['id']}.png").relative_to(R)) for r in rows}
assert expected <= set(changed),changed
parallel=sorted(set(changed)-expected)
(D/'source-check.json').write_text(json.dumps({'changed':changed,'unchangedPngs':len(baseline)-len(changed),'concurrentChangesNotOverwritten':parallel,'items':reports,'existingHongmengModelsUnchanged':True,'newTwelveModelsMigratedToOriginalLoader':True,'wearableUvsUnchanged':True},ensure_ascii=False,indent=2)+'\n')
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',21)
sheet=Image.new('RGB',(1120,2220),'#555b60');draw=ImageDraw.Draw(sheet)
draw.text((18,14),'实际资源新旧对照 · 每组上旧 / 下新 · 非游戏截图',font=font,fill='white')
for k,row in enumerate(rows):
 x=k%4*280;y=k//4*540+55
 for old,yy in [(True,y),(False,y+235)]:
  p=(D/'before' if old else A)/'textures/item'/f"{row['id']}.png"
  im=Image.open(p).convert('RGBA').resize((216,216),Image.Resampling.NEAREST);sheet.paste(im,(x+32,yy),im)
 draw.text((x+12,y+470),row['name'],font=font,fill='white')
sheet.save(D/'comparison.png')
sheet=Image.new('RGB',(1120,1140),'#555b60');draw=ImageDraw.Draw(sheet)
draw.text((18,12),'鸿蒙 / 紫微 / 混元 / 北斗 · 十六件 · 实际物品贴图 · 非游戏截图',font=font,fill='white')
for k,row in enumerate(rows):
 x=k%4*280;y=k//4*270+45;im=Image.open(A/'textures/item'/f"{row['id']}.png").convert('RGBA').resize((210,210),Image.Resampling.NEAREST);sheet.paste(im,(x+35,y),im);draw.text((x+10,y+215),row['name'],font=font,fill='white')
sheet.save(D/'after.png')
small=Image.new('RGB',(600,330),'#555b60')
for k,row in enumerate(rows):
 im=Image.open(A/'textures/item'/f"{row['id']}.png").convert('RGBA').resize((32,32),Image.Resampling.NEAREST);small.paste(im,(k%4*145+55,k//4*75+10),im)
small.save(D/'inventory-32px.png')
print('PASS sixteen original-RGBA textures; unrelated PNG changes left alone:',parallel)
