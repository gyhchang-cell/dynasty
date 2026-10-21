import pathlib,zipfile,re,json,hashlib,io,collections
from PIL import Image,ImageDraw
base=pathlib.Path('/tmp/dynasty-bow-ge-study');out=pathlib.Path('docs/art/basic-weapons-thicker-v2');out.mkdir(parents=True,exist_ok=True)
rows=json.loads((base/'candidates.json').read_text())
# Add downloaded official sources and unconventional melee from previously reviewed official libraries.
archives=list(base.glob('*.zip'))+list(pathlib.Path('/tmp/dynasty-weapon-study-20261015').glob('*.zip'))
for p in archives:
 z=zipfile.ZipFile(p)
 for n in z.namelist():
  if not re.search(r'/textures/items?/',n) or not n.endswith('.png'):continue
  s=pathlib.PurePosixPath(n).stem
  typ='scythe' if re.search('scythe|sickle',s) else 'bow' if 'bow' in s and 'crossbow' not in s else 'unconventional' if re.search(r'chakram|warglaive|twinblade|sai|flanged_mace|quarterstaff|halberd|guisarme|ranseur|ahlspiess|lucernhammer|warhammer',s) else None
  if typ:rows.append({'category':typ,'name':s,'archive':str(p),'path':n})

def rank(r):
 a=r['archive']
 if r['category']=='bow' and 'terra_equipment' in a:return 0
 if '/tmp/' in a:return 0
 if any(s in a for s in ['l2archery','l2weaponry','simplyswords','AgeOfWeapons','goety','malum','soulslike','Divine Weaponry']):return 1
 return 2
selected=[];images=[]
for cat in ['bow','scythe','unconventional']:
 seen=set();ids=set();count=0
 for r in sorted([r for r in rows if r['category']==cat],key=lambda r:(rank(r),r['archive'],r['path'])):
  n=r['path'];s=r['name'];a=r['archive']
  if cat=='bow' and (re.search(r'_[1-9]$|standby_[1-9]$|bowhead|template',s) or s in ('items','item')):continue
  if cat=='bow' and re.search(r'bowcaster|_clear$|_solid$|^bow_[ns]$|lil_bow|lilbow|sidebow|bow_of_revelation',s):continue
  if cat=='scythe' and re.search(r'scythed_|soul_of_',s):continue
  if re.search(r'pull|loaded|arrow|bolt|layer|overlay|_e$|emissive|lights|broken|fragment|projectile|coating|/parts/|huge|_model|_handheld|_pre_|_alt|_old|_use|_2d|_3d',n):continue
  if 'dynasty' in pathlib.Path(a).name.lower() or 'rainbow' in s or re.search(r'bowl|elbow|bowtie|bow_tie|soup|/food/|/mana_staff/',n):continue
  if cat=='scythe' and '/generated/' in n and 'l2weaponry' in n:continue
  if 'lucky_block' in a:continue
  try:
   z=zipfile.ZipFile(a);raw=z.read(n);im=Image.open(io.BytesIO(raw)).convert('RGBA')
   if im.height!=im.width or im.width>128:continue
   h=hashlib.sha256(im.tobytes()).hexdigest();ident=re.sub(r'_(gui|icon|sprite|inventory)$','',n.split('/textures/')[-1])
   namespace=n.split('/assets/')[-1].split('/')[0] if '/assets/' in n else n.split('assets/')[-1].split('/')[0]
   ident=namespace+':'+ident
   if h in seen or ident in ids:continue
   seen.add(h);ids.add(ident);r={**r,'number':count+1,'sha256':hashlib.sha256(raw).hexdigest(),'size':im.size};selected.append(r);images.append(im);count+=1
   if count==100:break
  except Exception:pass
 print(cat,count)
(out/'references-300.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
for cat in ['bow','scythe','unconventional']:
 pairs=[(r,im) for r,im in zip(selected,images) if r['category']==cat]
 for page in range((len(pairs)+49)//50):
  canvas=Image.new('RGB',(1200,1000),'#30343a');d=ImageDraw.Draw(canvas)
  for j,(r,im) in enumerate(pairs[page*50:(page+1)*50]):
   x=j%10*120;y=j//10*200;sc=max(1,min(100//im.width,145//im.height));im=im.resize((im.width*sc,im.height*sc),Image.Resampling.NEAREST);canvas.paste(im,(x+(120-im.width)//2,y+4),im)
   label=r['name'] if r['name'] not in ('bow','scythe') else pathlib.PurePosixPath(r['path']).parent.name
   d.text((x+3,y+155),str(r['number']),fill='white');d.text((x+3,y+170),label[:19],fill='white');d.text((x+3,y+183),label[19:38],fill='white')
  canvas.save(base/f'{cat}-{page+1}.png')
