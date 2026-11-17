"""D26 freeze six unread eastern ceremonial/scout sets; exact native sources, no production."""
from pathlib import Path
from io import BytesIO
import json,hashlib,zipfile,subprocess,sys,shutil,importlib.util,re,math
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2]
PRIOR=R/'docs/art/armor-eastern-workwear-reference-20261104/combined-semantic-ledger.json'
INV=R/'docs/art/armor-additional-design-reference-20261104/candidate-archive-scan.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
FAMILIES='blk fxt hlp lb qn yangjian'.split()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def draw_icons():
 p=json.loads((D/'provenance.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
 # Whole native source PNGs at scale1. No reduction, cropping or asset modification.
 for i,case in enumerate(p['cases'],1):
  images=[Image.open(D/a['local']).convert('RGBA') for a in case['icons']];cw=max(180,max(im.width for im in images)+20);ch=max(im.height for im in images)+95
  out=Image.new('RGB',(cw*4,75+ch),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'READ-ONLY NATIVE REFERENCE / NOT DYNASTY ART / NOT GAME / '+case['case_key'],font=font,fill='white')
  for j,(im,a) in enumerate(zip(images,case['icons'])):
   x=j*cw;out.paste(im,(x+10,65),im);dr.text((x+10,65+ch-80),['helmet','chestplate','leggings','boots'][j]+' '+str(a['size']),font=font,fill='white');dr.text((x+10,65+ch-55),a['sha256'][:12],font=font,fill='#b7c0c4')
  out.save(D/f'icons-{i:02}.png')
def main():
 assert not (D/'provenance.json').exists()
 src=next(a for a in json.loads(INV.read_text())['archives'] if 'jinghui-1.9.6' in a['jar']);jar=src['jar'];keys=['jinghui:'+f for f in FAMILIES];prior=json.loads(PRIOR.read_text());assert not set(keys)&set(prior['reviewed_case_keys'])
 targets=json.loads(next((R/'docs/art/armor-survival-complete-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
 subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D26复用623已读名称/212保守学习组及D24/D25对应证据，实际读取6未读白龙/凤兮/黑龙袍/无双/潜匿/清源四槽原图及专用GeoModel、item/renderer绑定，核实完整结构与材料身份；源图高分辨率如实保留，只作参考，不以高分辨率渲染图冒充MC像素成稿。专用UV不套普通甲，战损/换色/部件不算独立信用，1000完整有效独立设计未达前不制作；保护精致认可旧稿与289路径、共享Jar/实例/声光，不开游戏，不重跑旧批次验收。'],check=True,capture_output=True)
 save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
 cases=[];decls=[];worn=[];meta=[];classes=[];bindings=[];geometry=[];javap=Path(shutil.which('javap')).resolve()
 with zipfile.ZipFile(jar) as z:
  def copy(e,folder,png=False):
   b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path(folder)/f'{h[:12]}-{Path(e).name}';(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);a={'jar':jar,'entry':e,'sha256':h,'local':str(loc)}
   if png:a['size']=list(Image.open(BytesIO(b)).size)
   return a
  lang=copy('assets/jinghui/lang/zh_cn.json','language-declaration');labels=json.loads((D/lang['local']).read_text())
  for f in FAMILIES:
   key='jinghui:'+f;icons=[]
   for part in ['helmet','chestplate','leggings','boots']:
    e=f'assets/jinghui/models/item/{f}_{part}.json';m=json.loads(z.read(e));loc=m['textures']['layer0'];ns,t=loc.split(':');entry=f'assets/{ns}/textures/{t}.png';icon=copy(entry,'references',True);assert min(icon['size'])>0;icons.append(icon);decls.append({'case_key':key,'part':part,'model':copy(e,'declarations'),'texture':icon,'texture_location':loc,'parent':m['parent'],'label':labels[f'item.jinghui.{f}_{part}']})
    if entry+'.mcmeta' in z.namelist():meta.append({'case_key':key,'source':icon,'metadata':copy(entry+'.mcmeta','animation-declarations')})
   cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
   name=f[0].upper()+f[1:];a=copy(f'net/mcreator/jinghui/item/model/{name}Model.class','classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/a['local'])],text=True);loc=Path('disassembly')/(name+'Model.class.txt');(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=str(loc),disassembly_sha256=sha(D/loc));classes.append(a)
   method=out.split(f'getTextureResource(net.mcreator.jinghui.item.{name}Item);',1)[1].split('\n  public ',1)[0];vals=re.findall(r'// String (textures/[^\s]+\.png)',method);assert len(vals)==1
   entry='assets/jinghui/'+vals[0];assert entry in z.namelist()
   bindings.append({'case_key':key,'kind':'EXACT_GEOMODEL_TEXTURE_DECLARATION','class_source':a,'method_excerpt':method,'declared_texture':'jinghui:'+vals[0],'archive_entry':entry,'runtime_selected_chain_proven':False})
   worn.append({**copy(entry,'worn-references',True),'case_key':key,'binding_proven':False,'role':'STATIC_GEOMODEL_DECLARATION_NOT_FINAL_RENDER_OR_TARGET_UV_PROOF'})
   for prefix,folder in [('geo/','geo-declarations'),('animations/','animation-declarations')]:
    vals=re.findall(r'// String ('+prefix+r'[^\s]+\.json)',out);assert len(vals)==1;aa=copy('assets/jinghui/'+vals[0],folder);payload=json.loads((D/aa['local']).read_text());aa.update(case_key=key,kind='GEOMETRY_ATLAS_CONTEXT' if prefix=='geo/' else 'DECLARED_ANIMATION_CONTEXT')
    if prefix=='geo/':aa['descriptions']=[g['description'] for g in payload['minecraft:geometry']]
    geometry.append(aa)
  for e in z.namelist():
   bases=[f[0].upper()+f[1:] for f in FAMILIES]
   include=e=='net/mcreator/jinghui/init/JinghuiModItems.class' or any(e==f'net/mcreator/jinghui/client/renderer/{n}ArmorRenderer.class' or re.fullmatch(r'net/mcreator/jinghui/item/'+n+r'Item(?:\$\d+)?\.class',e) for n in bases)
   if not include:continue
   aa=copy(e,'classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/aa['local'])],text=True);loc=Path('disassembly')/(Path(e).name+'.txt');(D/loc).write_text(out);aa.update(disassembly=str(loc),disassembly_sha256=sha(D/loc),role='ITEM_RENDERER_REGISTRY_CONTEXT_NOT_EXECUTED');classes.append(aa)
 save('provenance.json',{'archives':[{'path':jar,'sha256':sha(Path(jar))}],'cases':cases,'worn_textures':worn,'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
 save('resource-declarations.json',decls);save('animation-candidates.json',meta);save('static-declarations.json',bindings);save('geometry-animation-context.json',geometry);save('class-provenance.json',{'javap':str(javap),'javap_sha256':sha(javap),'classes':classes});save('language-provenance.json',lang)
 paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'candidate_inventory':INV,'icon_chart_collector':CHART}
 save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':keys,'skipped_large_render_icon_names':[k for k in src['families'] if k not in keys]})
 assert not meta,'Read animation frames separately if present'
 draw_icons()
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
 # Two full source atlases per page to make each pixel visible without thumbnail reduction.
 for page,start in enumerate(range(0,len(worn),2),1):
  group=worn[start:start+2];scales=[min(3,max(1,640//max(a['size']))) for a in group];heights=[max(150,a['size'][1]*s)+40 for a,s in zip(group,scales)];width=max(1500,530+max(a['size'][0]*s for a,s in zip(group,scales))+20);out=Image.new('RGB',(width,55+sum(heights)),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,10),'READ-ONLY STATIC DECLARED SOURCE ATLAS / no actual player render proof / NOT GAME',font=font,fill='white');y=50
  for a,h,s in zip(group,heights,scales):
   im=Image.open(D/a['local']).convert('RGBA');im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);dr.text((8,y+5),a['case_key'],font=font,fill='white');dr.text((8,y+27),Path(a['entry']).name,font=font,fill='#b7c0c4');dr.text((8,y+49),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4');out.paste(im,(530,y),im);y+=h
  out.save(D/f'worn-{page:02}.png')
 print(json.dumps({'names':len(cases),'icons':len(decls),'native_atlases':len(worn),'static_declarations':len(bindings),'classes':len(classes),'geo_and_animations':len(geometry),'pages':len(cases)+math.ceil(len(worn)/2)}))
if __name__=='__main__':main()
