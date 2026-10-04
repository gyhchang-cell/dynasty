"""Reproducible workstation resources. No saves, worldgen, or deployment writes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'src/main/resources'
STATIONS={
 'marrow_vat':('化髓槽','Marrow Vat','marrow','minecraft:bone_block','minecraft:rotten_flesh',
 '右键：腐肉×8 → 骨粉×4；材料放背包。潜行右键查看说明。','Right-click: 8 rotten flesh → 4 bone meal. Materials in inventory. Sneak-use for help.',
 '已化髓：骨粉×4。','Produced 4 bone meal.'),
 'essence_condenser':('凝灵器','Essence Condenser','essence','minecraft:amethyst_block','dynasty:jade',
 '右键：紫水晶碎片×4 + 骨粉×4 → 附魔之瓶×1；潜行右键查看说明。','Right-click: 4 amethyst shards + 4 bone meal → 1 experience bottle. Sneak-use for help.',
 '已凝灵：附魔之瓶×1。','Produced 1 experience bottle.'),
 'jade_mending_forge':('玉髓修补炉','Jade Mending Forge','repair','minecraft:anvil','dynasty:jade',
 '主手拿受损装备，右键：玉×2 + 铁锭×4，修复最大耐久的25%；保留附魔和淬炼。','Hold damaged gear and use: 2 jade + 4 iron ingots repairs 25% max durability. Keeps all gear data.',
 '修补完成，附魔和淬炼保留。','Repaired. Enchantments and refining preserved.'),
 'vitality_shrine':('养元龛','Vitality Shrine','vitality','minecraft:honey_block','dynasty:jade',
 '右键：蜂蜜瓶×1，恢复6点生命，返还玻璃瓶；个人冷却30秒，满血不消耗。','Use: 1 honey bottle restores 6 health and returns a bottle. 30s personal cooldown. No cost at full health.',
 '养元完成，恢复6点生命。','Restored up to 6 health.'),
}
def write(path,obj):
 p=RES/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def names():
 zh={'workshop.dynasty.cooldown':'还需等待%s秒。','workshop.dynasty.repair.hold':'请主手拿着需要修复的装备。','workshop.dynasty.vitality.full':'生命已满，不消耗材料。'}
 en={'workshop.dynasty.cooldown':'Wait %s seconds.','workshop.dynasty.repair.hold':'Hold a damaged item in your main hand.','workshop.dynasty.vitality.full':'Already at full health. No materials consumed.'}
 for id,(cn,eng,key,_,__,guide,eg,done,ed) in STATIONS.items():
  zh['block.dynasty.'+id]=cn;en['block.dynasty.'+id]=eng
  zh['workshop.dynasty.'+key+'.guide']=guide;en['workshop.dynasty.'+key+'.guide']=eg
  zh['workshop.dynasty.'+key+'.done']=done;en['workshop.dynasty.'+key+'.done']=ed
 return {'zh_cn':zh,'en_us':en}
def merge_lang():
 for lang,entries in names().items():
  p=RES/f'assets/dynasty/lang/{lang}.json';data=json.loads(p.read_text());data.update(entries);write(f'assets/dynasty/lang/{lang}.json',data)
def main():
 raise SystemExit('Retired bulk-transaction generator. Use workshop_assets_v9.py for shapes, then generate_workshop_assets.mjs for current items/text. Recipes live in WorkshopRecipes.java.')
 for id,(_,__,key,base,core,*_) in STATIONS.items():
  write(f'assets/dynasty/blockstates/{id}.json',{'variants':{'lit=false':{'model':'dynasty:block/'+id},'lit=true':{'model':'dynasty:block/'+id}}})
  # Stepped base, housing and rim: deliberately recognizable workstation shapes, not solid cubes.
  boxes={'marrow':[((0,0,0),(16,3,16)),((2,3,2),(14,11,14)),((0,11,0),(16,14,3)),((0,11,13),(16,14,16)),((0,11,3),(3,14,13)),((13,11,3),(16,14,13))],
   'essence':[((1,0,1),(15,3,15)),((3,3,3),(13,12,13)),((5,12,5),(11,16,11))],
   'repair':[((0,0,0),(16,3,16)),((3,3,3),(13,10,13)),((0,10,1),(16,14,15))],
   'vitality':[((0,0,0),(16,3,16)),((3,3,3),(13,11,13)),((1,11,1),(15,14,15)),((5,14,5),(11,16,11))]}[key]
  faces={d:{'texture':'#all'} for d in ('up','down','north','south','east','west')}
  write(f'assets/dynasty/models/block/{id}.json',{'textures':{'all':'dynasty:block/'+id,'particle':'dynasty:block/'+id},'elements':[{'from':a,'to':b,'faces':faces} for a,b in boxes]})
  write(f'assets/dynasty/models/item/{id}.json',{'parent':'dynasty:block/'+id})
  write(f'data/dynasty/recipes/{id}.json',{'type':'minecraft:crafting_shaped','pattern':['SCS','SBS','SSS'],'key':{'S':{'item':'minecraft:stone_bricks'},'C':{'item':core},'B':{'item':base}},'result':{'item':'dynasty:'+id}})
  write(f'data/dynasty/loot_tables/blocks/{id}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+id}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
 p=RES/'data/minecraft/tags/blocks/mineable/pickaxe.json';data=json.loads(p.read_text()) if p.exists() else {'replace':False,'values':[]}
 data['values']=list(dict.fromkeys(data['values']+['dynasty:'+id for id in STATIONS]));write('data/minecraft/tags/blocks/mineable/pickaxe.json',data)
 merge_lang();print('Generated 4 interactive workstation resource sets')
if __name__=='__main__':main()
