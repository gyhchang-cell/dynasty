from pathlib import Path
import sys,json
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent));from inspect_reference import sha,save
r=Path.cwd();b=r/'docs/art/armor-goat-fur-whole-20261112';src=b/'source/src/main/resources/assets/cold_sweat/textures/models/armor'
# Explicit correspondence transcribed from ten actually read addBox declarations.
rows=[('cap','head',1,[16,80],[8,8,8],[-4,-6.5,-7],[0,-1.5,3],False,.8),('chest','body',1,[0,64],[8,12,4],[-4,-24,-2],[0,24,0],False,.8),('fluff','body',1,[24,64],[10,6,10],[-5,-2,-5],[0,1,0],False,.8),('right_sleeve','right_arm',1,[0,80],[4,12,4],[-7.75,-23.75,-2],[4.5,22,0],False,[.8,1.2,.8]),('left_sleeve','left_arm',1,[0,80],[4,12,4],[8.75,-23.75,-2],[-9.5,22,0],True,[.8,1.2,.8]),('waist_armor','body',2,[16,112],[8,12,4],[-4,-24,-2],[0,23.75,0],False,.6),('right_legging','right_leg',2,[0,112],[4,12,4],[-2,0,-2],[-.1,0,0],False,.6),('left_legging','left_leg',2,[0,112],[4,12,4],[-2,0,-2],[.1,0,0],True,.6),('right_boot','right_leg',1,[48,80],[4,12,4],[-2,0,-2],[-.25,-.5,0],False,.8),('left_boot','left_leg',1,[48,80],[4,12,4],[-2,0,-2],[.25,-.5,0],True,.8)]
records=[];nets=[]
for name,parent,layer,uv,size,origin,pivot,mirror,inflation in rows:
 u,v=uv;w,h,d=size;rects=[[u+d,v,u+d+w,v+d],[u+d+w,v,u+d+2*w,v+d],[u,v+d,u+d,v+d+h],[u+d,v+d,u+d+w,v+d+h],[u+d+w,v+d,u+2*d+w,v+d+h],[u+2*d+w,v+d,u+2*d+2*w,v+d+h]]
 assert all(0<=x<=64 and 0<=y<=128 for x,y in [(z[0],z[1])for z in rects]+[(z[2],z[3])for z in rects]);rec=dict(name=name,parent=parent,layer=layer,uv=uv,size=size,origin=origin,local_pivot=pivot,builder_mirror_before_addBox=mirror,inflation=inflation,raw_rectangles=rects);records.append(rec)
 if not any(n['layer']==layer and n['uv']==uv and n['size']==size for n in nets):nets.append(rec)
for layer in [1,2]:
 im=Image.open(src/f'goat_fur_layer_{layer}.png').convert('RGBA');selected=[n for n in nets if n['layer']==layer];out=Image.new('RGB',(1000,len(selected)*125),(81,87,91));draw=ImageDraw.Draw(out)
 for j,n in enumerate(selected):
  draw.text((5,j*125+3),n['name']+' UV'+str(n['uv']),fill='white')
  for k,rect in enumerate(n['raw_rectangles']):
   c=im.crop(rect);c=c.resize((c.width*6,c.height*6),Image.Resampling.NEAREST);out.paste(c,(140+k*140,j*125+28),c);draw.text((140+k*140,j*125+8),str(rect),fill='white')
 out.save(b/f'goat-layer-{layer}-raw-nets.png')
save(b/'source-uv-correspondence.json',{'custom_boxes':records,'custom_box_count':10,'unique_raw_nets':len(nets),'raw_faces':60,'inherited_standard_base_cubes':7,'base_mesh_argument_y_offset':1.0,'baked_mirror_orientation_accepted':False,'final_pose_or_wearing_accepted':False})
context=['docs/art/armor-mortem-whole-20261112/context/HumanoidArmorLayer.java','docs/art/armor-robe-main-layer-20261111/source/net/minecraftforge/client/ForgeHooksClient.java','docs/art/armor-robe-main-layer-20261111/source/net/minecraftforge/client/extensions/common/IClientItemExtensions.java','docs/art/armor-iridium-whole-20261112/context/net/minecraft/client/model/HumanoidModel.java'];notes=[]
for s in context:
 p=r/s;target=b/'context'/p.name;target.parent.mkdir(exist_ok=True);target.write_bytes(p.read_bytes());notes.append({'existing_source':str(p),'copy':str(target),'sha256':sha(p)})
save(b/'context/provenance.json',{'files':notes,'scope':'saved Forge1.20.1 patched context, not exact loaded ColdSweat dependencies','bounded_read':{'HumanoidArmorLayer.java':'complete','ForgeHooksClient.java':'325-343','IClientItemExtensions.java':'98-139','HumanoidModel.java':'36-80'}})
