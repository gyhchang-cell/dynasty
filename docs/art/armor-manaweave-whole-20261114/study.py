from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math
D=Path(__file__).resolve().parent;P=D.parent/'armor-botania-reference-20261111';R=D.parents[2];S=P/'source';T=S/'Xplat/src/main/resources/assets/botania/textures'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Exact source nominal cube and PartPose declarations; radians stored, no pose rasterization.
rows=[]
def add(slot,name,parent,uv,origin,size,mirror=False,offset=[0,0,0],rotation=[0,0,0],deform=.01):
 rows.append(dict(slot=slot,part=name,parent=parent,uv=uv,nominal_origin=origin,nominal_size=size,mirror=mirror,local_offset=offset,local_rotation_radians=rotation,deformation=deform))
add('HEAD','head',None,[0,0],[-1,-2,0],[2,2,2]);add('HEAD','helm','head',[0,0],[-4.5,-9.5,-4],[9,11,10],rotation=[math.pi/18,0,0])
add('CHEST','body',None,[0,0],[-1,0,-1],[2,2,2]);add('CHEST','body_top','body',[0,21],[-4.5,-.5,-3],[9,7,6],deform=0);add('CHEST','body_bottom','body_top',[0,34],[-4.5,6.5,-2.5],[9,5,5])
for side,sgn in [('left',1),('right',-1)]:
 root=side+'_arm';main=side+'_arm_main';pauldron=side+'_arm_pauldron'
 add('CHEST',root,None,[0,0],[0 if side=='left' else -2,-1,-1],[2,2,2],True,[4*sgn,2,0])
 add('CHEST',main,root,[0,44],[-1.5 if side=='left' else -3.5,-2.5,-2.49 if side=='left' else -2.51],[5,10,5],side=='left',deform=0 if side=='left' else .01)
 add('CHEST',pauldron,main,[20,44],[-1 if side=='left' else -5,-3,-3],[6,5,6],side=='left',rotation=[0,0,-sgn*math.pi/36],deform=0 if side=='left' else .01)
 leg=side+'_leg';skirt=side+'_leg_skirt'
 add('LEGS',leg,None,[0,78],[-2.39 if side=='left' else -2.61,-.5 if side=='left' else 0,-2.49 if side=='left' else -2.51],[5,6,5],side=='left',[1.9*sgn,12,0])
 add('LEGS',skirt,leg,[0,59],[-1 if side=='left' else -4,0,-.5],[5,13,6],side=='left',[-.5*sgn,-2,-2.5],[0,-sgn*math.pi/18,-sgn*math.pi/12])
 add('FEET',leg,None,[0,89],[-2.39 if side=='left' else -2.61,8.5,-2.49 if side=='left' else -2.51],[5,4,5],side=='left',[1.9*sgn,12,0])
def faces(uv,sz):
 u,v=uv;x,y,z=sz;return {'DOWN_y_min':[u+z,v,u+z+x,v+z],'UP_y_max':[u+z+x,v+z,u+z+2*x,v],'WEST_x_min':[u,v+z,u+z,v+z+y],'NORTH_z_min':[u+z,v+z,u+z+x,v+z+y],'EAST_x_max':[u+z+x,v+z,u+2*z+x,v+z+y],'SOUTH_z_max':[u+2*z+x,v+z,u+2*z+2*x,v+z+y]}
im=Image.open(T/'model/armor_manaweave.png').convert('RGBA');assert im.size==(64,128)
for x in rows:
 x['faces']=[]
 for normal,uv in faces(x['uv'],x['nominal_size']).items():
  a,b,c,d=uv;rect=[min(a,c),min(b,d),max(a,c),max(b,d)];assert 0<=rect[0]<rect[2]<=64 and 0<=rect[1]<rect[3]<=128
  crop=im.crop(rect);x['faces'].append({'source_direction':normal,'signed_uv':uv,'raw_crop_rect':rect,'nontransparent_pixels':sum(v>0 for v in crop.getchannel('A').get_flattened_data()),'pixels':crop.width*crop.height})
