#!/usr/bin/env python3
"""Original cuboid quadruped and strict 16px pixels. Writes only secret-12 assets."""
import base64,json,uuid,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'src/main/resources/assets/dynasty'; D=ROOT/'docs/art/cod3-white-deer-v1'; R=ROOT/'src/main/resources/data/dynasty'
D.mkdir(parents=True,exist_ok=True)
def write(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
palette={'.':'#ffffff','W':'#ffffff','S':'#b2bfb1','D':'#29382e','G':'#71934c'}
portrait=['........','..S..S..','.SW..WS.','..DWWD..','..WWWW..','..SGGS..','..D..D..','........']
token=['........','...SS...','..SGGS..','.SGWWGS.','.SGWWGS.','..SGGS..','...SS...','........']
def pixels(rows,p):
 im=Image.new('RGB',(16,16),'white');draw=ImageDraw.Draw(im)
 for y,row in enumerate(rows):
  assert len(row)==8
  for x,ch in enumerate(row):draw.rectangle((x*2,y*2,x*2+1,y*2+1),fill=palette[ch])
 p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 return im
texture=A/'textures/entity/cod3/white_deer.png';im=pixels(portrait,texture)
pixels(token,A/'textures/item/white_deer_token.png')
uv={'W':[6,6],'S':[4,2],'D':[4,6],'G':[6,10]};bones=[];index={}
def bone(name,parent,pivot,rotation=None):
 b={'name':name,'pivot':pivot}
 if parent:b['parent']=parent
 if rotation:b['rotation']=rotation
 bones.append(b);index[name]=b
 return name
def box(name,o,s,mat='W'):
 assert all(v>0 for v in s)
 index[name].setdefault('cubes',[]).append({'origin':o,'size':s,'uv':{f:{'uv':uv[mat],'uv_size':[2,2]} for f in ['north','south','east','west','up','down']}})
bone('root',None,[0,0,0]);bone('body','root',[0,12,0]);box('body',[-3,9,-5],[6,7,12]);box('body',[-2.5,9.5,7],[5,5,1],'S')
bone('chest','body',[0,14,-5]);box('chest',[-2.75,10,-7.5],[5.5,6,3]);bone('neck','chest',[0,14,-6]);box('neck',[-2,14,-8],[4,6,3]);box('neck',[-1.75,18,-9],[3.5,3,3])
bone('head','neck',[0,20,-9]);box('head',[-2.5,19,-11.5],[5,4,6]);box('head',[-2,19,-14.5],[4,2,3])
# Nose cap projects beyond the muzzle on both side and top planes, avoiding grazing-pose z-fighting.
box('head',[-2.25,20.25,-14.75],[4.5,1,.75],'D')
for side,sgn in [('left',1),('right',-1)]:
 box('head',[sgn*2.5-(.5 if sgn<0 else 0),21,-11],[.5,1.5,2],'D')
 ear=bone(side+'_ear','head',[sgn*2,22,-8],[0,0,sgn*-25]);box(ear,[sgn*2-(3 if sgn<0 else 0),22,-9],[3,2,2],'S')
 horn=bone(side+'_antler','head',[sgn*1.5,23,-8]);x=sgn*1.5-1
 box(horn,[x,23,-9],[2,4,2],'S');box(horn,[x+(1 if sgn>0 else -2),26,-9],[3,2,2],'S');box(horn,[x+(3 if sgn>0 else -3),27,-9],[2,3,2],'S');box(horn,[x,26,-7],[2,2,3],'S')
bone('herb','head',[0,19.5,-14]);box('herb',[-.5,18,-16],[1,2.5,2],'G');box('herb',[-2,18,-18],[4,1.5,3],'G');box('herb',[-1.5,19.5,-17.5],[3,1.25,2],'S');index['herb']['locators']={'mouth_herb':[0,19.5,-14]}
bone('tail','body',[0,13,7]);box('tail',[-1,11.5,7],[2,3,3],'S');box('tail',[-.75,11,9],[1.5,2,1.25],'W')
for front,z in [('front',-5),('hind',5)]:
 for side,sign in [('left',1),('right',-1)]:
  name=front+'_'+side; x=sign*2
  bone(name+'_upper','body',[x,11,z]);box(name+'_upper',[x-1,5,z-1],[2,6,2],'W')
  bone(name+'_shin',name+'_upper',[x,5,z]);box(name+'_shin',[x-.75,1,z-.75],[1.5,4,1.5],'S')
  bone(name+'_hoof',name+'_shin',[x,1,z]);box(name+'_hoof',[x-1,0,z-1.5],[2,1.5,3],'D')
geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.white_deer','texture_width':16,'texture_height':16,'visible_bounds_width':3,'visible_bounds_height':3,'visible_bounds_offset':[0,1,0]},'bones':bones}]}
write(A/'geo/cod3/white_deer.geo.json',geo)
def keys(a,b,c):return {'0.0':a,'0.5':b,'1.0':c}
anims={}
def anim(name,length,bs):anims['animation.white_deer.'+name]={'loop':True,'animation_length':length,'bones':bs}
anim('idle',1,{'head':{'rotation':keys([0,0,0],[2,0,0],[0,0,0])},'tail':{'rotation':keys([0,-8,0],[0,8,0],[0,-8,0])}})
walk={}
for front in ('front','hind'):
 for side in ('left','right'):
  v=18*(1 if (front=='front')==(side=='left') else -1);n=front+'_'+side
  walk[n+'_upper']={'rotation':keys([v,0,0],[-v,0,0],[v,0,0])}
  walk[n+'_shin']={'rotation':keys([max(0,-v*.6),0,0],[max(0,v*.6),0,0],[max(0,-v*.6),0,0])}
walk['body']={'position':keys([0,0,0],[0,.25,0],[0,0,0])};anim('walk',1,walk)
anim('graze',1,{'neck':{'rotation':keys([32,0,0],[38,0,0],[32,0,0])},'head':{'rotation':keys([15,0,0],[10,0,0],[15,0,0])}})
anim('look_back',1,{'neck':{'rotation':keys([0,12,0],[0,18,0],[0,12,0])},'head':{'rotation':keys([0,28,0],[0,35,0],[0,28,0])}})
anim('startled',1,{'head':{'rotation':keys([-15,0,0],[-20,0,0],[-15,0,0])},'left_ear':{'rotation':keys([0,-25,0],[0,-35,0],[0,-25,0])},'right_ear':{'rotation':keys([0,25,0],[0,35,0],[0,25,0])},'tail':{'rotation':keys([-30,0,0],[-35,0,0],[-30,0,0])}})
write(A/'animations/cod3/white_deer.animation.json',{'format_version':'1.8.0','animations':anims})
# Official Bedrock codec coordinate conversion; all face UVs reference explicit islands.
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/white-deer-v1/'+s))
groups={};elements=[]
for b in bones:
 group={'name':b['name'],'type':'group','uuid':uid(b['name']),'origin':[-b['pivot'][0],*b['pivot'][1:]],'rotation':[-b.get('rotation',[0,0,0])[0],-b.get('rotation',[0,0,0])[1],b.get('rotation',[0,0,0])[2]],'export':True,'children':[]};groups[b['name']]=group
 for i,c in enumerate(b.get('cubes',[])):
  x,y,z=c['origin'];w,h,d=c['size'];ident=uid(b['name']+'/'+str(i));faces={}
  for f,m in c['uv'].items():
   u,v=m['uv'];faces[f]={'uv':[u+2,v+2,u,v] if f in ('up','down') else [u,v,u+2,v+2],'texture':0}
  elements.append({'name':b['name']+'_'+str(i),'type':'cube','uuid':ident,'from':[-x-w,y,z],'to':[-x,y+h,z+d],'origin':group['origin'],'rotation':[0,0,0],'box_uv':False,'faces':faces});group['children'].append(ident)
 for name,p in b.get('locators',{}).items():
  ident=uid(name);elements.append({'type':'locator','name':name,'uuid':ident,'position':[-p[0],*p[1:]]});group['children'].append(ident)
outliner=[]
for b in bones:
 if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
 else:outliner.append(groups[b['name']])
write(D/'blockbench/white_deer.bbmodel',{'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':'white_deer','model_identifier':'white_deer','geckolib_modid':'dynasty','resolution':{'width':16,'height':16},'elements':elements,'outliner':outliner,'textures':[{'name':'white_deer.png','id':'0','uuid':uid('texture'),'width':16,'height':16,'uv_width':16,'uv_height':16,'source':'data:image/png;base64,'+base64.b64encode(texture.read_bytes()).decode()}]})
write(D/'blockbench/white_deer.animation.json',{'format_version':'1.8.0','animations':anims})
write(D/'authoring.json',{'design':'Horizontal body 6x7x12; stepped neck; long muzzle; branching cuboid antlers; four upper/shin/hoof chains; mouth-attached herb.', 'pixels':16,'palette':palette,'explicit_white_foreground_uv':[6,6,2,2],'bones':len(bones),'cubes':sum(len(b.get('cubes',[])) for b in bones),'animations':list(anims)})
write(A/'models/item/white_deer_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
write(A/'models/item/white_deer_token.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/white_deer_token'}})
write(R/'forge/biome_modifier/white_deer.json',{'type':'forge:add_spawns','biomes':['minecraft:bamboo_jungle'],'spawners':{'type':'dynasty:white_deer','weight':1,'minCount':1,'maxCount':1}})
write(R/'loot_tables/entities/white_deer.json',{'type':'minecraft:entity','pools':[]})
write(R/'dimension/white_deer_grotto.json',{'type':'dynasty:white_deer_grotto','generator':{'type':'minecraft:flat','settings':{'biome':'minecraft:the_void','features':False,'lakes':False,'layers':[{'height':1,'block':'minecraft:air'}],'structure_overrides':[]}}})
write(R/'dimension_type/white_deer_grotto.json',{'ultrawarm':False,'natural':False,'coordinate_scale':1,'has_skylight':True,'has_ceiling':False,'ambient_light':.2,'monster_spawn_light_level':0,'monster_spawn_block_light_limit':0,'piglin_safe':False,'bed_works':True,'respawn_anchor_works':False,'has_raids':False,'logical_height':256,'min_y':0,'height':256,'infiniburn':'#minecraft:infiniburn_overworld','effects':'minecraft:overworld','fixed_time':1000})
for lang,entries in {'zh_cn':{'entity.dynasty.white_deer':'衔草白鹿','item.dynasty.white_deer_spawn_egg':'衔草白鹿刷怪蛋','item.dynasty.white_deer_token':'白鹿灵契','cod3.dynasty.deer.quiet':'不要惊扰白鹿。在晨间静步跟随它五分钟。','cod3.dynasty.deer.begin':'白鹿回望了你。保持静步，跟上它的脚步。','cod3.dynasty.deer.progress':'静步随鹿：%s / %s 秒','cod3.dynasty.deer.enter':'洞天福地已开启。使用白鹿灵契返回来处。','cod3.dynasty.deer.locked':'灵契只回应获白鹿认可的主人。','cod3.dynasty.deer.return_blocked':'来处被阻挡，请腾出安全落脚点后再返回。'},'en_us':{'entity.dynasty.white_deer':'Herb-bearing White Deer','item.dynasty.white_deer_spawn_egg':'White Deer Spawn Egg','item.dynasty.white_deer_token':'White Deer Pact','cod3.dynasty.deer.quiet':'Do not disturb the deer. Follow quietly for five minutes at dawn.','cod3.dynasty.deer.begin':'The deer looks back. Sneak and follow its steps.','cod3.dynasty.deer.progress':'Quiet trail: %s / %s seconds','cod3.dynasty.deer.enter':'The bamboo grotto opens. Use your pact to return.','cod3.dynasty.deer.locked':'The pact answers only its recognized owner.','cod3.dynasty.deer.return_blocked':'Your return point is blocked. Clear a safe landing before returning.'}}.items():
 p=A/f'lang/{lang}.json';content=json.loads(p.read_text());content.update(entries);write(p,content)
# Static checks are intentionally separate from native runtime acceptance.
assert len(set(im.getdata()))<=4 and im.size==(16,16)
for b in bones:
 assert 'parent' not in b or b['parent'] in index
 for c in b.get('cubes',[]):
  for face in c['uv'].values():
   x,y=face['uv'];assert len(set(im.crop((x,y,x+2,y+2)).getdata()))==1
for a in anims.values():
 assert set(a['bones'])<=set(index)
 for b in a['bones'].values():
  for channel in b.values():assert channel['0.0']==channel['1.0']
for p in [texture,A/'textures/item/white_deer_token.png']:
 t=Image.open(p);assert t.size==(16,16) and len(set(t.getdata()))<=4
 for x in range(16):assert t.getpixel((x,0))==(255,255,255)==t.getpixel((x,15))
 for y in range(16):assert t.getpixel((0,y))==(255,255,255)==t.getpixel((15,y))
 for y in range(0,16,2):
  for x in range(0,16,2):assert len(set(t.crop((x,y,x+2,y+2)).getdata()))==1
print('PASS original white deer: '+str(len(bones))+' bones / '+str(sum(len(b.get('cubes',[])) for b in bones))+' cuboids / 5 animations / strict 16x16 textures')
