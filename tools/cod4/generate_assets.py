"""Reproducible native GeckoLib rigs, vanilla JSON assets and recipes for COD4.
No raster edits: the existing Dynasty material atlases and vanilla item sprites are reused.
"""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parents[2]; A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'src/main/resources/data/dynasty'
rows=json.loads((ROOT/'docs/cod4/secondary-roster.json').read_text())
def write(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def box(x,y,z,w,h,d):return {'origin':[x,y,z],'size':[w,h,d],'uv':[0,0]}
def rig(r):
 bones=[]
 def bone(name,parent=None,pivot=(0,0,0),cubes=None,rotation=None):
  b={'name':name,'pivot':list(pivot)}
  if parent:b['parent']=parent
  if cubes:b['cubes']=cubes
  if rotation:b['rotation']=rotation
  bones.append(b)
 bone('root'); id=r['id'];n=r['index'];human=n<=5 or n==14;snake=id in ('giant_python','stone_worm');bird=n in (20,21,22,29);water=15<=n<=19
 if human:
  bone('pelvis','root',(0,12,0),[box(-3,11,-2,6,3,4)])
  bone('waist','pelvis',(0,14,0),[box(-2.5,14,-1.8,5,2,3.6)])
  bone('chest','waist',(0,16,0),[box(-3.5,16,-2.2,7,6,4.4)],[-12 if n==1 else 0,0,0])
  bone('neck','chest',(0,22,0),[box(-1.2,22,-1,2.4,2,2)])
  bone('head','neck',(0,24,0),[box(-2.5,24,-2.5,5,5,5),box(-.65,25.3,-3.2,1.3,1.3,1)])
  for side,s in [('left',1),('right',-1)]:
   bone(side+'_upper_arm','chest',(s*4,21,0),[box(s*4-1.1,17,-1.1,2.2,4,2.2)])
   bone(side+'_elbow',side+'_upper_arm',(s*4,17,0),[box(s*4-1,16,-1,2,1,2)])
   bone(side+'_forearm',side+'_elbow',(s*4,16,0),[box(s*4-1,12.5,-1,2,3.5,2)])
   bone(side+'_wrist',side+'_forearm',(s*4,12.5,0),[box(s*4-.8,12,-.8,1.6,.5,1.6)])
   bone(side+'_hand',side+'_wrist',(s*4,12,0),[box(s*4-.9,10.5,-.9,1.8,1.5,1.8)])
   bone(side+'_thigh','pelvis',(s*1.7,12,0),[box(s*1.7-1.3,7,-1.5,2.6,5,3)])
   bone(side+'_knee',side+'_thigh',(s*1.7,7,0),[box(s*1.7-1.2,6,-1.4,2.4,1,2.8)])
   bone(side+'_shin',side+'_knee',(s*1.7,6,0),[box(s*1.7-1.1,2,-1.2,2.2,4,2.4)])
   bone(side+'_ankle',side+'_shin',(s*1.7,2,0),[box(s*1.7-.8,1,-.8,1.6,1,1.6)])
   bone(side+'_foot',side+'_ankle',(s*1.7,1,0),[box(s*1.7-1.3,0,-2.5,2.6,1.5,4)])
  if n==1:bone('rags','chest',(0,18,0),[box(-4,17,1.6,8,3,1),box(-3,10,1,2,6,1)])
  if n==2:bone('mask','head',(0,26,0),[box(-2.7,24,-2.7,5.4,2.2,1)]);bone('blade','right_hand',(-4,11,0),[box(-4.3,6,-.4,.6,9,.8),box(-4.7,15,-.3,1.4,5,.6)])
  if n==3:bone('lantern','left_hand',(4,11,0),[box(3.5,7,-.5,1,4,1),box(2,3,-2,4,4,4)]);bone('clapper','right_hand',(-4,11,0),[box(-4.5,7,-.7,1,5,1.4)])
  if n==4:bone('robe','pelvis',(0,12,0),[box(-4,5,-2.5,8,7,5)]);bone('abacus','left_hand',(4,11,0),[box(2,9,-3,5,1,6)])
  if n==5:bone('basket','chest',(0,16,2),[box(-4,11,2,8,9,5),box(-4.5,19,1.5,9,1,6)])
  if n==14:
   for b in bones:
    for c in b.get('cubes',[]):c['size'][2]=.3;c['origin'][2]=-.15
 elif snake:
  bone('body','root',(0,4,0),[box(-3,1,-5,6,6,10)])
  parent='body'
  for i in range(1,7):
   name=f'segment_{i}';z=4+(i-1)*3.5;size=max(1,6-i*.7)
   bone(name,parent,(0,3,z),[box(-size/2,1,z,size,size,4)]);parent=name
  bone('neck','body',(0,4,-4),[box(-2.5,2,-9,5,5,5)])
  bone('head','neck',(0,5,-9),[box(-3,2,-14,6,4,6),box(-2,1,-13,4,1,5)])
 elif bird:
  bone('body','root',(0,8,0),[box(-2.5,6,-3,5,5,7)])
  bone('neck','body',(0,10,-3),[box(-1.5,9,-5,3,3,3)])
  bone('head','neck',(0,12,-4),[box(-2,10,-7,4,4,4),box(-.75,10.5,-10,1.5,1.5,3)])
  for side,s in [('left',1),('right',-1)]:
   bone(side+'_wing','body',(s*2,9,0),[box(2 if s>0 else -9,8,-2,7,1,6)])
   bone(side+'_wingtip',side+'_wing',(s*9,9,0),[box(9 if s>0 else -15,8,-1,6,.5,5)])
   bone(side+'_foot','body',(s,6,0),[box(s-.4,3,-.5,.8,3,1),box(s-.6,2,-2,1.2,1,3)])
  bone('tail','body',(0,8,4),[box(-2,7,4,4,1,7)])
  if n==20:bone('ears','head',(0,13,-5),[box(-2,13,-6,1,3,1),box(1,13,-6,1,3,1)])
  if n==21:bone('stone','head',(0,10,-10),[box(-1,9,-11,2,2,2)])
  if n==29:bone('gears','body',(0,9,0),[box(-3,7,-1,6,4,2),box(-1,6,-1,2,6,2)])
 elif n in (13,27,28):
  bone('body','root',(0,12,0),[box(-4,8,-3,8,10,6)])
  bone('head','body',(0,18,0),[box(-3,18,-2.5,6,5,5)])
  bone('tail','body',(0,9,0),[box(-2,3,-1,4,5,2)])
  if n==13:bone('ribs','body',(0,12,0),[box(-5,8,-4,10,1,8),box(-5,18,-4,10,1,8)])
  if n==27:
   for i in range(8):
    angle=i*math.pi/4;bone('paper_'+str(i),'body',(0,12,0),[box(math.cos(angle)*6,11+math.sin(angle)*6,-1,3,3,.2)])
 elif n==23:
  bone('body','root',(0,8,0))
  for i in range(14):
   x=(i%4-1.5)*4;y=5+(i%3)*3;z=(i//4-1.5)*4
   bone('insect_'+str(i),'body',(x,y,z),[box(x-.7,y,z,1.4,.9,2.4),box(x-2,y+.4,z,4,.15,1)])
 elif water and n not in (17,19):
  bone('body','root',(0,9,0),[box(-3,6,-2,6,10,4)])
  bone('head','body',(0,16,0),[box(-3,16,-3,6,5,6)])
  bone('tail','body',(0,6,0),[box(-2,0,-1,4,6,3)])
  for side,s in [('left',1),('right',-1)]:bone(side+'_fin','body',(s*3,12,0),[box(s*4-1,7,-1,2,7,2)])
  if n==15:bone('dish','head',(0,21,0),[box(-4,20.5,-4,8,.5,8)])
  if n==16:bone('hair','head',(0,19,0),[box(-3.5,10,1.8,7,12,1)])
  if n==18:bone('shell','body',(0,10,3),[box(-5,5,1,10,10,6),box(-3,7,7,6,6,2)])
 else:
  big=n in (11,12);insect=n in (19,24,25);fish=n==17
  bone('body','root',(0,6,0),[box(-4,4,-5,8,6 if not big else 12,12)])
  bone('neck','body',(0,7,-5),[box(-2.5,6,-8,5,4,4)])
  bone('head','neck',(0,8,-7),[box(-3,5,-12,6,5,5),box(-2,5,-14,4,2,3)])
  bone('tail','body',(0,7,6),[box(-1,5,6,2,2,8)])
  for i in range(6 if insect else 4):
   s=1 if i%2 else -1;z=(-3 if i<2 else 4)+(i//4)*2
   bone('leg_'+str(i),'body',(s*3,6,z),[box(s*4-1,2,z-1,2,4,2)])
   bone('foot_'+str(i),'leg_'+str(i),(s*4,2,z),[box(s*4-1.1,0,z-2,2.2,2,3)])
  if n in (6,7,10,30):bone('ears','head',(0,10,-10),[box(-3,10,-10,1.5,3,2),box(1.5,10,-10,1.5,3,2)])
  if n==8:bone('tusks','head',(0,6,-12),[box(-3,5,-15,1,3,3),box(2,5,-15,1,3,3)])
  if n==11:
   for i in range(4):bone('branch_'+str(i),'body',(0,16,0),[box((i-2)*3,14,-2,1.5,10-i,2)])
  if n==12:bone('boulder','body',(0,12,0),[box(-5,10,-4,10,7,9)])
  if n in (19,25):
   for side,s in [('left',1),('right',-1)]:bone(side+'_claw','body',(s*4,7,-3),[box(s*7-2,4,-10,4,4,7),box(s*7-2,4,-13,1.2,4,3),box(s*7+.8,4,-13,1.2,4,3)])
  if n==25:bone('stinger','tail',(0,7,10),[box(-1,7,9,2,8,2),box(-.5,14,6,1,1,4)])
  if n==30:bone('key','body',(0,9,1),[box(-.5,9,0,1,6,1),box(-3,13,0,6,1,1)])
  if fish:
   bones=[b for b in bones if not b['name'].startswith(('leg_','foot_'))]
   for side,s in [('left',1),('right',-1)]:bone(side+'_fin','body',(s*4,8,0),[box(s*4-3,7,-1,6,.3,5)])
 geometry={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.secondary.'+id,'texture_width':64,'texture_height':64,'visible_bounds_width':4,'visible_bounds_height':4,'visible_bounds_offset':[0,1,0]},'bones':bones}]}
 write(A/'geo/secondary'/f'{id}.geo.json',geometry)
 names={b['name'] for b in bones};animations={}
 for state in ('idle','wander','hunt','flee','attack','special','evade'):
  moving=state in ('wander','hunt','flee');duration=.65 if moving else 1.5
  motion={'root':{'position':[0,'math.sin(query.anim_time * 180) * 0.25',0]}}
  for name in sorted(names):
   if 'wing' in name:motion[name]={'rotation':[0,0,f'math.sin(query.anim_time * 720) * {30 if name.startswith("left") else -30}']}
   if moving and (name.startswith('leg_') or name.endswith('_thigh')):motion[name]={'rotation':[f'math.sin(query.anim_time * 540) * {24 if "left" in name or name[-1:] in "02" else -24}',0,0]}
   if name.startswith('segment_') or name=='tail':motion[name]={'rotation':[0,'math.sin(query.anim_time * 180) * 12',0]}
  if state in ('attack','special'):
   motion['root']={'rotation':{'0.0':[0,0,0],'0.2':[-15,0,0],'0.5':[0,0,0]}}
   if 'right_upper_arm' in names:motion['right_upper_arm']={'rotation':{'0.0':[-35,0,0],'0.2':[-95,0,-10],'0.5':[0,0,0]}}
  animations[state]={'loop':True,'animation_length':duration,'bones':motion}
 write(A/'animations/secondary'/f'{id}.animation.json',{'format_version':'1.8.0','animations':animations})
for r in rows:rig(r)

zh=json.loads((A/'lang/zh_cn.json').read_text());en=json.loads((A/'lang/en_us.json').read_text())
names={'qimen_cable':'奇门钢索','qimen_gear':'奇门机括','fox_pelt':'狐皮','wolf_fang':'狼牙','python_gall':'蟒蛇胆','crab_shell':'蟹甲','kappa_scale':'河童鳞','sprite_jade':'石精玉粒','lantern_oil':'灯油','locust_dust':'蝗粉','repeating_crossbow':'连弩','siege_crossbow':'重弩','rope_dart':'绳镖','meteor_hammer':'流星锤','mandarin_duck_axe':'鸳鸯钺','flying_claw':'飞爪','poison_arrow':'淬毒矢','pierce_arrow':'破甲矢','thunder_arrow':'引雷矢','heavy_bolt':'重钢弩矢','repeating_bolt':'连发弩矢','regen_pill':'回春丹','qi_pill':'聚气丹','antidote_pill':'避毒丹','zhuangyuan_wine':'状元酒','marching_wine':'壮行酒','soul_incense':'安魂香','guide_incense':'引路香','army_ration':'军粮'}
textures={'qimen_cable':'minecraft:item/string','qimen_gear':'minecraft:item/clock','fox_pelt':'minecraft:item/rabbit_hide','wolf_fang':'minecraft:item/bone','python_gall':'minecraft:item/spider_eye','crab_shell':'minecraft:item/scute','kappa_scale':'minecraft:item/prismarine_shard','sprite_jade':'dynasty:item/jade','lantern_oil':'minecraft:item/honey_bottle','locust_dust':'minecraft:item/gunpowder','rope_dart':'minecraft:item/trident','meteor_hammer':'minecraft:item/netherite_axe','mandarin_duck_axe':'minecraft:item/iron_axe','flying_claw':'minecraft:item/tripwire_hook','regen_pill':'minecraft:item/slime_ball','qi_pill':'minecraft:item/magma_cream','antidote_pill':'minecraft:item/fermented_spider_eye','zhuangyuan_wine':'minecraft:item/honey_bottle','marching_wine':'minecraft:item/potion','soul_incense':'minecraft:item/blaze_rod','guide_incense':'minecraft:item/stick','army_ration':'minecraft:item/bread'}
for id,name in names.items():
 zh['item.dynasty.'+id]=name;en['item.dynasty.'+id]=id.replace('_',' ').title()
 if id.endswith('crossbow'):
  model={'parent':'minecraft:item/crossbow','textures':{'layer0':'minecraft:item/crossbow_standby'},'overrides':[{'predicate':{'pulling':1},'model':'minecraft:item/crossbow_pulling_0'},{'predicate':{'pulling':1,'pull':.58},'model':'minecraft:item/crossbow_pulling_1'},{'predicate':{'pulling':1,'pull':1},'model':'minecraft:item/crossbow_pulling_2'},{'predicate':{'charged':1},'model':'minecraft:item/crossbow_arrow'}]}
 else:model={'parent':'minecraft:item/handheld' if id in ('rope_dart','meteor_hammer','mandarin_duck_axe','flying_claw') else 'minecraft:item/generated','textures':{'layer0':textures.get(id,'minecraft:item/arrow')}}
 write(A/'models/item'/f'{id}.json',model)
for r in rows:
 id=r['id'];zh['entity.dynasty.'+id]=r['name'];en['entity.dynasty.'+id]=id.replace('_',' ').title();zh['item.dynasty.'+id+'_spawn_egg']=r['name']+'刷怪蛋';en['item.dynasty.'+id+'_spawn_egg']=en['entity.dynasty.'+id]+' Spawn Egg'
 write(A/'models/item'/f'{id}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
 material={6:'fox_pelt',7:'wolf_fang',9:'python_gall',12:'sprite_jade',13:'lantern_oil',15:'kappa_scale',19:'crab_shell',23:'locust_dust',29:'qimen_gear',30:'qimen_cable'}.get(r['index'])
 common={1:'minecraft:string',2:'dynasty:copper_coin',3:'dynasty:lantern_oil',4:'dynasty:copper_coin',5:'dynasty:herb',8:'minecraft:porkchop',10:'minecraft:leather',11:'minecraft:slime_ball',14:'dynasty:talisman_paper',16:'minecraft:string',17:'minecraft:prismarine_shard',18:'minecraft:nautilus_shell',20:'minecraft:leather',21:'minecraft:flint',22:'minecraft:feather',24:'dynasty:crab_shell',25:'minecraft:spider_eye',26:'minecraft:iron_nugget',27:'minecraft:paper',28:'minecraft:ghast_tear'}
 drop='dynasty:'+material if material else common.get(r['index'],'minecraft:bone')
 if drop=='dynasty:herb':drop='minecraft:wheat_seeds'
 write(D/'loot_tables/entities'/f'{id}.json',{'type':'minecraft:entity','pools':[{'rolls':1,'conditions':[{'condition':'minecraft:killed_by_player'},{'condition':'minecraft:random_chance','chance':.55}],'entries':[{'type':'minecraft:item','name':drop}]}]})
 habitats=['#minecraft:is_forest','#minecraft:is_mountain']
 if 15<=r['index']<=19:habitats=['#minecraft:is_river','#minecraft:is_ocean','minecraft:swamp']
 if r['index'] in (23,25):habitats=['minecraft:desert','minecraft:badlands','minecraft:savanna']
 if r['index'] in (20,24,26,30):habitats=['minecraft:dripstone_caves','minecraft:lush_caves','minecraft:deep_dark']
 write(D/'tags/worldgen/biome/secondary'/f'{id}.json',{'replace':False,'values':habitats})

materials=['qimen_cable','qimen_gear','fox_pelt','wolf_fang','python_gall','crab_shell','kappa_scale','sprite_jade','lantern_oil','locust_dust']
recipes={
'qimen_cable':(['dynasty:refined_steel','minecraft:string','minecraft:string'],2),
'qimen_gear':(['dynasty:refined_steel','minecraft:copper_ingot','minecraft:redstone'],2),
'repeating_crossbow':(['minecraft:crossbow','dynasty:qimen_gear','dynasty:qimen_cable','dynasty:jade'],1),
'siege_crossbow':(['dynasty:repeating_crossbow','dynasty:dragon_crystal','dynasty:qimen_gear','dynasty:refined_steel'],1),
'rope_dart':(['dynasty:qimen_cable','dynasty:refined_steel','dynasty:jade'],1),
'flying_claw':(['dynasty:qimen_cable','minecraft:iron_ingot','minecraft:tripwire_hook'],1),
'meteor_hammer':(['dynasty:qimen_gear','dynasty:qimen_cable','dynasty:dragon_crystal','minecraft:anvil'],1),
'mandarin_duck_axe':(['dynasty:qimen_gear','dynasty:refined_steel','dynasty:jade'],1),
'poison_arrow':(['minecraft:arrow','dynasty:locust_dust','minecraft:spider_eye'],4),
'pierce_arrow':(['minecraft:arrow','dynasty:wolf_fang','dynasty:refined_steel'],4),
 'thunder_arrow':(['minecraft:arrow','minecraft:amethyst_shard','minecraft:redstone'],4),
 'heavy_bolt':(['minecraft:arrow','dynasty:refined_steel','dynasty:crab_shell'],4),
 'repeating_bolt':(['minecraft:arrow','dynasty:qimen_gear','minecraft:feather'],8),
 'regen_pill':(['minecraft:glistering_melon_slice','dynasty:sprite_jade','minecraft:honey_bottle'],2),
 'qi_pill':(['dynasty:sprite_jade','minecraft:blaze_powder','minecraft:sugar'],2),
 'antidote_pill':(['dynasty:python_gall','minecraft:sugar','minecraft:kelp'],2),
 'zhuangyuan_wine':(['minecraft:honey_bottle','dynasty:python_gall','minecraft:sugar'],1),
 'marching_wine':(['minecraft:honey_bottle','dynasty:wolf_fang','minecraft:red_mushroom'],1),
 'soul_incense':(['minecraft:stick','dynasty:lantern_oil','minecraft:paper'],4),
 'guide_incense':(['minecraft:stick','dynasty:lantern_oil','minecraft:redstone'],2),
 'army_ration':(['minecraft:bread','minecraft:cooked_porkchop','minecraft:dried_kelp'],2),
}
for id,(ingredients,count) in recipes.items():write(D/'recipes/cod4'/f'{id}.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':i} for i in ingredients],'result':{'item':'dynasty:'+id,'count':count}})
# Alternative recipes retain all existing sources and give each new material at least two real uses.
for id,ingredients,result,count in [
 ('fox_charm',['dynasty:fox_pelt','dynasty:silk','dynasty:jade'],'dynasty:fox_tail_charm',1),
 ('fox_leather',['dynasty:fox_pelt'],'minecraft:leather',2),
 ('crab_steel',['dynasty:crab_shell','minecraft:iron_ingot'],'dynasty:refined_steel',1),
 ('kappa_pearl',['dynasty:kappa_scale','minecraft:ender_pearl','dynasty:jade'],'dynasty:sea_pearl',1),
 ('kappa_ration',['dynasty:kappa_scale','minecraft:bread','minecraft:kelp'],'dynasty:army_ration',2),
 ('locust_antidote',['dynasty:locust_dust','dynasty:python_gall','minecraft:sugar'],'dynasty:antidote_pill',3),
 ]:write(D/'recipes/cod4'/f'{id}.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':i} for i in ingredients],'result':{'item':result,'count':count}})