assert len(rows)==17
save('slot-face-uv.json',{'scope':'default nonholiday noPhantomInk Manaweave17 source cuboids/102 raw UVrectangles; not102designs','context':'Botania exactsource declarations; MC1.20.1 ModelPart UV arithmetic reused from Forge47.4.10mappedsource, not loaded47.1.3binary','rows':rows,'empty_roots_not_counted':['outside/hat','inside/head','inside/hat','inside/left_arm','inside/right_arm','inside/body']})
for page,start in enumerate([0,9],1):
 subset=rows[start:start+9];out=Image.new('RGBA',(1200,len(subset)*110),(52,57,61,255));draw=ImageDraw.Draw(out)
 for i,x in enumerate(subset):
  draw.text((5,i*110+5),x['slot']+' '+x['part'],fill='white')
  for j,f in enumerate(x['faces']):
   crop=im.crop(f['raw_crop_rect']);px=210+j*160;draw.text((px,i*110+5),f['source_direction'],fill='white');out.alpha_composite(crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST),(px,i*110+25))
 out.save(D/f'raw-slot-face-crops-{page}.png')
paths=[T/f'item/manaweave_{s}.png' for s in ['helmet','chestplate','leggings','boots']]+[T/'model/armor_manaweave.png'];records=[]
out=Image.new('RGBA',(1050,950),(60,64,68,255));draw=ImageDraw.Draw(out)
for i,f in enumerate(paths):
 a=Image.open(f).convert('RGBA');records.append({'path':str(f.resolve()),'sha256':h(f),'size':a.size,'bbox':a.getbbox(),'alpha_values':sorted(set(a.getchannel('A').get_flattened_data()))})
 if i<4:out.alpha_composite(a.resize((160,160),Image.Resampling.NEAREST),(20+240*i,25));draw.text((20+240*i,195),f.stem,fill='white')
 else:out.alpha_composite(a.resize((320,640),Image.Resampling.NEAREST),(20,240));draw.text((370,240),'64x128 source atlas / integer NN',fill='white')
out.save(D/'native-source-study.png');save('original-image-paths.json',records)
# Every selected reused source is independently byte-bound to the fixed old commit tree.
tree=json.loads((P/'tree.json').read_text());idx={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
java=['client/model/armor/ManaweaveRobeModel.java','client/model/armor/ArmorModel.java','client/model/armor/ArmorModels.java','common/item/equipment/armor/manaweave/ManaweaveArmorItem.java','common/item/equipment/armor/manaweave/ManaweaveHelmItem.java','common/item/equipment/armor/manasteel/ManasteelArmorItem.java','client/model/BotaniaLayerDefinitions.java','client/model/BotaniaModelLayers.java','client/lib/ResourcesLib.java','common/item/BotaniaItems.java','common/lib/LibItemNames.java'];selected=[S/('Xplat/src/main/java/vazkii/botania/'+n) for n in java]+[S/'Forge/src/main/java/vazkii/botania/forge/mixin/client/ItemManasteelArmorForgeMixin.java']+paths+[S/f'Xplat/src/generated/resources/assets/botania/models/item/manaweave_{s}.json' for s in ['helmet','chestplate','leggings','boots']]
reuse=[]
for f in selected:
 n=str(f.relative_to(S));b=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==idx[n];reuse.append({'path':str(f.resolve()),'upstream_path':n,'git_blob':idx[n],'sha256':h(f)})
save('reused-source-provenance.json',{'commit':'0c06dcf7ae9555d52885f913ecd769ceb94fa823','fixed_tree':str((P/'tree.json').resolve()),'files':reuse})
print('17 source cubes/102 rectangles in bounds;5 PNG/21 reused pinned sources;4 helper-root cubes alpha',[(x['part'],sum(f['nontransparent_pixels'] for f in x['faces'])) for x in rows if x['nominal_size']==[2,2,2]])
