from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent;S=D/'source'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
icon=[]
for s in ['goggles','vest','pants','boots']:
 if s=='goggles':icon.append(S/f'src/main/resources/assets/tconstruct/textures/item/tool/armor/travelers/{s}/base.png')
 for part,mat in [('cuirass','leather'),('metal','rose_gold')]:icon.append(S/f'src/generated/resources/assets/tconstruct/textures/item/tool/armor/travelers/{s}/{part}_tconstruct_{mat}.png')
atlas=[S/'src/main/resources/assets/tconstruct/textures/tinker_armor/travelers/base_armor.png']
atlas += [S/f'src/generated/resources/assets/tconstruct/textures/tinker_armor/travelers/{p}_{slot}_tconstruct_{mat}.png' for slot in ['armor','leggings'] for p,mat in [('cuirass','leather'),('metal','rose_gold')]]
rows=[]
for p in icon+atlas:
 im=Image.open(p).convert('RGBA');rows.append({'path':str(p.relative_to(D)),'sha256':h(p),'size':list(im.size),'nonzero_alpha':sum(a>0 for a in im.getchannel('A').getdata()),'alpha_levels':sorted(set(im.getchannel('A').getdata()))})
save('native-png-index.json',rows)
def sheet(ps,name,cols,scale,cellw,cellh):
 out=Image.new('RGB',(cols*cellw,((len(ps)+cols-1)//cols)*cellh+35),(75,80,85));draw=ImageDraw.Draw(out);draw.text((8,8),'UPSTREAM NATIVE PIXELS / nearest enlargement / NOT GAME',fill='white')
 for i,p in enumerate(ps):
  x=i%cols*cellw;y=i//cols*cellh+35;im=Image.open(p).convert('RGBA');out.paste(im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST),(x+8,y+35),im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST));draw.text((x+8,y),p.stem[:60],fill='white')
 out.save(D/name)
sheet(icon,'native-icon-parts.png',3,7,380,170)
sheet(atlas,'native-worn-layers.png',1,9,690,325)
# Diagnostic source-over only. Does not emulate tint, item loader, cutout, depth or GPU rendering.
out=Image.new('RGB',(1000,290),(75,80,85));dr=ImageDraw.Draw(out);dr.text((8,8),'SOURCE-OVER DIAGNOSTIC / DEFAULT rose_gold + leather / NOT GAME',fill='white')
for n,s in enumerate(['goggles','vest','pants','boots']):
 ps=[p for p in icon if '/'+s+'/' in str(p)];im=Image.new('RGBA',(16,16))
 for p in ps:im.alpha_composite(Image.open(p).convert('RGBA'))
 out.paste(im.resize((192,192),Image.Resampling.NEAREST),(n*250+20,60),im.resize((192,192),Image.Resampling.NEAREST));dr.text((n*250+20,35),s,fill='white')
out.save(D/'source-over-diagnostic.png')
save('sheet-generation.json',{'native_files':len(rows),'pages':['native-icon-parts.png','native-worn-layers.png','source-over-diagnostic.png'],'diagnostic_not_runtime':True,'source_originals_modified':False})
print('native files',len(rows))
