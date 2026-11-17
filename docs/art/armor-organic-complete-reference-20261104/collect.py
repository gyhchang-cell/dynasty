"""Read eleven unread complete organic armor item designs and exact static texture declarations."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,sys,shutil,importlib.util,re,math
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
D=Path(__file__).resolve().parent;R=D.parents[2]
PRIOR=R/'docs/art/armor-additional-design-reference-20261104/combined-semantic-ledger.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
INV=R/'docs/art/armor-additional-design-reference-20261104/candidate-archive-scan.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 src=next(a for a in json.loads(INV.read_text())['archives'] if 'macabre-0.8.4' in a['jar']);jar=src['jar'];keys=src['families'];prior=json.loads(PRIOR.read_text());assert len(keys)==11 and not set(keys)&set(prior['reviewed_case_keys'])
 targets=json.loads(next((R/'docs/art/armor-additional-design-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D19继续十一未读完整有机盔甲的真实原始图标及原生图层。复用544名称/205学习组，读实际静态纹理返回声明，专用有机UV不套原版；部件/图层/版本/换色不算独立设计。1000完整有效独立设计未达前不制作，精致旧稿和289路径、声音亮度、共享Jar和用户实例不变。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[];decls=[];worn=[];metadata=[];classes=[];bindings=[];geometry=[]
 javap=Path(shutil.which('javap'));jhash=sha(javap.resolve())
 with zipfile.ZipFile(jar) as z:
  def copy(e,folder,png=False):
   b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path(folder)/f'{h[:12]}-{Path(e).name}';(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);a={'jar':jar,'entry':e,'sha256':h,'local':str(loc)}
   if png:a['size']=list(Image.open(BytesIO(b)).size)
   return a
  def disasm(e):
   a=copy(e,'classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/a['local'])],text=True);loc=Path('disassembly')/(Path(e).name+'.txt');(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=str(loc),disassembly_sha256=sha(D/loc));classes.append(a);return a,out
  for key in keys:
   family=key.split(':')[1];icons=[]
   for part in ['helmet','chestplate','leggings','boots']:
    e=f'assets/macabre/models/item/{family}_{part}.json';m=json.loads(z.read(e));loc=m['textures']['layer0'];ns,t=loc.split(':');entry=f'assets/{ns}/textures/{t}.png';icon=copy(entry,'references',True);icons.append(icon);decls.append({'case_key':key,'part':part,'model':copy(e,'declarations'),'texture':icon,'texture_location':loc,'parent':m['parent']})
    if entry+'.mcmeta' in z.namelist():metadata.append({'case_key':key,'source':icon,'metadata':copy(entry+'.mcmeta','animation-declarations')})
   cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
   base={'abhorrent_armor':'AbhorrentArmor','blood_clot_armor':'BloodClotArmor','ferrum_armor':'FerrumArmor','plasma_armor':'PlasmaArmor','skinsuit':'Skinsuit','symbiotic_armor':'SymbioticArmor'}
   paths=[]
   if family in base:
    for part in ['Helmet','Chestplate','Leggings','Boots']:
     a,out=disasm(f'com/curseforge/macabre/item/{base[family]}Item${part}.class')
     method=out.split('public java.lang.String getArmorTexture(',1)[1].split('\n  public ',1)[0]
     vals=re.findall(r'// String (macabre:textures/[^\s]+\.png)',method);assert len(vals)==1
     entry='assets/'+vals[0].replace(':','/',1);assert entry in z.namelist()
     bindings.append({'case_key':key,'part':part.lower(),'kind':'EXACT_ITEM_SUBCLASS_TEXTURE_OVERRIDE','class_source':a,'method_excerpt':method,'declared_texture':vals[0],'archive_entry':entry,'runtime_selected_chain_proven':False})
     if entry not in paths:paths.append(entry)
   else:
    name=family.removesuffix('_armor').capitalize();a,out=disasm(f'com/curseforge/macabre/item/model/{name}ArmorModel.class')
    method=out.split(f'getTextureResource(com.curseforge.macabre.item.{name}ArmorItem);',1)[1].split('\n  public ',1)[0]
    vals=re.findall(r'// String (textures/[^\s]+\.png)',method);assert len(vals)==1
    entry='assets/macabre/'+vals[0];assert entry in z.namelist();paths.append(entry)
    bindings.append({'case_key':key,'kind':'EXACT_GEOMODEL_TEXTURE_DECLARATION','class_source':a,'method_excerpt':method,'declared_texture':'macabre:'+vals[0],'archive_entry':entry,'runtime_selected_chain_proven':False})
    # Copy actual declared geometry and animation for atlas-size context, not a game rendering claim.
    for prefix,folder in [('geo/','geo-declarations'),('animations/','animation-declarations')]:
     val=re.findall(r'// String ('+prefix+r'[^\s]+\.json)',out);assert len(val)==1
     aa=copy('assets/macabre/'+val[0],folder);payload=json.loads((D/aa['local']).read_text())
     aa.update(case_key=key,kind='GEOMETRY_ATLAS_CONTEXT' if prefix=='geo/' else 'DECLARED_ANIMATION_CONTEXT')
     if prefix=='geo/':aa['descriptions']=[g['description'] for g in payload['minecraft:geometry']]
     geometry.append(aa)
   for e in paths:worn.append({**copy(e,'worn-references',True),'case_key':key,'binding_proven':False,'role':'STATIC_DECLARED_TEXTURE_NOT_FINAL_RENDER_OR_TARGET_UV_PROOF'})
 assert not metadata,'Read actual frame metadata separately if present'
 save('provenance.json',{'archives':[{'path':jar,'sha256':sha(Path(jar))}],'cases':cases,'worn_textures':worn,'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
 save('resource-declarations.json',decls);save('animation-candidates.json',metadata);save('static-declarations.json',bindings);save('geometry-animation-context.json',geometry);save('class-provenance.json',{'javap':str(javap.resolve()),'javap_sha256':jhash,'classes':classes})
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'icon_chart_collector':CHART,'candidate_inventory':INV}
 save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':keys})
 spec=importlib.util.spec_from_file_location('chart',CHART);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.main()
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
 for page,start in enumerate(range(0,len(worn),4),1):
  group=worn[start:start+4];heights=[max(130,a['size'][1]*min(3,max(1,512//max(a['size']))))+35 for a in group];out=Image.new('RGB',(1550,55+sum(heights)),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,10),'READ-ONLY STATIC DECLARED SOURCE ATLAS / no final render proof / NOT GAME',font=font,fill='white');y=50
  for a,h in zip(group,heights):
   im=Image.open(D/a['local']).convert('RGBA');s=min(3,max(1,512//max(im.size)));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);dr.text((8,y+5),a['case_key'],font=font,fill='white');dr.text((8,y+27),Path(a['entry']).name,font=font,fill='#b7c0c4');dr.text((8,y+49),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4');out.paste(im,(530,y),im);y+=h
  out.save(D/f'worn-{page:02}.png')
 print(json.dumps({'names':len(cases),'icons':len(decls),'native_layers':len(worn),'static_declarations':len(bindings),'classes':len(classes),'geo_and_animations':len(geometry),'pages':math.ceil(len(cases)/7)+math.ceil(len(worn)/4)}))
if __name__=='__main__':main()
