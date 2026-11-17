from pathlib import Path
import zipfile,re,io,hashlib,json,collections
from PIL import Image,ImageDraw
O=Path('docs/art/axe-study-v12');O.mkdir(exist_ok=True);P=Path('/Users/a15356015027/Public/.minecraft/versions');target=P/'登神者：天阶咏叹v1.5'
archives=list((target/'mods').glob('*.jar'))+list((target/'resourcepacks').glob('*.zip'))
archives+=list(Path('/tmp/dynasty-weapon-study-20261015').glob('*.zip'))
archives+=list(P.glob('*/mods/*.jar'))
archives.append(P/'1.20.1/1.20.1.jar')
archives+=list(Path('/tmp/dynasty-bow-ge-study').rglob('*.zip'))
excluded=set()
seenfiles=set();seenpixels=set();rows=[];ims=[]
pattern=re.compile(r'axe|hatchet|tomahawk|halberd')
for ar in archives:
 if ar.name in seenfiles:continue
 seenfiles.add(ar.name)
 if 'dynasty' in ar.name.lower():continue
 try:
  with zipfile.ZipFile(ar) as z:
   names=set()
   for ln in z.namelist():
    if ln.endswith('/lang/en_us.json'):
     try:
      for k,t in json.loads(z.read(ln)).items():
       if k.startswith('item.') and re.search(r'\b(axe|battleaxe|greataxe|hatchet|tomahawk|halberd)\b',str(t),re.I):names.add(k.split('.')[-1])
     except Exception:pass
   for n in z.namelist():
    name=Path(n).stem.lower()
    if not n.endswith('.png') or not re.search('/textures/items?/',n) or not (pattern.search(name) or name in names):continue
    if re.search(r'pickaxe|pick_axe|waxed|axe_head|axehead|hatchet_head|/parts/|_head|_handle|_blade|/armor/',n):continue
    if re.search('fragment|broken|shard|swordfish|charm|tassel|sheath|handle|blade_part|guard|projectile|emissive|overlay|_layer|_model|enchanted|/parts/|sword_blade|_hilt|empty_slot|sword_spell|sword_logo|sword_knot|_in_hand|template|banner_pattern|upgrade|_tex|_clear|_solid',n):continue
    im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
    if im.width!=im.height or im.width>128 or im.width<16:continue
    h=hashlib.sha256(im.tobytes()).hexdigest()
    if h in seenpixels:continue
    seenpixels.add(h);rows.append({'mod':n.split('assets/')[1].split('/')[0],'number':len(rows)+1,'name':name,'archive':str(ar),'path':n,'size':im.size,'pixel_sha256':h,'dengshen':str(target) in str(ar)});ims.append(im)
 except Exception:continue
print('unique axe-like sprites',len(rows),'Dengshen',sum(x['dengshen'] for x in rows),flush=True)
(O/'reference-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(O/'references.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for page in range((len(rows)+99)//100):
 c=Image.new('RGB',(1500,1500),'#343e46');d=ImageDraw.Draw(c)
 for j,(r,im) in enumerate(zip(rows[page*100:(page+1)*100],ims[page*100:(page+1)*100])):
  x=j%10*150;y=j//10*150;s=max(1,min(106//im.width,106//im.height));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);c.paste(im,(x+(150-im.width)//2,y),im);d.text((x+2,y+111),str(r['number'])+(' DS' if r['dengshen'] else ''),fill='white');d.text((x+2,y+125),r['name'][:23],fill='white')
 c.save(O/f'reference-{page+1:02}.png')
print('pages ready',len(rows),flush=True)

(O/'summary.json').write_text(json.dumps({'unique_sprites':len(rows),'namespaces':len(set(r['mod'] for r in rows)),'counts':dict(collections.Counter(r['mod'] for r in rows)),'note':'Decoded RGBA dedup; material variants remain; automatic candidates need visual inspection.'},indent=2))
