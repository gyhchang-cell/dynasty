from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;P=D.parent/'armor-travelers-whole-20261114';S=D/'source'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
v=json.load(open(D/'provenance.json'));T={x['path']:x for x in json.load(open(P/'tree-api.json'))['tree'] if x['type']=='blob'}
paths=[]
for slot in ['helmet','chestplate','leggings','boots']:
 for part,mat in [('plating','iron'),('maille','leather')]:paths.append(f'src/generated/resources/assets/tconstruct/textures/item/tool/armor/plate/{slot}/{part}_tconstruct_{mat}.png')
for slot in ['armor','leggings']:
 for part,mat in [('plating','iron'),('maille','leather')]:paths.append(f'src/generated/resources/assets/tconstruct/textures/tinker_armor/plate/{part}_{slot}_tconstruct_{mat}.png')
paths += [f'src/generated/resources/data/tconstruct/tinkering/materials/{kind}/{mat}.json' for kind in ['stats','definition'] for mat in ['iron','leather']]
def f(p):
 out=S/p;out.parent.mkdir(parents=True,exist_ok=True);u=f'https://raw.githubusercontent.com/SlimeKnights/TinkersConstruct/{v["commit"]}/{p}';subprocess.run(['curl','--fail','--silent','--show-error','--max-time','30',u,'-o',str(out)],check=True);b=out.read_bytes();a=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert a==T[p]['sha'];return dict(path=p,url=u,git_blob=a,sha256=h(out))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:v['files']+=list(e.map(f,paths))
save('provenance.json',v)
icons=[S/p for p in paths[:8]];atlases=[S/p for p in paths[8:12]]
index=[]
for p in icons+atlases:
 im=Image.open(p).convert('RGBA');a=list(im.getchannel('A').getdata());index.append({'path':str(p.relative_to(D)),'sha256':h(p),'size':list(im.size),'nonzero_alpha':sum(x>0 for x in a),'alpha_levels':sorted(set(a)),'bbox':list(im.getbbox())})
save('native-png-index.json',index)
def page(ps,name,cols,scale,cw,ch):
 out=Image.new('RGB',(cols*cw,((len(ps)+cols-1)//cols)*ch+35),(75,80,85));dr=ImageDraw.Draw(out);dr.text((8,8),'UPSTREAM NATIVE COMPONENTS / NEAREST / NOT GAME',fill='white')
 for i,p in enumerate(ps):
  x=i%cols*cw;y=i//cols*ch+35;im=Image.open(p).convert('RGBA');q=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out.paste(q,(x+8,y+32),q);dr.text((x+8,y),p.parent.name+'/'+p.stem,fill='white')
 out.save(D/name)
page(icons,'native-icon-parts.png',2,9,490,195);page(atlases,'native-worn-layers.png',1,9,710,325)
out=Image.new('RGB',(1000,290),(75,80,85));dr=ImageDraw.Draw(out);dr.text((8,8),'SOURCE-OVER DIAGNOSTIC / CHOSEN iron + leather / NOT GAME',fill='white')
for i,slot in enumerate(['helmet','chestplate','leggings','boots']):
 im=Image.new('RGBA',(16,16))
 for p in icons[2*i:2*i+2]:im.alpha_composite(Image.open(p).convert('RGBA'))
 q=im.resize((192,192),Image.Resampling.NEAREST);out.paste(q,(i*250+20,60),q);dr.text((i*250+20,35),slot,fill='white')
out.save(D/'source-over-diagnostic.png')
# comparison reopens the exact D78 diagnostic; no additional upstream originals counted.
a=Image.open(P/'source-over-diagnostic.png');b=Image.open(D/'source-over-diagnostic.png');out=Image.new('RGB',(1000,580));out.paste(a,(0,0));out.paste(b,(0,290));out.save(D/'prior-whole-comparison.png')
contextpaths=[P/'source/gradle.properties',P/'source/src/main/java/slimeknights/tconstruct/tools/TinkerTools.java',P/'source/src/main/java/slimeknights/tconstruct/tools/ArmorDefinitions.java',P/'source/src/main/java/slimeknights/tconstruct/tools/data/ArmorModelProvider.java']+list((P/'source/src/main/java/slimeknights/tconstruct/library/client/armor').rglob('*.java'))+[P/'source/src/main/java/slimeknights/tconstruct/library/tools/item/armor/MultilayerArmorItem.java',P/'source/src/main/java/slimeknights/tconstruct/library/client/model/tools/ToolModel.java',P/'source/src/generated/resources/assets/tconstruct/tinkering/materials/leather.json',P/'source/src/generated/resources/assets/tconstruct/tinkering/materials/iron.json']
save('reused-consumer-context.json',{'same_fixed_commit':v['commit'],'new_implementation_credit':0,'inputs':[{'path':str(p),'sha256':h(p)} for p in contextpaths],'prior_visual_comparison':{'path':str(P/'source-over-diagnostic.png'),'sha256':h(P/'source-over-diagnostic.png'),'not_game':True}})
print('new files',len(v['files']),'native_png',len(index))
