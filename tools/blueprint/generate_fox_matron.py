"""Original four-colour cuboid robe, half mask, three tails and a same-actor fox death rig."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
ID='baimian_huxiangu';assets=Path('src/main/resources/assets/dynasty');data=Path('src/main/resources/data/dynasty')
colors=['#FFFFFF','#3B263C','#CE849B','#C5A552'];slots=[(10,10),(2,2),(10,2),(2,10)]
atlas=Image.new('RGB',(16,16),colors[0]);d=ImageDraw.Draw(atlas)
for i,box in [(1,(1,1,6,6)),(2,(9,1,14,6)),(3,(1,9,6,14))]:d.rectangle(box,fill=colors[i])
def cube(o,s,m=1):return {'origin':o,'size':s,'uv':{f:{'uv':list(slots[m]),'uv_size':[4,4]} for f in ['north','south','east','west','up','down']}}
bones=[]
def bone(n,p,pivot,c=()):
 b={'name':n,'pivot':pivot,'cubes':list(c)}
 if p:b['parent']=p
 bones.append(b)
bone('root',None,[0,0,0]);bone('robe_root','root',[0,0,0]);bone('pelvis','robe_root',[0,12,0],[cube([-3.5,10,-2.5],[7,4,5],2)])
bone('waist','pelvis',[0,14,0],[cube([-3,14,-2.4],[6,3,4.8],3)])
bone('chest','waist',[0,17,0],[cube([-4.5,17,-3],[9,6,6],2),cube([-1.5,17,-3.4],[3,6,.8],3),cube([-4,17,2.6],[8,5,1])])
for side,sign in [('left',1),('right',-1)]:
 x=sign*3
 bone('skirt_'+side,'pelvis',[x,12,0],[cube([x-2.5,0,-3.2],[5,12,6.4],2),cube([x-1,0,-3.7],[2,10,.7],3)])
 x=sign*5.5
 bone(side+'_upper_arm','chest',[x,22,0],[cube([x-2,16,-2],[4,6,4],1),cube([x-2.5,15,-2.5],[5,4,5],2)])
 bone(side+'_forearm',side+'_upper_arm',[x,16,0],[cube([x-1.5,11,-1.5],[3,5,3],0)])
 bone(side+'_hand',side+'_forearm',[x,11,0],[cube([x-1.4,9.5,-1.6],[2.8,2,3.2],0)])
bone('neck','chest',[0,23,0],[cube([-1.6,23,-1.5],[3.2,2,3],0)])
bone('head','neck',[0,25,0],[cube([-3.7,24,-3],[7.4,5,6],0),cube([-4,24,2],[8,7,2])])
bone('hair_bun','head',[0,28,0],[cube([-3,29,-1],[6,2,4]),cube([-5,29,0],[10,1.3,1.5],3)])
bone('half_mask','head',[0,26,-3],[cube([-3.5,24.5,-3.6],[3.7,4.5,.9],0),cube([-3,28.5,-3.4],[2,2,1],0),cube([-2.5,26,-4.1],[2,1.1,.8]),cube([-1.5,24.8,-4],[1.5,1.2,1],3)])
bone('mask_crack','half_mask',[-1,27,-4.3],[cube([-1.5,26.5,-4.4],[1,2,.3],2),cube([-2.5,27.5,-4.4],[1,1,.3],2)])
bone('fan','left_hand',[5.5,10,0],[cube([5,6,-.5],[1,7,1],3),cube([1,10,-.8],[9,2,1.5],0),cube([2,12,-.8],[7,2,1.5],0),cube([3,14,-.8],[5,1.5,1.5],3)])
for i in range(3):
 x=(i-1)*3
 bone('tail_'+str(i)+'_0','pelvis',[x,12,2.5],[cube([x-1.6,9,2.5],[3.2,3.2,6],0)])
 bone('tail_'+str(i)+'_1','tail_'+str(i)+'_0',[x,10,8],[cube([x-2,7.5,8],[4,4,6],0)])
 bone('tail_'+str(i)+'_2','tail_'+str(i)+'_1',[x,9.5,13.5],[cube([x-1.7,7.8,13.5],[3.4,3.4,5],0),cube([x-1.3,8.2,17.5],[2.6,2.6,3],2)])
# A small three-tailed white fox emerges as the robe collapses, still using the original entity.
bone('death_fox','root',[0,0,0],[cube([-2,2,-4],[4,3,7],0)])
bone('fox_head','death_fox',[0,4,-4],[cube([-2,3,-7],[4,3,4],0),cube([-1,3,-8],[2,2,2],0),cube([-2,6,-6],[1.5,2,1.5]),cube([.5,6,-6],[1.5,2,1.5]),cube([-1.8,4.5,-7.2],[1,1,.4]),cube([.8,4.5,-7.2],[1,1,.4])])
for i,x in enumerate([-1.5,1.5]):
 for j,z in enumerate([-2,2]):bone(f'fox_leg_{i}_{j}','death_fox',[x,2,z],[cube([x-.6,.1,z-.8],[1.2,2,1.6],0)])
for i in range(3):bone('fox_tail_'+str(i),'death_fox',[(i-1)*1.5,3,2.5],[cube([(i-1)*1.5-.8,2.5,2.5],[1.6,2,5],0)])
rig={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+ID,'texture_width':16,'texture_height':16,'visible_bounds_width':5,'visible_bounds_height':4,'visible_bounds_offset':[0,1.8,0]},'bones':bones}]}
A={}
def tr(kind,frames):return {kind:{str(t):v for t,v in frames}}
def rot(frames):return tr('rotation',frames)
def clip(n,L,ch,loop=False):A['animation.'+ID+'.'+n]={'loop':loop,'animation_length':L,'bones':ch}
def tails(L,spread=12):
 ch={}
 for i in range(3):
  for k in range(3):ch[f'tail_{i}_{k}']=rot([(0,[0,(i-1)*spread,3-k*4]),(L/2,[5,(i-1)*spread+5,k*3]),(L,[0,(i-1)*spread,3-k*4])])
 return ch
clip('idle',2,{'root':tr('position',[(0,[0,0,0]),(1,[0,.6,0]),(2,[0,0,0])]),**tails(2)},True)
clip('walk',1,{'chest':rot([(0,[5,0,-3]),(.5,[5,0,3]),(1,[5,0,-3])]),**tails(1)},True)
clip('hurt',.4,{'chest':rot([(0,[0,0,0]),(.15,[-15,0,-8]),(.4,[0,0,0])]),**tails(.4)})
clip('mirror',3.8,{'left_upper_arm':rot([(0,[0,0,0]),(.7,[-115,0,-20]),(1,[-115,0,-20]),(2.6,[-95,0,-15]),(3.8,[0,0,0])]),'left_forearm':rot([(0,[0,0,0]),(.7,[-35,0,0]),(2.6,[-35,0,0]),(3.8,[0,0,0])]),'fan':rot([(0,[0,0,0]),(.7,[0,0,35]),(2.6,[0,0,35]),(3.8,[0,0,0])]),**tails(3.8)})
clip('fire',4.95,{'right_upper_arm':rot([(0,[0,0,0]),(1,[-150,0,10]),(3.4,[-150,0,10]),(4.95,[0,0,0])]),'left_upper_arm':rot([(0,[0,0,0]),(1,[-70,0,-45]),(3.4,[-70,0,-45]),(4.95,[0,0,0])]),**tails(4.95,35)})
clip('split',1.55,{'chest':rot([(0,[0,0,0]),(.3,[0,80,0]),(.65,[0,-40,0]),(1.55,[0,0,0])]),**tails(1.55,30)})
clip('death',3.5,{'robe_root':{**tr('position',[(0,[0,0,0]),(1.2,[0,-2,0]),(3.5,[0,-2,0])]),**tr('scale',[(0,[1,1,1]),(1.2,[1,.08,1]),(3.5,[1,.08,1])])},'half_mask':{**tr('position',[(0,[0,0,0]),(.6,[0,-5,-2]),(1.2,[0,-12,-3])]),**rot([(0,[0,0,0]),(1.2,[75,0,0])])},'death_fox':tr('position',[(0,[0,0,0]),(1.25,[0,0,0]),(2.5,[0,0,-24]),(3.5,[0,0,-32])]),**tails(3.5)})
for directory,ext,v in [('geo','.geo.json',rig),('animations','.animation.json',{'format_version':'1.8.0','animations':A})]:
 p=assets/directory/'blueprint/elite'/(ID+ext);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
p=assets/'textures/entity/blueprint/elite'/(ID+'.png');p.parent.mkdir(parents=True,exist_ok=True);atlas.save(p)
for name,label in [('white_fox_fur','三尾白狐绒'),('bone_fan_fragment','金丝骨扇残片'),('fox_mask_flake','狐面瓷片')]:
 icon=Image.new('RGB',(16,16),'white');g=ImageDraw.Draw(icon)
 g.rectangle((3,3,12,12),fill=colors[1]);g.rectangle((5,5,10,10),fill=colors[2] if name!='white_fox_fur' else colors[0]);g.rectangle((7,5,8,10),fill=colors[3])
 icon.save(assets/'textures/item'/(name+'.png'))
 (assets/'models/item'/(name+'.json')).write_text(json.dumps({'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+name}},indent=2)+'\n')
(assets/'models/item'/(ID+'_spawn_egg.json')).write_text(json.dumps({'parent':'minecraft:item/template_spawn_egg'},indent=2)+'\n')
(data/'tags/worldgen/structure/blueprint/fox_sites.json').write_text(json.dumps({'replace':False,'values':['dynasty:herbal_retreat']},indent=2)+'\n')
(data/'loot_tables/entities'/(ID+'.json')).write_text(json.dumps({'type':'minecraft:entity','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+n}]} for n in ['white_fox_fur','bone_fan_fragment','fox_mask_flake']]},indent=2)+'\n')
(data/'advancements/blueprint'/('kill_'+ID+'.json')).write_text(json.dumps({'criteria':{'kill':{'trigger':'minecraft:player_killed_entity','conditions':{'entity':{'type':'dynasty:'+ID,'nbt':'{FoxDecoy:0b}'}}}}},indent=2)+'\n')
for language,labels in [('zh_cn',{'entity.dynasty.'+ID:'白面狐仙姑','effect.dynasty.fox_haze':'狐火幻镜','item.dynasty.white_fox_fur':'三尾白狐绒','item.dynasty.bone_fan_fragment':'金丝骨扇残片','item.dynasty.fox_mask_flake':'狐面瓷片','item.dynasty.'+ID+'_spawn_egg':'白面狐仙姑刷怪蛋'}),('en_us',{'entity.dynasty.'+ID:'White-mask Fox Matron','effect.dynasty.fox_haze':'Fox Haze','item.dynasty.white_fox_fur':'Three-tail Fox Fur','item.dynasty.bone_fan_fragment':'Bone Fan Fragment','item.dynasty.fox_mask_flake':'Fox Mask Flake','item.dynasty.'+ID+'_spawn_egg':'Fox Matron Spawn Egg'})]:
 p=assets/'lang'/(language+'.json');content=json.loads(p.read_text());content.update(labels);p.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
assert len(atlas.getcolors(256))==4 and atlas.size==(16,16)
assert set(b['name'] for b in bones).issuperset(n for a in A.values() for n in a['bones'])
print(ID,len(bones),'bones',sum(len(b['cubes']) for b in bones),'cuboids',len(A),'clips;16px four-color palette')

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()
