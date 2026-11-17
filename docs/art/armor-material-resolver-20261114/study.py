from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent;P=D.parent/'armor-plate-whole-20261114';S=D/'source';V=D.parent/'armor-travelers-whole-20261114'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
icons=[S/f'src/main/resources/assets/tconstruct/textures/item/tool/armor/plate/{slot}/{part}.png' for slot in ['helmet','chestplate','leggings','boots'] for part in ['plating','maille']];atlas=[S/f'src/main/resources/assets/tconstruct/textures/tinker_armor/plate/{part}_{slot}.png' for slot in ['armor','leggings'] for part in ['plating','maille']]
rows=[]
for p in icons+atlas:
 im=Image.open(p).convert('RGBA');mat='iron' if p.stem.startswith('plating') else 'leather';rel=str(p.relative_to(S)).replace('src/main/resources/','src/generated/resources/');q=P/'source'/rel;q=q.with_name(q.stem+'_tconstruct_'+mat+'.png');native=Image.open(q).convert('RGBA');assert im.size==native.size
 rows.append({'path':str(p),'sha256':h(p),'size':list(im.size),'specialized_path':str(q),'specialized_sha256':h(q),'alpha_identical_to_D79_specialized':im.getchannel('A').tobytes()==native.getchannel('A').tobytes(),'rgba_identical':im.tobytes()==native.tobytes(),'is_design_count_test':False})
save('base-texture-qualification.json',{'base_files':rows,'source_existence_verified':True,'resource_validator_runtime_executed':False,'loaded_pack_override_order_unverified':True,'new_design_credit':0})
def page(ps,name,cols,scale,cw,ch):
 out=Image.new('RGB',(cols*cw,((len(ps)+cols-1)//cols)*ch+35),(75,80,85));dr=ImageDraw.Draw(out);dr.text((8,8),'UPSTREAM BASE TEXTURES / NEAREST / NOT GAME',fill='white')
 for i,p in enumerate(ps):
  x=i%cols*cw;y=i//cols*ch+35;im=Image.open(p).convert('RGBA');q=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out.paste(q,(x+8,y+30),q);dr.text((x+8,y),p.parent.name+'/'+p.stem,fill='white')
 out.save(D/name)
page(icons,'native-item-bases.png',2,9,340,190);page(atlas,'native-worn-bases.png',1,8,690,300)
save('original-image-paths.json',{'base_png_paths':rows,'these_are_template_bases_not_12_new_designs':True,'view_pages':['native-item-bases.png','native-worn-bases.png']})
print('base PNG12',[(Path(r['path']).name,r['alpha_identical_to_D79_specialized']) for r in rows])
