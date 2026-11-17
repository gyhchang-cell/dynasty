"""Freeze newly unread complete local item sets; source atlases remain unbound candidates."""
from pathlib import Path
from io import BytesIO
import json,hashlib,zipfile,subprocess,sys,importlib.util,math
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2]
PRIOR=R/'docs/art/armor-organic-complete-reference-20261104/combined-semantic-ledger.json'
INV=R/'docs/art/armor-additional-design-reference-20261104/candidate-archive-scan.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
TOKENS=['radiation_zone_reborn-1.3.2.1','PasterDream-forge1.20.1','TheOuterEnd-1.0.13','sons-of-sins-1.20.1','Gobber2-Forge-1.20.1-2.8.9','inventorypets-1.20.1-2.2.8','deeperdarker-forge-1.20.1-1.3.3','EvilHunter 2.1.1','torchesbecomesunlight-0.4.7','Cardinal Sins 1.0.3','echovoids-2.0.3b','cultofazazelforge-1.1.4.12']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 prior=json.loads(PRIOR.read_text());inv=json.loads(INV.read_text())['archives'];selected=[]
 for token in TOKENS:
  a=next(a for a in inv if token in Path(a['jar']).name)
  selected.extend((k,a['jar']) for k in a['families'] if k not in prior['reviewed_case_keys'])
 assert len(selected)==24 and len({k for k,_ in selected})==24
 targets=json.loads(next((R/'docs/art/armor-organic-complete-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D20沿555已读名称/205保守学习组断点，实际阅读24未读四部件名称的图标和候选源图；整套语义去重，换色/图层不算独立设计。仅阅读，不重跑过去批次核查；未达到1000有效独立设计不制作、不改289保护路径/程序/共享Jar/用户实例，不开游戏或声光。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[];decls=[];worn=[];meta=[];archives={}
 for key,jar in selected:
  ns,family=key.split(':');archives[jar]={'path':jar,'sha256':sha(Path(jar))}
  with zipfile.ZipFile(jar) as z:
   def copy(e,folder,png=False):
    b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path(folder)/ns/f'{h[:12]}-{Path(e).name}';(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);a={'jar':jar,'entry':e,'sha256':h,'local':str(loc)}
    if png:a['size']=list(Image.open(BytesIO(b)).size)
    return a
   icons=[]
   for part in ['helmet','chestplate','leggings','boots']:
    e=f'assets/{ns}/models/item/{family}_{part}.json';m=json.loads(z.read(e));loc=m['textures']['layer0'];tns,t=loc.split(':');entry=f'assets/{tns}/textures/{t}.png';icon=copy(entry,'references',True);icons.append(icon);decls.append({'case_key':key,'part':part,'model':copy(e,'declarations'),'texture':icon,'texture_location':loc,'parent':m['parent'],'overrides':m.get('overrides',[])})
    if entry+'.mcmeta' in z.namelist():meta.append({'case_key':key,'source':icon,'metadata':copy(entry+'.mcmeta','animation-declarations')})
   cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
   explicit={
    'radiation_zone_reborn:giantrock_armor':['models/armor/giantrock_armor_layer_1','models/armor/giantrock_armor_layer_2','entities/giantrock_protective_mask_layer'],
    'radiation_zone_reborn:sedisilver_armor':['models/armor/sedisilver_armor_layer_1','models/armor/sedisilver_armor_layer_2','entities/sedisilver_protective_mask_layer'],
    'radiation_zone_reborn:protective':['entities/protective_'+p+'_layer' for p in ['mask','clothing','leggings','boots']],
    'radiation_zone_reborn:tyrant_skin_armor':['entities/tyrant_skin_armor_layer'],
    'radiation_zone_reborn:wastefur_armor':['entities/wastefur_'+p+'_layer' for p in ['helmet','cloak','leggings','boots']],
    'cardinal_sins:robed_armor':['models/armor/robedarmorplaceholder_layer_1','models/armor/robedarmorplaceholder_layer_2','entities/robedarmor_texture'],
    'netherman:azazel':['models/armor/believer_armor']}
   if key in explicit:rel=explicit[key]
   elif ns=='pasterdream':
    pre={'copper_armor':'tong__','dyedream_armor':'ran_meng__','qym_armor':'qym_','sculk_armor':'hui_xiang__','titanium_armor':'tai__'}[family];rel=[f'models/armor/{pre}_layer_{i}' for i in [1,2]]
   elif ns=='outer_end':rel=[f'models/armor/{family.removesuffix("_crystal")}_layer_{i}' for i in [1,2]]
   elif ns=='sons_of_sins':rel=[f'models/armor/soul_steel_layer_{i}' for i in [1,2]]
   elif ns=='evilhunter':rel=[f'models/armor/armor_layer_{i}' for i in [1,2]]
   elif ns=='cardinal_sins':rel=[f'models/armor/darksteelarmor_placeholder_layer_{i}' for i in [1,2]]
   elif ns=='echovoids':rel=[f'models/armor/chainmail_layer_{i}' for i in [1,2]]
   elif ns=='torchesbecomesunlight':rel=[] # Same-named entity skins are not assumed to be armor atlases.
   else:rel=[f'models/armor/{family}_layer_{i}' for i in [1,2]]
   for p in rel:
    e=f'assets/{ns}/textures/{p}.png';assert e in z.namelist(),e
    worn.append({**copy(e,'worn-references',True),'case_key':key,'binding_proven':False,'role':'RAW_NATIVE_ATLAS_CANDIDATE_NO_PLAYER_OR_TARGET_BINDING_PROOF'})
 save('provenance.json',{'archives':list(archives.values()),'cases':cases,'worn_textures':worn,'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
 save('resource-declarations.json',decls);save('animation-candidates.json',meta)
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'candidate_inventory':INV,'icon_chart_collector':CHART}
 save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':[k for k,_ in selected]})
 spec=importlib.util.spec_from_file_location('chart',CHART);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.main()
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
 for page,start in enumerate(range(0,len(worn),4),1):
  group=worn[start:start+4];heights=[max(130,a['size'][1]*min(3,max(1,512//max(a['size']))))+35 for a in group];out=Image.new('RGB',(1550,55+sum(heights)),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,10),'READ-ONLY RAW NATIVE ATLAS / no actual selected player binding / NOT GAME',font=font,fill='white');y=50
  for a,h in zip(group,heights):
   im=Image.open(D/a['local']).convert('RGBA');s=min(3,max(1,512//max(im.size)));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);dr.text((8,y+5),a['case_key'],font=font,fill='white');dr.text((8,y+27),Path(a['entry']).name,font=font,fill='#b7c0c4');dr.text((8,y+49),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4');out.paste(im,(530,y),im);y+=h
  out.save(D/f'worn-{page:02}.png')
 print(json.dumps({'cases':len(cases),'icons':len(decls),'raw_layers':len(worn),'animated_icon_entries':len(meta),'pages':math.ceil(len(cases)/7)+math.ceil(len(worn)/4)}))
if __name__=='__main__':main()