# Effect icons reuse existing, already reviewed native icons unchanged.
import shutil
for id,name,source in [('yin_qi','阴气','internal_injury'),('yang_qi','阳气','dragon_might'),('sha_qi','煞气','intimidation'),('thunder_mark','雷印','swift_wind'),('soul_burn','灼魂','intimidation'),('frost_vein','寒脉','internal_injury'),('armor_break','裂甲','iron_wall'),('stagger','破势','internal_injury')]:
 zh['effect.dynasty.'+id]=name;en['effect.dynasty.'+id]=id.replace('_',' ').title();src=A/'textures/mob_effect'/f'{source}.png';dst=A/'textures/mob_effect'/f'{id}.png'
 if src.exists():shutil.copyfile(src,dst)
site_ids=['wayside_shrine','nameless_tomb','old_weapon_rack','sword_scar_wall','herb_spot','abandoned_armory','puzzle_box','battlefield_remnant','broken_stele','mortuary_room','ghost_market_boat','wayside_tea_stall','old_bellows','broken_waterwheel','ancient_well']
# Registered Sites inherit stone harvest rules; preserve ordinary native recovery.
for tool,ids in [('pickaxe',site_ids),('axe',[site_ids[i] for i in (2,5,6,10,11,12,13)])]:
 tag=ROOT/'src/main/resources/data/minecraft/tags/blocks/mineable'/f'{tool}.json'
 data=json.loads(tag.read_text()) if tag.exists() else {'replace':False,'values':[]}
 for id in ids:
  if 'dynasty:'+id not in data['values']:data['values'].append('dynasty:'+id)
 write(tag,data)
