"""Generate native block models and matching collision geometry from one definition.
No raster drawing, no instance or save writes. Run from any directory.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources'
ASSET = RES / 'assets/dynasty'
DATA = RES / 'data/dynasty'

def cub(x1,y1,z1,x2,y2,z2,tex='all'):
    return ([x1,y1,z1], [x2,y2,z2], tex)

def basin(low,high,tex='all'):
    # Solid bottom and four walls, genuinely empty above the bottom.
    return [cub(1,1,1,15,low,15,tex),cub(1,low,1,3,high,15,tex),
            cub(13,low,1,15,high,15,tex),cub(3,low,1,13,high,3,tex),cub(3,low,13,13,high,15,tex)]

def legs(height,tex='all'):
    return [cub(x,0,z,x+3,height,z+3,tex) for x in (1,12) for z in (1,12)]

# kind, registry id, localized names, textures, exact occupied cuboids
WORKSHOPS = [
 ('MARROW','marrow_vat','化髓槽','Marrow Vat',{'all':'dynasty:block/marrow_vat'},basin(3,14)),
 ('ESSENCE','essence_condenser','凝灵器','Essence Condenser',{'all':'dynasty:block/essence_condenser','crystal':'minecraft:block/amethyst_block'},
  [cub(1,0,1,15,3,15),cub(5,3,5,11,5,11),cub(6,5,6,10,13,10,'crystal'),cub(4,13,4,12,15,12)]),
 ('REPAIR','jade_mending_forge','玉髓修补炉','Jade Mending Forge',{'all':'dynasty:block/jade_mending_forge'},
  [cub(1,0,2,15,3,14),cub(5,3,5,11,10,11),cub(0,10,2,16,14,14)]),
 ('VITALITY','vitality_shrine','养元龛','Vitality Shrine',{'all':'dynasty:block/vitality_shrine','wood':'dynasty:block/crimson_pillar_side','jade':'dynasty:block/jade_block'},
  [cub(1,0,2,15,3,15),cub(1,3,12,15,14,15,'wood'),cub(1,3,2,4,12,12),cub(12,3,2,15,12,12),cub(0,12,1,16,15,16),cub(6,3,7,10,8,11,'jade')]),
 ('HIDE','hide_stretcher','制革架','Hide Stretcher',{'all':'dynasty:block/crimson_pillar_side','hide':'minecraft:block/brown_terracotta'},
  [cub(1,0,2,4,2,14),cub(12,0,2,15,2,14),cub(1,2,6,3,16,9),cub(13,2,6,15,16,9),cub(3,13,6,13,16,9),cub(3,3,6,13,5,9),cub(4,5,7,12,13,8,'hide')]),
 ('HERBAL','herbal_basin','药浴盆','Herbal Basin',{'all':'dynasty:block/marble_block','band':'dynasty:block/jade_block'},
  basin(3,9)+[cub(0,7,0,16,10,3,'band'),cub(0,7,13,16,10,16,'band'),cub(0,7,3,3,10,13,'band'),cub(13,7,3,16,10,13,'band')]),
 ('LAPIDARY','lapidary_bench','琢玉台','Lapidary Bench',{'all':'dynasty:block/crimson_pillar_side','stone':'dynasty:block/palace_bricks','jade':'dynasty:block/jade_block'},
  legs(9)+[cub(0,9,0,16,12,16,'stone'),cub(6,12,6,10,15,10,'jade'),cub(1,5,7,15,7,9)]),
 ('EMBER','ember_brazier','御火盆','Ember Brazier',{'all':'dynasty:block/bronze_block','coal':'minecraft:block/coal_block'},
  legs(4)+[cub(2,4,2,14,6,14,'coal'),cub(1,4,1,3,11,15),cub(13,4,1,15,11,15),cub(3,4,1,13,11,3),cub(3,4,13,13,11,15)])
]

NEW = {
 'hide_stretcher': ('HIDE',['SLS','SBS','S S'],{'S':'minecraft:stick','L':'minecraft:leather','B':'minecraft:bone'}),
 'herbal_basin': ('HERBAL',['S S','SJS','SSS'],{'S':'minecraft:smooth_stone','J':'dynasty:jade'}),
 'lapidary_bench': ('LAPIDARY',['SSS','PAP','P P'],{'S':'minecraft:stone_slab','P':'minecraft:oak_planks','A':'minecraft:amethyst_shard'}),
 'ember_brazier': ('EMBER',['I I','ICI','B B'],{'I':'minecraft:iron_ingot','C':'minecraft:charcoal','B':'minecraft:brick'})
}

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def generate():
    java=[]
    for kind,id,zh,en,textures,boxes in WORKSHOPS:
        elements=[{'from':a,'to':b,'faces':{f:{'texture':'#'+t} for f in ('north','south','east','west','up','down')}} for a,b,t in boxes]
        # block/block supplies the standard three-dimensional inventory display transforms.
        write(ASSET/'models/block'/f'{id}.json',{'parent':'minecraft:block/block','textures':{**textures,'particle':textures['all']},'elements':elements})
        write(ASSET/'models/item'/f'{id}.json',{'parent':f'dynasty:block/{id}'})
        write(ASSET/'blockstates'/f'{id}.json',{'variants':{
            f'facing={f},lit={lit}':{'model':f'dynasty:block/{id}',**({'y':y} if y else {})}
            for f,y in [('north',0),('east',90),('south',180),('west',270)] for lit in ('true','false')}})
        cuboids=', '.join('Block.box('+','.join(map(str,a+b))+')' for a,b,_ in boxes)
        java.append(f'        SHAPES.put(LivingWorkshopBlock.Kind.{kind}, rotations(Shapes.or({cuboids})));')
    (ROOT/'src/main/java/com/dynasty/block/WorkshopShapes.java').write_text('''package com.dynasty.block;

import java.util.EnumMap;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Generated with the JSON models by tools/art/workshop_assets_v9.py. */
final class WorkshopShapes {
    private static final EnumMap<LivingWorkshopBlock.Kind,VoxelShape[]> SHAPES = new EnumMap<>(LivingWorkshopBlock.Kind.class);
    static {
'''+ '\n'.join(java)+'''
    }
    private static VoxelShape[] rotations(VoxelShape north) {
        VoxelShape[] shapes=new VoxelShape[4]; shapes[0]=north.optimize();
        for(int i=1;i<4;i++) {
            final VoxelShape[] next={Shapes.empty()};
            shapes[i-1].forAllBoxes((x1,y1,z1,x2,y2,z2) ->
                next[0]=Shapes.or(next[0],Shapes.box(1-z2,y1,x1,1-z1,y2,x2)));
            shapes[i]=next[0].optimize();
        }
        return shapes;
    }
    static VoxelShape get(LivingWorkshopBlock.Kind kind,Direction facing) {
        int index=switch(facing) {case EAST -> 1; case SOUTH -> 2; case WEST -> 3; default -> 0;};
        return SHAPES.get(kind)[index];
    }
}
''')
    for id,(_,pattern,ingredients) in NEW.items():
        write(DATA/'recipes'/f'{id}.json',{'type':'minecraft:crafting_shaped','pattern':pattern,'key':{k:{'item':v} for k,v in ingredients.items()},'result':{'item':f'dynasty:{id}'}})
        write(DATA/'loot_tables/blocks'/f'{id}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':f'dynasty:{id}'}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
    mine=RES/'data/minecraft/tags/blocks/mineable/pickaxe.json'
    content=json.loads(mine.read_text()) if mine.exists() else {'replace':False,'values':[]}
    content['values']=list(dict.fromkeys(content['values']+[f'dynasty:{w[1]}' for w in WORKSHOPS]))
    write(mine,content)
    translations={
      'zh_cn':{
        'hide.guide':'右键：腐肉×8 + 骨粉×2 → 皮革×2。材料放背包，冷却1秒。潜行右键查看说明。',
        'hide.done':'制革完成：皮革×2。',
        'herbal.guide':'右键：小麦×4 + 糖×2 + 海带×2，解除中毒并获得5秒生命恢复I。冷却30秒；满血且未中毒不消耗。',
        'herbal.done':'药浴完成：解除中毒，生命恢复5秒。','herbal.full':'当前满血且未中毒，不消耗材料。',
        'lapidary.guide':'右键：紫水晶碎片×4 + 下界石英×4 → 玉×1。材料放背包，冷却1秒。潜行右键查看说明。',
        'lapidary.done':'琢玉完成：玉×1。',
        'ember.guide':'右键：木炭×2 + 烈焰粉×1，获得2分钟抗火I。个人冷却30秒。潜行右键查看说明。',
        'ember.done':'御火完成：抗火2分钟。'},
      'en_us':{
        'hide.guide':'Right-click: 8 rotten flesh + 2 bone meal -> 2 leather. Keep materials in inventory. 1s cooldown. Sneak-right-click for help.',
        'hide.done':'Produced 2 leather.',
        'herbal.guide':'Right-click: 4 wheat + 2 sugar + 2 kelp to cure Poison and gain Regeneration I for 5s. 30s cooldown. Free if healthy and not poisoned.',
        'herbal.done':'Poison cured. Regeneration for 5 seconds.','herbal.full':'Already healthy and not poisoned. No materials consumed.',
        'lapidary.guide':'Right-click: 4 amethyst shards + 4 nether quartz -> 1 jade. Keep materials in inventory. 1s cooldown. Sneak-right-click for help.',
        'lapidary.done':'Produced 1 jade.',
        'ember.guide':'Right-click: 2 charcoal + 1 blaze powder for Fire Resistance I for 2 minutes. Personal cooldown: 30s. Sneak-right-click for help.',
        'ember.done':'Fire Resistance for 2 minutes.'}}
    for lang,entries in translations.items():
        p=ASSET/'lang'/f'{lang}.json'; data=json.loads(p.read_text())
        # Legacy transaction descriptions are deliberately not regenerated.
        for key in list(data):
            if key.startswith('workshop.dynasty.') and key != 'workshop.dynasty.next': del data[key]
        for _,id,zh,en,_,_ in WORKSHOPS:
            data[f'block.dynasty.{id}']=zh if lang=='zh_cn' else en
        write(p,data)
    print('8 matched model/collision layouts, 4 new recipes/drops, languages; no save or instance writes.')

if __name__=='__main__':generate()
