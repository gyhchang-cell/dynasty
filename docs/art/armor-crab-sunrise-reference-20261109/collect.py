"""D29: static original-source study, not production or game QA."""
from pathlib import Path
from io import BytesIO
import json,hashlib,zipfile,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent; R=D.parents[2]
PRIOR=R/'docs/art/armor-rpg-robe-reference-20261104'
JAR=Path('/Users/a15356015027/Public/.minecraft/versions/神话：起源/mods/Mokels RPG 2 3.1.jar')
JAVAP=Path('/Users/a15356015027/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/javap')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 targets=json.loads(next(PRIOR.glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D29遵守用户粗像素/原版盔甲比例/原稿不缩16要求。先实际查两套候选原图、geo、穿戴材质和声明；候选别名不加参考信用。保留认可稿及289保护路径；只在研究目录写入，不开游戏、不碰实例、共享Jar、声光或主清单。1000有效相关独立完整设计门槛未达，不制作。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 records=[];models=[];classes=[]
 with zipfile.ZipFile(JAR) as z:
  def cp(e,folder):
   b=z.read(e);h=hashlib.sha256(b).hexdigest();local=str(Path(folder)/(h[:12]+'-'+Path(e).name));(D/local).parent.mkdir(parents=True,exist_ok=True);(D/local).write_bytes(b);a={'entry':e,'local':local,'sha256':h}
   if e.endswith('.png'):a['size']=list(Image.open(BytesIO(b)).size)
   records.append(a);return a
  for family in ['crabarmor','sunrise_armor']:
   for part in ['helmet','chestplate','leggings','boots']:
    e=f'assets/mokels_rpg_two/models/item/{family}_{part}.json';m=json.loads(z.read(e));ns,t=m['textures']['layer0'].split(':');models.append({'case_key':'mokels_rpg_two:'+family,'part':part,'model':cp(e,'models'),'icon':cp(f'assets/{ns}/textures/{t}.png','icons'),'texture_location':m['textures']['layer0']})
  for e in z.namelist():
   if e.endswith('.class') and (any(k in e for k in ['CrabarmorItem','SunriseArmorItem','CrabarmorModel','SunriseArmorModel','CrabarmorArmorRenderer','SunriseArmorArmorRenderer']) or e=='net/mcreator/mokelsrpgtwo/init/MokelsRpgTwoModItems.class'):
    a=cp(e,'classes');out=subprocess.check_output([str(JAVAP),'-c','-p',str(D/a['local'])],text=True);loc='disassembly/'+Path(e).name+'.txt';(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=loc,disassembly_sha256=sha(D/loc));classes.append(a)
  resource_entries=set()
  import re
  for a in classes:
   if 'Model.class' in a['entry']:
    for s in re.findall(r'// String ([^\n]+)',(D/a['disassembly']).read_text()):
     if s.endswith(('.png','.geo.json','.animation.json')):resource_entries.add('assets/mokels_rpg_two/'+s)
  for e in sorted(resource_entries):cp(e,'atlases' if e.endswith('.png') else 'geometry')
  for lang in ['en_us','zh_cn']:
   e=f'assets/mokels_rpg_two/lang/{lang}.json'
   if e in z.namelist():cp(e,'context')
 save('declarations.json',models)
 save('provenance.json',{'archive':{'path':str(JAR),'sha256':sha(JAR)},'records':records,'classes':classes,'javap':str(JAVAP),'javap_sha256':sha(JAVAP),'prior_ledger':str((PRIOR/'combined-semantic-ledger.json').relative_to(R)),'prior_ledger_sha256':sha(PRIOR/'combined-semantic-ledger.json'),'game_starts':0,'production_changes':0})
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
 for i,f in enumerate(['crabarmor','sunrise_armor'],1):
  out=Image.new('RGB',(900,220),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE SOURCE ONLY / NOT DYNASTY / NOT GAME / '+f,font=font,fill='white')
  for n,m in enumerate(x for x in models if x['case_key'].endswith(':'+f)):
   im=Image.open(D/m['icon']['local']).convert('RGBA');s=max(1,min(4,128//max(im.size)));out.paste(im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST),(n*225+15,45),im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST));dr.text((n*225+15,180),m['part']+' '+str(im.size),font=font,fill='white')
  out.save(D/f'icons-{i:02}.png')
 for i,a in enumerate(x for x in records if x['local'].startswith('atlases/')):
  im=Image.open(D/a['local']).convert('RGBA');s=max(1,min(4,512//max(im.size)));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);out=Image.new('RGB',(max(900,im.width+30),im.height+85),(68,73,78));out.paste(im,(15,75),im);dr=ImageDraw.Draw(out);dr.text((8,8),'READ ONLY NATIVE ATLAS / NOT GAME',font=font,fill='white');dr.text((8,35),a['entry'],font=font,fill='white');out.save(D/f'atlas-{i+1:02}.png')
 print(json.dumps({'icons':len(models),'classes':len(classes),'resources':sorted(resource_entries),'all_source_records':len(records)}))
if __name__=='__main__':main()