site_names=['小神龛','无名墓','旧兵器架','剑痕石壁','药草点','废弃军械','小机关盒','古战场残迹','破损界碑','义庄停尸','鬼市小舟','古道茶摊','旧风箱','残破水车','古井沉冤']
hints=['手持安魂香祈福','手持鲜花祭扫','检视兵器架','露天月光下持剑，依剑影东移、西移、北移并主手空挥；前两步朝北、最后朝东，每段四十秒。','采集药草','拆解军械','朝北站立、朝东潜行、朝南站立，再朝西潜行按动木销；按锁纹提示等待。','调查三处不同位置的古战场残迹','手持纸张拓印','先辨认微弱气息，两分钟后持治疗药水救助生者；牛奶仍可净化自身。','点一支阴香请船夫，询问后等两分钟，再持朱砂重新点击小舟交付；可进入原生交易。','察看油膜、无招牌和老汉，等两分钟后选择掀桌；直接喝会中毒，牛奶原解毒保留。','手持木炭，30秒后给三格内装有有效配方的熔炉助燃。','手持一条奇门钢索，一分钟后修复水车并恢复机关通路。','七次交付实际清水并保留空桶，按提示等待三分钟；空桶不计数。']
verified_hint_en={'sword_scar_wall': 'In open moonlight, step east, west, then north and swing your main-hand sword; face north, north, east. Retain forty-second stages.', 'wayside_tea_stall': 'Inspect the oily tea and unsigned stall, then overturn after two minutes. Drinking poisons you; original milk cleansing remains.', 'ghost_market_boat': 'Light Soul Incense, ask the boatman, then reopen holding Cinnabar after two minutes to deliver; native trading is available.', 'ancient_well': 'Deliver seven actual water buckets over at least three minutes; empty buckets do not count.', 'puzzle_box': 'Press north standing, east sneaking, south standing, then west sneaking; follow the lock timing.', 'mortuary_room': 'Identify the faint breath, then offer a healing potion after two minutes; milk still cleanses you.', 'old_bellows': 'After 30 seconds, offer charcoal beside a furnace with a valid recipe and output space.', 'broken_waterwheel': 'Offer one qimen cable after a minute to repair the wheel and restore the mechanism route.'}
for index,(id,name,hint) in enumerate(zip(site_ids,site_names,hints)):
 zh['block.dynasty.'+id]=name;en['block.dynasty.'+id]=id.replace('_',' ').title();zh['interaction.dynasty.'+id]=hint;en['interaction.dynasty.'+id]=verified_hint_en.get(id,'Inspect the site and bring the required offering.')
 wood=index in (2,5,6,10,11,12,13);texture='minecraft:block/oak_planks' if wood else 'minecraft:block/mossy_stone_bricks'
 # Distinct native block silhouettes, using existing vanilla material textures.
 shapes={
 'wayside_shrine':[(1,0,1,15,2,15),(2,2,10,14,12,14),(2,2,2,4,12,10),(12,2,2,14,12,10),(0,12,0,16,15,16),(6,2,5,10,7,9)],
 'nameless_tomb':[(1,0,2,15,3,15),(3,3,5,13,5,14),(5,3,2,11,14,5)],
 'old_weapon_rack':[(1,0,2,4,2,14),(12,0,2,15,2,14),(2,2,7,4,14,9),(12,2,7,14,14,9),(2,11,7,14,13,9),(5,2,6,6,16,7),(9,3,6,10,16,7)],
 'sword_scar_wall':[(2,0,5,14,3,14),(3,3,7,9,15,13),(10,3,7,13,14,13),(9,3,8,10,15,13)],
 'herb_spot':[(1,0,1,15,2,15),(3,2,4,5,5,6),(7,2,9,9,7,11),(11,2,3,13,6,5)],
 'abandoned_armory':[(1,0,2,15,3,14),(2,3,3,14,5,6),(3,5,3,5,12,12),(10,3,7,14,9,13),(5,3,10,12,6,12)],
 'puzzle_box':[(3,0,3,13,2,13),(4,2,4,12,10,12),(2,5,6,14,8,9),(6,3,2,9,11,14)],
 'battlefield_remnant':[(0,0,0,16,2,16),(3,2,3,4,13,4),(4,9,3,10,13,4),(9,2,7,13,5,13),(6,2,10,7,8,11)],
 'broken_stele':[(2,0,2,14,3,14),(4,3,6,12,10,10),(4,10,6,8,15,10),(8,10,6,10,12,10)],
 'mortuary_room':[(1,0,2,15,3,14),(3,3,3,13,6,13),(4,6,4,12,8,12),(4,8,10,12,10,12)],
 'ghost_market_boat':[(2,0,4,14,2,12),(0,2,4,16,5,6),(0,2,10,16,5,12),(0,2,6,2,5,10),(14,2,6,16,5,10),(7,2,7,9,14,9),(3,9,7,8,14,8)],
 'wayside_tea_stall':[(1,9,1,15,11,15),(2,0,2,4,9,4),(12,0,2,14,9,4),(2,0,12,4,9,14),(12,0,12,14,9,14),(6,11,6,10,14,10),(3,11,4,5,13,6)],
 'old_bellows':[(1,0,3,13,3,13),(2,3,4,12,7,12),(1,7,3,13,9,13),(13,3,7,16,5,9),(2,9,7,7,11,9)],
 'broken_waterwheel':[(0,0,6,16,2,10),(7,2,6,9,15,10),(1,7,6,15,10,10),(3,3,6,6,6,10),(10,11,6,13,14,10),(3,11,6,6,14,10)],
 'ancient_well':[(1,0,1,15,7,4),(1,0,12,15,7,15),(1,0,4,4,7,12),(12,0,4,15,7,12),(1,7,7,3,14,9),(13,7,7,15,14,9),(1,13,7,15,15,9)]}
 elements=[{'from':list(b[:3]),'to':list(b[3:]),'faces':{d:{'texture':'#all'} for d in ['north','south','east','west','up','down']}} for b in shapes[id]]
 write(A/'models/block'/f'{id}.json',{'textures':{'all':texture,'particle':texture},'elements':elements})
 write(A/'models/item'/f'{id}.json',{'parent':'dynasty:block/'+id});write(A/'blockstates'/f'{id}.json',{'variants':{'':{'model':'dynasty:block/'+id}}})
 if id=='wayside_tea_stall':
  overturned=[dict(e,**{'from':[e['from'][0],e['from'][2],16-e['to'][1]],'to':[e['to'][0],e['to'][2],16-e['from'][1]]}) for e in elements]
  write(A/'models/block'/'wayside_tea_stall_overturned.json',{'textures':{'all':texture,'particle':texture},'elements':overturned})
  write(A/'blockstates'/f'{id}.json',{'variants':{'lit=false':{'model':'dynasty:block/'+id},'lit=true':{'model':'dynasty:block/wayside_tea_stall_overturned'}}})
 write(D/'loot_tables/blocks'/f'{id}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+id}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
 write(D/'advancements/cod4'/f'{id}.json',{'criteria':{'code':{'trigger':'minecraft:impossible'}}})
for key,z,e in [('no_ruin','附近未找到遗迹。','No nearby ruin found.'),('site_done','此处调查已完成。','Investigation complete.'),('wait','还需等待 %s 秒。','Wait %s seconds.'),('site_started','开始调查，30秒后继续。','Investigation started; return in 30 seconds.'),('site_progress','调查进度：%s / %s','Investigation: %s / %s')]:zh['message.dynasty.cod4.'+key]=z;en['message.dynasty.cod4.'+key]=e
write(A/'lang/zh_cn.json',zh);write(A/'lang/en_us.json',en)
write(ROOT/'docs/cod4/recipes.json',recipes)
print('Generated 30 rigs, 210 animation states, item/block/effect assets and 27 recipes')
