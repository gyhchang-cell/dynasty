"""D28 unread alternative-named robe sets; original bytes and no production mutation."""
from pathlib import Path
from io import BytesIO
import json,hashlib,subprocess,zipfile,sys,shutil,re
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2];PRIOR=R/'docs/art/armor-simian-kit-reference-20261104/combined-semantic-ledger.json'
FAMILIES=['arcane_robe','fire_robe','frost_robe','netherite_arcane_robe','netherite_fire_robe','netherite_frost_robe','wizard_robe']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 for f,n in [('dynasty-armor-alternate-slot-candidates-20261104.json','alternate-name-candidates.json'),('dynasty-armor-latest-standard-candidates-20261104.json','standard-name-candidates.json')]:
  a=json.loads((Path('/tmp')/f).read_text());assert a['reference_credit']==0;save(n,a)
 candidates=json.loads((D/'alternate-name-candidates.json').read_text())['candidates'];first=next(c for c in candidates if c['case_key']=='wizards:arcane_robe');jar=first['jar'];prior=json.loads(PRIOR.read_text());assert not {'wizards:'+f for f in FAMILIES}&set(prior['reviewed_case_keys'])
 targets=json.loads(next((R/'docs/art/armor-simian-kit-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D28复用D27累计633已读名称/213学习组，实际阅读7个此前未读的head/chest/legs/feet法袍套装；本地3069文件名去重Jar候选扫描零设计信用。先核整套造型、像素材质和声明绑定，同模升级/换色不重复计数。1000有效独立完整参考未达不制作；原图不缩16、不量化，保护认可精致旧稿、289路径、用户实例、声光及共享Jar。仅静态研究，Fabric/AzureLib来源不是Dynasty Forge可直接接入资源。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[];decl=[];atlases=[];classes=[];geo=[];context=[];javap=Path(shutil.which('javap')).resolve()
 with zipfile.ZipFile(jar) as z:
  def copy(e,folder,png=False):
   b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path(folder)/(h[:12]+'-'+Path(e).name);(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);a={'jar':jar,'entry':e,'sha256':h,'local':str(loc)}
   if png:a['size']=list(Image.open(BytesIO(b)).size)
   return a
  for lang in ['en_us','zh_cn']:
   e=f'assets/wizards/lang/{lang}.json'
   if e in z.namelist():context.append(copy(e,'context'))
  context.append(copy('fabric.mod.json','context'))
  for f in FAMILIES:
   icons=[]
   for part in ['head','chest','legs','feet']:
    e=f'assets/wizards/models/item/{f}_{part}.json';m=json.loads(z.read(e));ns,t=m['textures']['layer0'].split(':');a=copy(f'assets/{ns}/textures/{t}.png','icons',True);icons.append(a);decl.append({'case_key':'wizards:'+f,'part':part,'model':copy(e,'models'),'icon':a,'texture_location':m['textures']['layer0'],'parent':m['parent']})
   cases.append({'case_key':'wizards:'+f,'icons':icons})
   atlases.append({**copy(f'assets/wizards/textures/armor/{f}.png','atlases',True),'case_key':'wizards:'+f,'role':'CANDIDATE_UNTIL_STATIC_RESOURCE_DECLARATION_CHECKED'})
  for e in ['assets/wizards/geo/wizard_robes.geo.json','assets/wizards/animations/armor_idle.json']:geo.append(copy(e,'geometry'))
  for e in z.namelist():
   if not e.endswith('.class'):continue
   if not (e.startswith('net/wizards/client/armor/') or e in ['net/wizards/item/Armors.class','net/wizards/item/WizardArmor.class','net/wizards/item/WizardArmor$1.class','net/wizards/item/WizardItems.class','net/wizards/fabric/client/FabricClientMod.class']):continue
   a=copy(e,'classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/a['local'])],text=True);loc=Path('disassembly')/(Path(e).name+'.txt');(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=str(loc),disassembly_sha256=sha(D/loc));classes.append(a)
 save('provenance.json',{'archives':[{'path':jar,'sha256':sha(Path(jar))}],'cases':cases,'native_atlases':atlases,'classes':classes,'geometry_context':geo,'other_context':context,'javap':str(javap),'javap_sha256':sha(javap),'game_starts':0,'production_changes':0})
 save('declarations.json',decl)
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'prior_progress':PRIOR.parent/'progress.json','prior_verification':PRIOR.parent/'verification.json'};save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'candidate_scan_reference_credit':0})
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
 for i,c in enumerate(cases,1):
  ims=[Image.open(D/a['local']).convert('RGBA') for a in c['icons']];s=4 if max(max(im.size) for im in ims)<=64 else 1;cw=max(210,max(im.width*s for im in ims)+20);h=max(im.height*s for im in ims)+115;out=Image.new('RGB',(cw*4,h),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE READ-ONLY REFERENCES / NOT DYNASTY / NOT GAME / '+c['case_key'],font=font,fill='white')
  for j,(im,a,part) in enumerate(zip(ims,c['icons'],['head','chest','legs','feet'])):
   im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);out.paste(im,(j*cw+10,45),im);dr.text((j*cw+10,h-55),part+' '+str(a['size']),font=font,fill='white');dr.text((j*cw+10,h-32),a['sha256'][:12],font=font,fill='white')
  out.save(D/f'icons-{i:02}.png')
 for i,a in enumerate(atlases,1):
  im=Image.open(D/a['local']).convert('RGBA');s=4 if max(im.size)<=128 else 1;im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);out=Image.new('RGB',(max(950,im.width+30),im.height+90),(68,73,78));out.paste(im,(15,70),im);dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE ATLAS / STATIC SOURCE / NOT GAME / '+a['case_key'],font=font,fill='white');dr.text((8,35),a['entry']+' '+str(a['size']),font=font,fill='white');out.save(D/f'atlas-{i:02}.png')
 print(json.dumps({'names':len(cases),'icons':len(decl),'atlases':len(atlases),'classes':len(classes),'geo_animation_context':len(geo),'analysis_pages':len(cases)+len(atlases),'source_platform':'Fabric/AzureLib, visual reference only'}))
if __name__=='__main__':main()
