from pathlib import Path
import zipfile,re,io,hashlib,json,collections
from PIL import Image,ImageDraw
O=Path('docs/art/weapons-existing-v6');P=Path('/Users/a15356015027/Public/.minecraft/versions');target=P/'登神者：天阶咏叹v1.5'
archives=list((target/'mods').glob('*.jar'))+list((target/'resourcepacks').glob('*.zip'))
archives+=list(Path('/tmp/dynasty-weapon-study-20261015').glob('*.zip'))
archives+=list(P.glob('*/mods/*.jar'))
archives.append(P/'1.20.1/1.20.1.jar')
archives+=list(Path('/tmp/dynasty-bow-ge-study').rglob('*.zip'))
excluded={(x['archive'],x['path']) for x in json.load(open(O/'excluded-paths.json'))}
seenfiles=set();seenpixels=set();rows=[];ims=[]
pattern=re.compile(r'sword|katana|saber|sabre|rapier|scimitar|cutlass|claymore|falchion|zweihander|estoc|flamberge|dagger|uchigatana|wakizashi|tachi|greatblade')
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
       if k.startswith('item.') and re.search(r'\b(sword|dagger|katana|saber|rapier|scimitar|cutlass|claymore|greatsword|longsword|shortsword)\b',str(t),re.I):names.add(k.split('.')[-1])
     except Exception:pass
   for n in z.namelist():
    name=Path(n).stem.lower()
    if not n.endswith('.png') or not re.search('/textures/items?/',n) or not (pattern.search(name) or name in names):continue
    if (str(ar),n) in excluded:continue
    if re.search('fragment|broken|shard|swordfish|charm|tassel|sheath|handle|blade_part|guard|projectile|emissive|overlay|_layer|_model|enchanted|/parts/|sword_blade|_hilt|empty_slot|sword_spell|sword_logo|sword_knot|_in_hand|template|banner_pattern|upgrade|_tex|_clear|_solid',n):continue
    im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
    if im.width!=im.height or im.width>128 or im.width<16:continue
    h=hashlib.sha256(im.tobytes()).hexdigest()
    if h in seenpixels:continue
    seenpixels.add(h);rows.append({'number':len(rows)+1,'name':name,'archive':str(ar),'path':n,'size':im.size,'pixel_sha256':h,'dengshen':str(target) in str(ar)});ims.append(im)
 except Exception:continue
print('unique sword-like sprites',len(rows),'Dengshen',sum(x['dengshen'] for x in rows),flush=True)
(O/'reference-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
rows=rows[:1000];ims=ims[:1000];(O/'references.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for page in range((len(rows)+99)//100):
 c=Image.new('RGB',(1500,1500),'#343e46');d=ImageDraw.Draw(c)
 for j,(r,im) in enumerate(zip(rows[page*100:(page+1)*100],ims[page*100:(page+1)*100])):
  x=j%10*150;y=j//10*150;s=max(1,min(106//im.width,106//im.height));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);c.paste(im,(x+(150-im.width)//2,y),im);d.text((x+2,y+111),str(r['number'])+(' DS' if r['dengshen'] else ''),fill='white');d.text((x+2,y+125),r['name'][:23],fill='white')
 c.save(O/f'reference-{page+1:02}.png')
print('pages ready',len(rows),flush=True)
