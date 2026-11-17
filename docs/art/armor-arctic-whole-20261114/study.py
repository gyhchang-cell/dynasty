from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,copy
D=Path(__file__).resolve().parent;R=D.parents[2];P=D.parent/'armor-sanguine-whole-20261114';T=D/'source/src/main/resources/assets/twilightforest/textures'
def h(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
base=[copy.deepcopy(x) for x in json.loads((P/'slot-face-uv.json').read_text())['rows'] if '/' not in x['part']]
for x in base:
 if x['part'] in ['right_leg','left_leg']:x['deformation']=[v+.1 for v in x['deformation']] # HumanoidModel, not HumanoidArmorModel -0.1 replacement
 x['parent']=None;x['local_rotation_radians']=[0,0,0]
extra=[('right_hood',[0,0],[-1,-2,-1],[1,4,1],[-2.5,-3,-5]),('left_hood',[0,0],[0,-2,-1],[1,4,1],[2.5,-3,-5]),('top_hood',[24,0],[-2,-1,-1],[4,1,1],[0,-5.5,-5]),('bottom_hood',[24,0],[-2,-1,-1],[4,1,1],[0,.5,-5])]
for name,uv,origin,size,offset in extra:base.append(dict(slot='HEAD',layer=1,part='head/'+name,parent='head',uv=uv,nominal_origin=origin,nominal_size=size,deformation=[.5,.5,.5],parent_offset=offset,mirror=False,local_rotation_radians=[0,0,0]))
def faces(uv,sz):
 u,v=uv;x,y,z=sz;return {'DOWN_y_min':[u+z,v,u+z+x,v+z],'UP_y_max':[u+z+x,v+z,u+z+2*x,v],'WEST_x_min':[u,v+z,u+z,v+z+y],'NORTH_z_min':[u+z,v+z,u+z+x,v+z+y],'EAST_x_max':[u+z+x,v+z,u+2*z+x,v+z+y],'SOUTH_z_max':[u+2*z+x,v+z,u+2*z+2*x,v+z+y]}
base.sort(key=lambda x:({'HEAD':0,'CHEST':1,'LEGS':2,'FEET':3}[x['slot']],x['part']))
passes=[]
for kind in ['dyed','overlay']:
 rows=copy.deepcopy(base);out=Image.new('RGBA',(1200,14*100),(53,57,61,255));draw=ImageDraw.Draw(out)
 for i,x in enumerate(rows):
  im=Image.open(T/f"armor/arcticarmor_{x['layer']}_{kind}.png").convert('RGBA');assert im.size==(64,32);x['pass']=kind;x['faces']=[];draw.text((5,i*100+5),x['slot']+' '+x['part'],fill='white')
  for j,(normal,uv) in enumerate(faces(x['uv'],x['nominal_size']).items()):
   a,b,c,d=uv;rect=[min(a,c),min(b,d),max(a,c),max(b,d)];assert 0<=rect[0]<rect[2]<=64 and 0<=rect[1]<rect[3]<=32
   crop=im.crop(rect);f={'source_direction':normal,'signed_uv':uv,'raw_crop_rect':rect,'nontransparent_pixels':sum(v>0 for v in crop.getchannel('A').get_flattened_data()),'pixels':crop.width*crop.height};x['faces'].append(f);px=215+j*160;draw.text((px,i*100+5),normal,fill='white');out.alpha_composite(crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST),(px,i*100+25))
 out.save(D/f'raw-slot-face-crops-{kind}.png');passes.append({'pass':kind,'rows':rows})
save('slot-face-uv.json',{'scope':'14 slot cube instances /84nominal face rectangles evaluated on2active passes=168rawimage rectangles, not168designs','context':'Arctic HumanoidModel.createMesh +4hood; sameMC1.20.1 arithmetic in Forge47.4.10 mapped source; declared Neo47.1.70 sourcepatch read, loadedMCbinary not run','passes':passes,'orientation':'signedUPV and mirrors preserved; crops not final vertex/pose/seams'})
paths=[T/f'item/arctic_{s}{v}.png' for s in ['helmet','chestplate','leggings','boots'] for v in ['', '_0']]+[T/f'armor/arcticarmor_{n}_{s}.png' for n in [1,2] for s in ['dyed','overlay']];records=[]
out=Image.new('RGBA',(1100,1050),(60,64,68,255));draw=ImageDraw.Draw(out)
for i,f in enumerate(paths):
 im=Image.open(f).convert('RGBA');records.append({'path':str(f.resolve()),'sha256':h(f),'size':im.size,'bbox':im.getbbox(),'alpha_values':sorted(set(im.getchannel('A').get_flattened_data()))})
 if i<8:
  col=i//2;row=i%2;xy=(20+260*col,25+200*row);out.alpha_composite(im.resize((160,160),Image.Resampling.NEAREST),xy);draw.text((xy[0],xy[1]+165),f.stem,fill='white')
 else:
  k=i-8;xy=(20+(k%2)*520,455+(k//2)*290);out.alpha_composite(im.resize((448,224),Image.Resampling.NEAREST),xy);draw.text((xy[0],xy[1]+235),f.stem+' / raw no tint',fill='white')
out.save(D/'native-source-study.png');save('original-image-paths.json',records)
# Byte comparison with old image evidence only, not proof of complete binary version identity.
old=json.loads((D.parent/'cod4-pattern-audit-v27/texture-reference-20261101/arctic-item-layer-binding.json').read_text());oldhash={e['entry'].split('/')[-1]:e['sha256'] for row in old['rows'] for e in row['source_pngs']};comparisons=[]
for a in records:
 f=Path(a['path']);prior=oldhash.get(f.name)
 if prior is None:
  matches=list((D.parent/'armor-reference-study-20261102/references/twilightforest').glob('*-'+f.name));prior=h(matches[0]) if len(matches)==1 else None
 comparisons.append({'basename':f.name,'current_sha256':a['sha256'],'old_sha256':prior,'same_bytes':prior==a['sha256'] if prior else None})
save('old-image-byte-comparison.json',{'old_item_binding':str(D.parent/'cod4-pattern-audit-v27/texture-reference-20261101/arctic-item-layer-binding.json'),'rows':comparisons,'whole_loaded_binary_identity_proven':False,'not_semantic_credit':True})
print('12 original PNG;14 slotinstances;168 rawpass rectangles;',sum(x['same_bytes'] is True for x in comparisons),'oldbyte matches')
