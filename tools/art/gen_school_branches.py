"""Four real passive weapon branches; declarative recipes and codex inputs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'src/main/resources'
BRANCHES={
 'guard':dict(id='beichen_spear',zh='北辰破阵枪',en='Beichen Spear',base='zhenyue_blade',material='refined_steel',next='juque_sword',next_material='dragon_crystal',
              effect='每点护甲韧性增加0.8%伤害，最多60%。',effect_en='+0.8% damage per armour toughness, up to 60%.'),
 'sword':dict(id='chengying_sword',zh='承影剑',en='Chengying Sword',base='liuyun_sword',material='jade',next='sword_dragon_crystal',next_material='dragon_crystal',
              effect='对生命至少90%的目标增加20%伤害。',effect_en='+20% damage against targets at 90% health or above.'),
 'archer':dict(id='fengling_bow',zh='风翎弓',en='Wind Plume Bow',base='zhuxing_bow',material='refined_steel',next='shenbi_bow',next_material='refined_steel',
              effect='箭矢伤害较逐星弓增加25%，穿透1个目标。',effect_en='+25% arrow damage over Star Bow; pierces one target.'),
 'talisman':dict(id='leifu_staff',zh='雷符杖',en='Thunder Edict Staff',base='chiling_brush',material='jade',next='taiyi_sword',next_material='dragon_crystal',
              effect='伤害增加15%，命中施加3秒缓慢。',effect_en='+15% damage; hits slow targets for 3 seconds.'),
}
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def smithing(base,material,result):
 return {'type':'minecraft:smithing_transform','template':{'item':'dynasty:blueprint'},'base':{'item':'dynasty:'+base},'addition':{'item':'dynasty:'+material},'result':{'item':'dynasty:'+result}}
def main():
 for spec in BRANCHES.values():
  key=spec['id']
  write(RES/f'data/dynasty/recipes/branch_{key}.json',smithing(spec['base'],spec['material'],key))
  write(RES/f'data/dynasty/recipes/branch_{key}_advance.json',smithing(key,spec['next_material'],spec['next']))
  if not key.endswith('_bow'):
   write(RES/f'assets/dynasty/models/item/{key}.json',{'parent':'minecraft:item/handheld','textures':{'layer0':'dynasty:item/'+key}})
 for loc in ('zh_cn','en_us'):
  path=RES/f'assets/dynasty/lang/{loc}.json';lang=json.loads(path.read_text())
  for spec in BRANCHES.values():
   lang['item.dynasty.'+spec['id']]=spec['zh' if loc=='zh_cn' else 'en']
   lang['tooltip.dynasty.branch.'+spec['id']]=spec['effect' if loc=='zh_cn' else 'effect_en']
  write(path,lang)
 # All approved drawn sprites, including Star Bow, point LEFT (-X).
 # Match vanilla's use-item rotations in both hands instead of reusing its diagonal sprite pose.
 display={f'firstperson_{side}':{'rotation':[26.78,yaw,0],
          'translation':[.8,3.2,.8],'scale':[.62,.62,.62]}
          for side,yaw in [('righthand',-76.87),('lefthand',103.13)]}
 for key in ('shenbi_bow','dragon_bow','fengling_bow','chang_gong','zhuxing_bow'):
  overrides=[]
  for stage in range(3):
   predicate={'dynasty:pulling':1}
   if stage: predicate['dynasty:pull']=(.65 if stage==1 else .9)
   overrides.append({'predicate':predicate,'model':f'dynasty:item/{key}_pulling_{stage}'})
   write(RES/f'assets/dynasty/models/item/{key}_pulling_{stage}.json',{'parent':f'minecraft:item/bow_pulling_{stage}','textures':{'layer0':f'dynasty:item/{key}_pulling_{stage}'},'display':display})
  write(RES/f'assets/dynasty/models/item/{key}.json',{'parent':'minecraft:item/bow','textures':{'layer0':'dynasty:item/'+key},'overrides':overrides})
 import subprocess
 subprocess.run(['node',str(ROOT/'tools/art/generate_bow_models.cjs')],check=True)
 subprocess.run(['node',str(ROOT/'tools/art/generate_handheld_edges.cjs')],check=True)
 print('4 branch weapons, 8 evolutions, 6 pixel-preserving bow model sets.')
if __name__=='__main__':main()
