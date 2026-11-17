from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,re
D=Path(__file__).resolve().parent;S=D/'source'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
icons=[S/f'src/main/resources/assets/oreganized/textures/item/electrum_{s}.png' for s in ['helmet','chestplate','leggings','boots']];active=[S/'src/main/resources/assets/oreganized/textures/entity/electrum_armor.png'];old=[S/f'src/main/resources/assets/oreganized/textures/models/armor/electrum_layer_{i}.png' for i in [1,2,3]]
rows=[]
for p in icons+active+old:
 im=Image.open(p).convert('RGBA');a=list(im.getchannel('A').getdata());rows.append({'path':str(p),'relative_path':str(p.relative_to(D)),'sha256':h(p),'size':list(im.size),'bbox':list(im.getbbox()),'nonzero_alpha':sum(x>0 for x in a),'alpha_levels':sorted(set(a)),'source_status':'inactive default-path context, not current override texture' if p in old else 'direct source reference'})
save('native-png-index.json',rows)
def page(ps,name,cols,scale,cw,ch):
 out=Image.new('RGB',(cols*cw,((len(ps)+cols-1)//cols)*ch+35),(75,80,85));dr=ImageDraw.Draw(out);dr.text((8,8),'UPSTREAM NATIVE PIXELS / nearest / NOT GAME',fill='white')
 for i,p in enumerate(ps):
  x=i%cols*cw;y=i//cols*ch+35;im=Image.open(p).convert('RGBA');q=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out.paste(q,(x+8,y+30),q);dr.text((x+8,y),p.stem,fill='white')
 out.save(D/name)
page(icons,'native-icons.png',4,10,235,210);page(active,'active-native-atlas.png',1,10,690,690);page(old,'inactive-default-path-context.png',1,8,690,570)
source=(S/'src/main/java/galena/oreganized/client/model/ElectrumArmorModel.java').read_text();matches=re.findall(r'texOffs\((\d+), (\d+)\)\.addBox\(([^)]*)\)',source);boxes=[]
for u,v,args in matches:
 vals=[float(x.strip().removesuffix('F')) for x in args.split(',')[:6]];boxes.append({'texOffs':[int(u),int(v)],'origin':vals[:3],'size':vals[3:],'nominal_plane':0 in vals[3:]})
assert len(boxes)==13
save('declared-uv-boxes.json',{'source':str(S/'src/main/java/galena/oreganized/client/model/ElectrumArmorModel.java'),'sha256':h(S/'src/main/java/galena/oreganized/client/model/ElectrumArmorModel.java'),'texture_size':[64,64],'boxes':boxes,'zero_width_planes':sum(b['nominal_plane'] for b in boxes),'not_face_orientation_or_render_validation':True})
save('original-image-paths.json',{'active_source_png':[r for r in rows if r['source_status']=='direct source reference'],'inactive_context_png':[r for r in rows if r['source_status']!='direct source reference'],'new_design_credit':0})
(D/'original-image-paths.txt').write_text('\n'.join(str(p) for p in icons+active)+'\n\nInactive default-path context (not current override):\n'+'\n'.join(str(p) for p in old)+'\n')
print([(Path(x['path']).name,x['size']) for x in rows])
