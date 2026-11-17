"""Freeze twelve unread complete item sets. Charts are analysis, never game artwork."""
from pathlib import Path
from io import BytesIO
import json, hashlib, zipfile, subprocess, sys, importlib.util, math
from PIL import Image, ImageDraw, ImageFont

D=Path(__file__).resolve().parent; R=D.parents[2]
PRIOR=R/'docs/art/armor-local-complete-reference-20261104/combined-semantic-ledger.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x): (D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 inv=json.loads(Path('/tmp/dynasty-armor-extra-candidates-20261104.json').read_text())
 save('candidate-archive-scan.json',{'scope':'Filename-deduplicated previously unused local archives with four named item models. Not visual or independent design evidence.','archives':inv,'reference_credit':0})
 prior=json.loads(PRIOR.read_text()); selected=[]
 for token in ['l2complements-2.6.1','brutality-0.8.2','dreadsteel-1.20.1-1.1.9.jar','create-1.20.1-6.0.8','threateningly_mobs-1.0.9.82']:
  a=next(a for a in inv if token in Path(a['jar']).name)
  selected.extend((key,a['jar']) for key in a['families'])
 assert len(selected)==12 and not {k for k,_ in selected}&set(prior['reviewed_case_keys'])
 targets=json.loads(next((R/'docs/art/armor-local-complete-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D18继续实际未读完整四部件盔甲12名称族。复用532已读名称及203保守学习组；仅原样读取原作者资源学习MC图标、袖口连接、腰腿材质。换色/发光层/部件不算独立设计，1000有效独立设计未达前不制作，不改289保护路径、程序、共享Jar、用户实例、声音和亮度。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[]; decls=[]; worn=[]; metadata=[]; archives={}
 for key,jar in selected:
  ns,family=key.split(':'); archives[jar]={'path':jar,'sha256':sha(Path(jar))}
  with zipfile.ZipFile(jar) as z:
   def copy(e,folder,png=False):
    b=z.read(e); h=hashlib.sha256(b).hexdigest(); loc=Path(folder)/ns/f'{h[:12]}-{Path(e).name}';(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b)
    a={'jar':jar,'entry':e,'sha256':h,'local':str(loc)}
    if png:a['size']=list(Image.open(BytesIO(b)).size)
    return a
   icons=[]
   for part in ['helmet','chestplate','leggings','boots']:
    e=f'assets/{ns}/models/item/{family}_{part}.json'; model=json.loads(z.read(e));loc=model['textures']['layer0'];tns,tex=loc.split(':');entry=f'assets/{tns}/textures/{tex}.png'
    icon=copy(entry,'references',True); icons.append(icon)
    decls.append({'case_key':key,'part':part,'model':copy(e,'declarations'),'texture':icon,'texture_location':loc,'parent':model['parent'],'overrides':model.get('overrides',[]),'override_branches_not_counted':True})
    if entry+'.mcmeta' in z.namelist():metadata.append({'case_key':key,'source':icon,'metadata':copy(entry+'.mcmeta','animation-declarations')})
   cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
   if ns=='l2complements': entries=[f'assets/{ns}/textures/models/armor/{family}_layer_{i}.png' for i in [1,2]]
   elif ns=='create': entries=[f'assets/{ns}/textures/models/armor/cardboard_layer_{i}.png' for i in [1,2]]
   elif ns=='brutality':entries=[f'assets/{ns}/textures/armor/{family}_armor{s}.png' for s in ['', '_glowmask']]
   elif ns=='dreadsteel':entries=[f'assets/{ns}/textures/item/dreadsteel_armor_model_default.png']
   else:
    prefixes={'bionics_armor':['bionics','bionic_armor'],'desert_armor':['desert_armor'],'ebonlord_armor':['ebonlord']}[family]
    entries=[f'assets/{ns}/textures/models/armor/{p}_layer_{i}.png' for p in prefixes for i in [1,2]]
   for e in entries:
    assert e in z.namelist(),e
    worn.append({**copy(e,'worn-references',True),'case_key':key,'binding_proven':False,'role':'RAW_NATIVE_ATLAS_OR_GLOW_CANDIDATE_NOT_SELECTED_WEAR_PROOF'})
 save('provenance.json',{'archives':list(archives.values()),'cases':cases,'worn_textures':worn,'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
 save('resource-declarations.json',decls);save('animation-candidates.json',metadata)
 assert not metadata,'Animation requires separate original frame reading'
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'icon_chart_collector':CHART}
 save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':[k for k,_ in selected],'candidate_scan_sha256':sha(D/'candidate-archive-scan.json')})
 spec=importlib.util.spec_from_file_location('icons',CHART);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.main()
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
 for page,start in enumerate(range(0,len(worn),4),1):
  group=worn[start:start+4];heights=[max(130,a['size'][1]*min(3,max(1,512//max(a['size']))))+35 for a in group]
  out=Image.new('RGB',(1550,55+sum(heights)),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,10),'READ-ONLY RAW NATIVE ATLAS / integer enlargement / no player binding / NOT GAME',font=font,fill='white');y=50
  for a,h in zip(group,heights):
   im=Image.open(D/a['local']).convert('RGBA');scale=min(3,max(1,512//max(im.size)));im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
   dr.text((8,y+5),a['case_key'],font=font,fill='white');dr.text((8,y+27),Path(a['entry']).name,font=font,fill='#b7c0c4');dr.text((8,y+49),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4');out.paste(im,(530,y),im);y+=h
  out.save(D/f'worn-{page:02}.png')
 print(json.dumps({'cases':len(cases),'icons':len(decls),'raw_layers':len(worn),'pages':math.ceil(len(cases)/7)+math.ceil(len(worn)/4)}))
if __name__=='__main__':main()
