"""D27 freeze exact unread source designs; static disassembly, never class execution."""
from pathlib import Path
from io import BytesIO
import json,hashlib,zipfile,subprocess,sys,shutil,re
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2]
PRIOR=R/'docs/art/armor-eastern-ceremonial-reference-20261104/combined-semantic-ledger.json'
INV=R/'docs/art/armor-additional-design-reference-20261104/candidate-archive-scan.json'
FAMILIES=['dark_wukong','ghost_wukong','iron_wukong','wukong']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'provenance.json').exists()
 prior=json.loads(PRIOR.read_text());assert not {'sw_wukong:'+f for f in FAMILIES}&set(prior['reviewed_case_keys'])
 src=next(a for a in json.loads(INV.read_text())['archives'] if '[forge]wukong' in a['jar']);jar=src['jar'];javap=Path(shutil.which('javap')).resolve()
 targets=json.loads(next((R/'docs/art/armor-eastern-ceremonial-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D27沿D26已有629名称/212学习组断点；读取悟空系列四套此前未读原图与客户端/模型绑定，识别共享护腿靴及同设计换色；不以文件/组件/换色/名称计独立设计，参考门槛未达不制作。原图不缩16px不量化，保护认可精致旧稿、289路径、实例及共享Jar。不启声光、不启动游戏。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[];decls=[];worn=[];classes=[];langs=[]
 with zipfile.ZipFile(jar) as z:
  def copy(e,folder,png=False):
   data=z.read(e);h=hashlib.sha256(data).hexdigest();loc=Path(folder)/(h[:12]+'-'+Path(e).name);(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(data);a={'jar':jar,'entry':e,'local':str(loc),'sha256':h}
   if png:a['size']=list(Image.open(BytesIO(data)).size)
   return a
  for lang in ['zh_cn','en_us']:
   e=f'assets/sw_wukong/lang/{lang}.json'
   if e in z.namelist():langs.append(copy(e,'languages'))
  labels={k:v for x in langs for k,v in json.loads((D/x['local']).read_text()).items()}
  for f in FAMILIES:
   key='sw_wukong:'+f;icons=[]
   for part in ['helmet','chestplate','leggings','boots']:
    e=f'assets/sw_wukong/models/item/{f}_{part}.json';m=json.loads(z.read(e));n,t=m['textures']['layer0'].split(':');icon=copy(f'assets/{n}/textures/{t}.png','icons',True);icons.append(icon)
    decls.append({'case_key':key,'part':part,'model':copy(e,'models'),'icon':icon,'texture_location':m['textures']['layer0'],'label':labels.get(f'item.sw_wukong.{f}_{part}'),'parent':m['parent']})
   cases.append({'case_key':key,'icons':icons})
  for e in z.namelist():
   if e.startswith('assets/sw_wukong/textures/entities/') or e.startswith('assets/sw_wukong/textures/models/armor/'):
    if e.endswith('.png'):worn.append(copy(e,'atlases',True))
   if not e.endswith('.class'):continue
   include=e.startswith('net/mcreator/wukong/client/model/Modelwukong_reworked') or e=='net/mcreator/wukong/init/SwWukongModItems.class' or re.fullmatch(r'net/mcreator/wukong/item/(?:DarkWukong|GhostWukong|IronWukong|Wukong)Item(?:\$[^/]+)?\.class',e)
   if include:
    a=copy(e,'classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/a['local'])],text=True);loc=Path('disassembly')/(Path(e).name+'.txt');(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=str(loc),disassembly_sha256=sha(D/loc));classes.append(a)
 save('provenance.json',{'archives':[{'path':jar,'sha256':sha(Path(jar))}],'cases':cases,'native_atlases':worn,'classes':classes,'languages':langs,'javap':str(javap),'javap_sha256':sha(javap),'new_artwork':0,'game_starts':0})
 save('declarations.json',decls)
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'candidate_inventory':INV,'prior_progress':PRIOR.parent/'progress.json','prior_verification':PRIOR.parent/'verification.json'}
 save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()})
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
 for i,c in enumerate(cases,1):
  ims=[Image.open(D/a['local']).convert('RGBA') for a in c['icons']];scale=4 if max(max(im.size) for im in ims)<=64 else 1;cw=max(230,max(im.width*scale for im in ims)+20);height=max(im.height*scale for im in ims)+140;out=Image.new('RGB',(cw*4,height),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE READ-ONLY REFERENCE / NOT DYNASTY / NOT GAME / '+c['case_key'],font=font,fill='white')
  for j,(im,a,part) in enumerate(zip(ims,c['icons'],['helmet','chestplate','leggings','boots'])):
   im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out.paste(im,(j*cw+10,50),im);dr.text((j*cw+10,height-65),part+' '+str(a['size']),font=font,fill='white');dr.text((j*cw+10,height-43),a['sha256'][:12],font=font,fill='white')
  out.save(D/f'icons-{i:02}.png')
 for i,a in enumerate(worn,1):
  im=Image.open(D/a['local']).convert('RGBA');s=4 if max(im.size)<=128 else 1;im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);out=Image.new('RGB',(max(900,im.width+30),im.height+90),(68,73,78));out.paste(im,(15,70),im);dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE SOURCE ATLAS / NO RUNTIME OR MODEL VISIBILITY PROOF',font=font,fill='white');dr.text((8,35),a['entry']+' '+str(a['size']),font=font,fill='white');out.save(D/f'atlas-{i:02}.png')
 print(json.dumps({'names':len(cases),'icons':len(decls),'native_atlases':len(worn),'classes':len(classes),'analysis_pages':len(cases)+len(worn),'game_starts':0}))
if __name__=='__main__':main()
