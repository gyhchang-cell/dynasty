#!/usr/bin/env python3
"""Editable original16px platform, drops and native world data; no runtime mutation."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'src/main/resources/data'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
# Block models sample only uniform UV material islands, never the white atlas margin.
colors=['#583E36','#9B8354','#624071','#FFFFFF'];islands=[[3,3,7,7],[9,3,13,7],[3,9,7,13]]
def faces(i):return {f:{'texture':'#all','uv':islands[i]} for f in ('up','down','north','south','west','east')}
def element(lo,hi,i):return {'from':lo,'to':hi,'faces':faces(i)}
blocks={'stargazer_mortise_plank':[element([0,0,0],[16,16,7],0),element([0,0,7],[16,16,9],1),element([0,0,9],[16,16,16],0)],'stargazer_charred_plank':[element([0,0,0],[16,16,16],2)],'stargazer_core_socket':[element([0,0,0],[16,12,16],0),element([0,12,0],[16,16,16],1),element([4,16,4],[12,18,12],2)],'stargazer_gear_rope':[element([3,0,7],[5,16,9],1),element([11,0,7],[13,16,9],1)]+[element([5,y,7],[11,y+2,9],0) for y in (2,8,14)]}
for name,els in blocks.items():
 im=Image.new('RGB',(16,16),'white');draw=ImageDraw.Draw(im)
 for col,uv in zip(colors,islands):draw.rectangle([uv[0],uv[1],uv[2]-1,uv[3]-1],fill=col)
 path=A/f'textures/block/{name}.png';path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
 write(A/f'blockstates/{name}.json',{'variants':{'':{'model':'dynasty:block/'+name}}})
 write(A/f'models/block/{name}.json',{'textures':{'all':'dynasty:block/'+name,'particle':'dynasty:block/'+name},'elements':els})
 write(A/f'models/item/{name}.json',{'parent':'dynasty:block/'+name})
 write(D/f'dynasty/loot_tables/blocks/{name}.json',{'type':'minecraft:block','pools':([] if name=='stargazer_core_socket' else [{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+name}],'conditions':[{'condition':'minecraft:survives_explosion'}]}])})
# Original six-by-six coarse silhouettes with actual2px pixels/white margin.
icons={'stargazer_kite_core_mechanism':['  BB  ',' BCCB ','BCCCBW','BCCCBB',' BCCB ','  BB  '],'stargazer_cinnabar_wood_feather':['   WW ','  WBW ',' WBWB ','WBWB  ','BWB   ','BB    '],'luban_clockwork_diagram_page':[' BBBB ',' BWWB ',' BWCB ',' BCWB ',' BWWB ',' BBBB ']}
for name,rows in icons.items():
 im=Image.new('RGB',(16,16),'white');draw=ImageDraw.Draw(im)
 for y,row in enumerate(rows):
  for x,ch in enumerate(row):
   if ch!=' ':draw.rectangle((2+x*2,2+y*2,3+x*2,3+y*2),fill={'B':colors[1],'C':colors[2],'W':colors[0]}[ch])
 path=A/f'textures/item/{name}.png';path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
 write(A/f'models/item/{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+name}})
write(A/'models/item/luban_yisha_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
# Additive tags preserve concurrent and vanilla entries.
for name,ids in {'climbable':['dynasty:stargazer_gear_rope'],'mineable/axe':['dynasty:stargazer_mortise_plank','dynasty:stargazer_charred_plank','dynasty:stargazer_gear_rope']}.items():
 path=D/f'minecraft/tags/blocks/{name}.json';obj=json.loads(path.read_text()) if path.exists() else {'replace':False,'values':[]};assert not obj.get('replace',False);obj['values']=list(dict.fromkeys(obj['values']+ids));write(path,obj)
write(D/'dynasty/recipes/stargazer_gear_rope.json',{'type':'minecraft:crafting_shaped','category':'misc','pattern':['SSS','SPS','SSS'],'key':{'S':{'item':'minecraft:string'},'P':{'item':'dynasty:luban_clockwork_diagram_page'}},'result':{'item':'dynasty:stargazer_gear_rope','count':16}})
write(D/'dynasty/advancements/recipes/decorations/stargazer_gear_rope.json',{'parent':'minecraft:recipes/root','criteria':{'has_page':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':['dynasty:luban_clockwork_diagram_page']}]}},'has_the_recipe':{'trigger':'minecraft:recipe_unlocked','conditions':{'recipe':'dynasty:stargazer_gear_rope'}}},'requirements':[['has_page','has_the_recipe']],'rewards':{'recipes':['dynasty:stargazer_gear_rope']}})
pools=[]
for name,lo,hi in [('stargazer_kite_core_mechanism',1,2),('stargazer_cinnabar_wood_feather',3,6),('luban_clockwork_diagram_page',1,1)]:
 entry={'type':'minecraft:item','name':'dynasty:'+name}
 if hi>1:entry['functions']=[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':lo,'max':hi}}]
 pools.append({'rolls':1,'entries':[entry]})
write(D/'dynasty/loot_tables/entities/luban_yisha.json',{'type':'minecraft:entity','pools':pools})
write(D/'dynasty/advancements/blueprint/defeat_luban_yisha.json',{'criteria':{'defeat':{'trigger':'minecraft:player_killed_entity','conditions':{'entity':{'type':'dynasty:luban_yisha'}}}}})
biomes=['minecraft:plains','minecraft:savanna','minecraft:windswept_hills','minecraft:windswept_forest']
write(D/'dynasty/worldgen/structure/stargazer_platform.json',{'type':'dynasty:stargazer_platform','biomes':biomes,'step':'surface_structures','terrain_adaptation':'none','spawn_overrides':{}})
write(D/'dynasty/worldgen/structure_set/stargazer_platform.json',{'structures':[{'structure':'dynasty:stargazer_platform','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':56,'separation':28,'salt':18374922}})
write(D/'dynasty/tags/worldgen/structure/blueprint/kite_sites.json',{'replace':False,'values':['dynasty:stargazer_platform']})
write(D/'dynasty/tags/worldgen/biome/has_structure/stargazer_platform.json',{'replace':False,'values':biomes})
zh={'entity.dynasty.luban_yisha':'九霄木鸢·鲁班遗煞','entity.dynasty.wood_kite_thunder_bomb':'木鸢雷煞飞火弹','item.dynasty.luban_yisha_spawn_egg':'九霄木鸢刷怪蛋','item.dynasty.stargazer_kite_core_mechanism':'天枢木鸢核心机括','item.dynasty.stargazer_cinnabar_wood_feather':'极韧朱砂木羽片','item.dynasty.luban_clockwork_diagram_page':'鲁班天工机关图残页','block.dynasty.stargazer_mortise_plank':'摘星台榫卯木板','block.dynasty.stargazer_charred_plank':'烧蚀摘星木板','block.dynasty.stargazer_core_socket':'天枢引鸢机关座','block.dynasty.stargazer_gear_rope':'机关通天绳梯','tooltip.dynasty.stargazer_kite_core_mechanism':'右键修复另一只手上的装备180点耐久，消耗一个机括。','tooltip.dynasty.stargazer_cinnabar_wood_feather':'右键获得6秒缓降，消耗一片木羽。','tooltip.dynasty.luban_clockwork_diagram_page':'与八束线合成16节可攀爬的机关绳梯。','message.dynasty.stargazer_platform':'从边缘绳梯登台，空手触动中央机关座。落雷烧木，木柱可挡罡风；流星落地前半秒起跳。'}
en={'entity.dynasty.luban_yisha':'Wood Kite · Luban\'s Remnant','entity.dynasty.wood_kite_thunder_bomb':'Wood Kite Thunder Bomb','item.dynasty.luban_yisha_spawn_egg':'Wood Kite Spawn Egg','item.dynasty.stargazer_kite_core_mechanism':'Stargazer Kite Core Mechanism','item.dynasty.stargazer_cinnabar_wood_feather':'Resilient Cinnabar Wood Feather','item.dynasty.luban_clockwork_diagram_page':'Luban Clockwork Diagram Page','block.dynasty.stargazer_mortise_plank':'Stargazer Mortise Plank','block.dynasty.stargazer_charred_plank':'Charred Stargazer Plank','block.dynasty.stargazer_core_socket':'Stargazer Kite Socket','block.dynasty.stargazer_gear_rope':'Clockwork Rope Ladder','tooltip.dynasty.stargazer_kite_core_mechanism':'Use to repair 180 durability on equipment in the other hand. Consumes one core.','tooltip.dynasty.stargazer_cinnabar_wood_feather':'Use for six seconds of Slow Falling. Consumes one feather.','tooltip.dynasty.luban_clockwork_diagram_page':'Craft with eight strings to make 16 climbable clockwork rope ladders.','message.dynasty.stargazer_platform':'Climb the outer rope and touch the central socket with an empty hand. Columns block wind; lightning burns planks. Jump half a second before meteor impact.'}
for loc,addition in [('zh_cn',zh),('en_us',en)]:
 path=A/f'lang/{loc}.json';obj=json.loads(path.read_text());obj.update(addition);write(path,obj)
for name in [*icons,*blocks]:
 im=Image.open(A/(f'textures/item/{name}.png' if name in icons else f'textures/block/{name}.png'));assert im.size==(16,16) and len(set(im.get_flattened_data()))<=4
 for y in range(16):
  for x in range(16):
   col=im.getpixel((x,y));assert 2<=x<=13 and 2<=y<=13 or col==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==col for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15)
print('Exported native platform, climbable ropes, functional drops, loot, first-arrival structure and localized16px assets')

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()
