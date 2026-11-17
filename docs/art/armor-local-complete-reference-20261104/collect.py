"""Freeze unviewed four-part local sets; raw atlas candidates are not worn binding proof."""
from pathlib import Path
from io import BytesIO
import hashlib, json, zipfile, subprocess, sys, importlib.util
from PIL import Image, ImageDraw, ImageFont
D=Path(__file__).resolve().parent; R=D.parents[2]
PRIOR=R/'docs/art/armor-unindexed-reference-20261104/combined-semantic-ledger.json'
INV=R/'docs/art/armor-unindexed-reference-20261104/candidate-inventory.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x): (D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 prior=json.loads(PRIOR.read_text()); inv=json.loads(INV.read_text()); rows={}
 for r in inv['candidate_complete_name_sets']:
  if r['case_key'] in prior['reviewed_case_keys'] or any(p['previously_seen_pixels'] for p in r['parts']): continue
  k=r['case_key']
  if k not in rows or '1.20.1_1.7.4' in r['jar'] or 'v0.6.3' in r['jar']: rows[k]=r
 assert len(rows)==41
 targets=json.loads(next((R/'docs/art/armor-unindexed-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','继续未读完整四部件41名称族本地参考；复用491已读名称/200保守学习组。实际查看原始图标和候选图集、按材料轮廓和UV学习去重，不把名称/部件/换色/动画/图层当设计数。未达1000有效独立设计前不生产、不更改游戏资源，不触碰289保护路径与共享Jar/实例；完整独立总数未知。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[]; decls=[]; worn=[]; archives={}; metadata=[]
 for key,r in rows.items():
  jar=r['jar']; ns,family=key.split(':'); assert sha(Path(jar))==r['archive_sha256']; archives[jar]={'path':jar,'sha256':r['archive_sha256']}
  with zipfile.ZipFile(jar) as z:
   def copy(e,folder,png=False):
    b=z.read(e); h=hashlib.sha256(b).hexdigest(); local=Path(folder)/ns/f'{h[:12]}-{Path(e).name}'; (D/local).parent.mkdir(parents=True,exist_ok=True); (D/local).write_bytes(b)
    a={'jar':jar,'entry':e,'sha256':h,'local':str(local)}
    if png: a['size']=list(Image.open(BytesIO(b)).size)
    return a
   icons=[]
   for part in ['helmet','chestplate','leggings','boots']:
    item=next(a for a in r['parts'] if a['part']==part); model=json.loads(z.read(item['model'])); loc=model['textures']['layer0']; tns,tex=loc.split(':'); assert item['texture']==f'assets/{tns}/textures/{tex}.png'
    icon=copy(item['texture'],'references',True); assert icon['sha256']==item['sha256']; icons.append(icon)
    decls.append({'case_key':key,'part':part,'model':copy(item['model'],'declarations'),'texture':icon,'texture_location':loc,'parent':model['parent']})
    if item['texture']+'.mcmeta' in z.namelist(): metadata.append({'case_key':key,'source':icon,'metadata':copy(item['texture']+'.mcmeta','animation-declarations')})
   cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
   explicit={
    'ulterlands:astrumm_set':['entities/astrumm_full'],
    'born_in_chaos_v1:nightmare_mantleofthe_night':['entities/nightrobeboot','entities/nightrobebreastplate','entities/nightrobeleggings','entities/nightrobemasc'],
    'born_in_chaos_v1:dark_metal_armor':['models/armor/darkmetar_layer_1','models/armor/darkmetar_layer_2'],
    'malum:soul_stained_steel':['armor/soul_stained_steel_reforged'],
    'mythsandlegends:infernum_warplate':['models/infernum_warplate_armor','models/infernum_warplate_armor_arm']}
   if key in explicit: entries=[f'assets/{ns}/textures/{e}.png' for e in explicit[key]]
   elif ns=='terra_equipment': entries=[f'assets/{ns}/textures/item/armor/{family}_armor.png']
   elif ns=='terramity':
    base=family.removesuffix('_armor'); entries=[f'assets/{ns}/textures/models/armor/{base}__layer_{i}.png' for i in [1,2]]+[f'assets/{ns}/textures/entities/{family if family.endswith("_armor") else family+"_armor"}.png']
   elif ns=='monsterexpansion': entries=[f'assets/{ns}/textures/models/armor/{family}_{tail}.png' for tail in ['armor','helmet','chestplate','leggings','boots']]
   elif ns=='fantasy_ending': entries=[f'assets/{ns}/textures/models/armor/{family}_armor_layer_{i}.png' for i in [1,2]]
   elif ns=='splendour_ablaze_epoch': entries=[f'assets/{ns}/textures/models/armor/mold_tin_layer_{i}.png' for i in [1,2]]
   elif ns=='lethality': entries=[f'assets/{ns}/textures/models/armor/hf_battle_maid_layer{s}.png' for s in ['', '_1','_2']]
   else: raise AssertionError(key)
   for e in entries:
    if e in z.namelist(): worn.append({**copy(e,'worn-references',True),'case_key':key,'binding_proven':False,'role':'RAW_NATIVE_ATLAS_CANDIDATE_NO_PLAYER_OR_TARGET_BINDING_PROOF'})
 save('provenance.json',{'archives':list(archives.values()),'cases':cases,'worn_textures':worn,'icon_name_families':41,'icon_png':164,'native_layer_candidates':len(worn),'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
 save('resource-declarations.json',decls); save('animation-candidates.json',metadata)
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'candidate_inventory':INV,'icon_chart_collector':CHART}
 save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':list(rows),'skipped_previously_reviewed_cases':prior['reviewed_case_keys']})
 assert not metadata, 'Inspect actual animation metadata before charting'
 spec=importlib.util.spec_from_file_location('icons',CHART); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.D=D; m.main()
 # Four source atlases per page; dynamic page height preserves every source pixel.
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
 for page,start in enumerate(range(0,len(worn),4),1):
  group=worn[start:start+4]; heights=[max(130,a['size'][1]*(min(3,max(1,512//max(a['size'])))))+35 for a in group]
  out=Image.new('RGB',(1550,55+sum(heights)),(68,73,78)); dr=ImageDraw.Draw(out); dr.text((8,10),'RAW NATIVE ATLAS CANDIDATES / no selected worn binding inferred / integer enlarged / NOT GAME',font=font,fill='white'); y=50
  for a,h in zip(group,heights):
   im=Image.open(D/a['local']).convert('RGBA'); scale=min(3,max(1,512//max(im.size))); im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
   dr.text((8,y+5),a['case_key'],font=font,fill='white'); dr.text((8,y+27),Path(a['entry']).name,font=font,fill='#b7c0c4'); dr.text((8,y+49),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4'); out.paste(im,(530,y),im); y+=h
  out.save(D/f'worn-{page:02}.png')
 print(json.dumps({'cases':len(cases),'icons':164,'raw_layers':len(worn),'animation_metadata':len(metadata)}))
if __name__=='__main__': main()
