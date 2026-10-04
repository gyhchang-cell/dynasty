"""Read-only reference extraction/contact sheets, never run resource generators."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import zipfile, io, json, hashlib, statistics
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/art/native16-rework-v11/accessory-research'
TMP=ROOT/'work/native16-v11/accessories'
OUT.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
sets=[
 ('The Fool 0.2.2 / Goety','愚者','goety',Path('/Users/a15356015027/Public/.minecraft/versions/愚者/mods/goety-2.5.36.1.jar'),[
 'alarming_charm','amethyst_necklace','feline_amulet','pendant_of_hunger','ring_of_force','ring_of_the_dragon','ring_of_the_forge','ring_of_thirst','ring_of_want','sea_amulet','star_amulet','warding_charm','focus_bag','empty_totem','soul_ruby','soul_emerald']),
 ('Ascender 1.5 / Artifacts','登神者：天阶咏叹v1.5','artifacts',Path('/Users/a15356015027/Public/.minecraft/versions/登神者：天阶咏叹v1.5/mods/[奇异饰品] artifacts-forge-9.5.16.jar'),[
 'antidote_vessel','charm_of_sinking','chorus_totem','cloud_in_a_bottle','cross_necklace','crystal_heart','flame_pendant','golden_hook','lucky_scarf','onion_ring','panic_necklace','shock_pendant','thorn_pendant','universal_attractor']),
 ('Ascender 1.5 / Relics','登神者：天阶咏叹v1.5','relics',Path('/Users/a15356015027/Public/.minecraft/versions/登神者：天阶咏叹v1.5/mods/[遗物] relics-1.20.1-0.8.0.13.jar'),[
 'bastion_ring','camouflage_ring','delay_ring','ghost_skin_talisman','holy_locket','jellyfish_necklace','magic_mirror_0','reflection_necklace','scarab_talisman','spider_necklace'])]
items=[]
for title,pack,ns,jar,names in sets:
 jar_hash=hashlib.sha256(jar.read_bytes()).hexdigest()
 with zipfile.ZipFile(jar) as z:
  for name in names:
   path=f'assets/{ns}/textures/item/{name}.png';data=z.read(path);im=Image.open(io.BytesIO(data)).convert('RGBA')
   assert im.width==16 and im.height%16==0
   # Animated strips: only first authored 16x16 frame is used for static silhouette study.
   frame=im.crop((0,0,16,16));p=TMP/f'{ns}-{name}.png';frame.save(p)
   mcmeta=json.loads(z.read(path+'.mcmeta')) if path+'.mcmeta' in z.namelist() else None
   nonzero=[v for v in frame.get_flattened_data() if v[3]>0]
   colors=len(set(nonzero));alphas=sorted(set(v[3] for v in frame.get_flattened_data()))
   model=f'assets/{ns}/models/item/{name}.json'
   items.append({'index':len(items)+1,'reference_id':f'{ns}:{name}','pack':pack,'source_label':title,'source_archive':str(jar),'source_archive_sha256':jar_hash,'archive_texture_path':path,'png_sha256':hashlib.sha256(data).hexdigest(),'source_dimensions':list(im.size),'displayed_frame':[0,0,16,16],'unique_visible_rgba':colors,'alpha_values':alphas,'visible_pixels':len(nonzero),'animation_metadata':mcmeta,'item_model':json.loads(z.read(model)) if model in z.namelist() else None,'frame_path':str(p),'usage':'Visual research only; third-party artwork remains its owners. No pixel/pattern copying into Dynasty.'})
font=ImageFont.truetype('/System/Library/Fonts/Monaco.ttf',11)
fontSmall=ImageFont.truetype('/System/Library/Fonts/Monaco.ttf',9)
for pi in range(2):
 sheet=Image.new('RGB',(1200,790),'#20242a');d=ImageDraw.Draw(sheet)
 d.text((15,12),f'ACCESSORY REFERENCE STUDY {pi+1}/2 - Original 16x16 + nearest-neighbor 6x; not Dynasty art',font=font,fill='#eeeeec')
 d.text((15,32),'Third-party local JAR assets; composition, silhouette and cluster analysis only.',font=font,fill='#b7bfca')
 for k,v in enumerate(items[pi*20:(pi+1)*20]):
  x=10+(k%5)*238;y=60+(k//5)*180
  d.rounded_rectangle((x,y,x+228,y+169),radius=6,fill='#2d3239')
  im=Image.open(v['frame_path']).convert('RGBA')
  for yy in range(96):
   for xx in range(96):
    sheet.putpixel((x+12+xx,y+42+yy), (62,68,77) if ((xx//12+yy//12)%2) else (53,59,67))
  big=im.resize((96,96),Image.Resampling.NEAREST);sheet.paste(big,(x+12,y+42),big)
  sheet.paste(im,(x+156,y+69),im)
  d.text((x+10,y+8),f"{v['index']:02} {v['reference_id'].split(':')[0]}",font=font,fill='white')
  d.text((x+10,y+25),v['reference_id'].split(':')[1],font=fontSmall,fill='white')
  d.text((x+139,y+47),'1x 16px',font=fontSmall,fill='#c7d1dc')
  d.text((x+120,y+99),f"{v['unique_visible_rgba']} colors",font=fontSmall,fill='#c7d1dc')
  d.text((x+10,y+149),v['source_label'],font=fontSmall,fill='#aab9ca')
 sheet.save(OUT/f'reference-contact-{pi+1}.png')
native=Image.new('RGB',(240,192),'#252a30');d=ImageDraw.Draw(native)
for k,v in enumerate(items):
 x=(k%10)*24+4;y=(k//10)*48+22;im=Image.open(v['frame_path']);native.paste(im,(x,y),im);d.text((x,y-13),str(v['index']),font=fontSmall,fill='white')
native.save(OUT/'reference-native-1x.png')
manifest={'purpose':'40 accessory/material item references, separate from the >=500 block study; no texture copying or recoloring.','distinct_reference_count':len(items),'source_packs':['愚者 / The Fool 0.2.2','登神者：天阶咏叹v1.5'],'source_mods':['Goety 2.5.36.1','Artifacts 9.5.16','Relics 0.8.0.13'],'reference_pixel_grid':[16,16],'first_frame_only_for_animated_relics':True,'active_resource_pack_order_not_resolved':True,'items':items}
(OUT/'reference-sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'references':len(items),'visible_colors_range':[min(v['unique_visible_rgba'] for v in items),max(v['unique_visible_rgba'] for v in items)],'visible_colors_median':statistics.median(v['unique_visible_rgba'] for v in items),'binary_alpha_count':sum(set(v['alpha_values']) <= {0,255} for v in items)},indent=2))
