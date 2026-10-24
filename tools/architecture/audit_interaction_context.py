#!/usr/bin/env python3
"""Read-only source/resource evidence for the existing fifteen interaction sites.

This does not execute Java, emulate Forge collision, or approve new buildings.
It measures model cuboids and records source constraints with hashes.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/architecture/continuation-20261022/interaction-context.json'
J = 'src/main/java/com/dynasty/'
R = 'src/main/resources/'
inputs = {}


def read(path):
    raw = (ROOT / path).read_bytes()
    inputs[path] = hashlib.sha256(raw).hexdigest()
    return raw.decode()


def js(path):
    return json.loads(read(path))


def anchor(path, needle):
    source = read(path)
    assert needle in source, (path, needle)
    return {'path': path, 'line': source[:source.index(needle)].count('\n') + 1,
            'text': needle}


def main():
    placement = J + 'structure/TravelSitePiece.java'
    behavior = J + 'expansion/SmallInteractions.java'
    source = read(placement)
    body = re.search(r'String\[\]\[\] sites = (.*?);', source, re.S).group(1)
    groups = [re.findall(r'"([a-z_]+)"', s) for s in re.findall(r'\{([^{}]+)\}', body)]
    assert len(groups) == 3 and all(len(g) == 5 for g in groups)
    sites = ['post_house', 'herbal_retreat', 'desert_caravan']
    rows = []
    zh = js(R+'assets/dynasty/lang/zh_cn.json')
    for style, names in enumerate(groups):
        structure = js(R+f'data/dynasty/worldgen/structure/{sites[style]}.json')
        assert structure['style'] == style
        for index, name in enumerate(names):
            pos = [5+4*index, 1, 28]
            declared = [2, 0, 2, 14, 5 if name == 'herb_spot' else 13, 14]
            state = js(R+f'assets/dynasty/blockstates/{name}.json')
            variants = []
            for condition, value in state['variants'].items():
                for spec in value if isinstance(value, list) else [value]:
                    assert not spec.get('x') and not spec.get('y'), 'Rotation requires explicit transform'
                    ns, model = spec['model'].split(':')
                    data = js(R+f'assets/{ns}/models/{model}.json')
                    elements = data['elements']
                    assert all('rotation' not in e for e in elements), 'Rotated cuboid needs transform'
                    lo = [min(e['from'][a] for e in elements) for a in range(3)]
                    hi = [max(e['to'][a] for e in elements) for a in range(3)]
                    outside = [i for i,e in enumerate(elements) if any(
                        e['from'][a]<declared[a] or e['to'][a]>declared[a+3] for a in range(3))]
                    variants.append({'condition':condition,'model':spec['model'],
                        'model_bounds_pixels':[lo,hi],
                        'scene_local_bounds_blocks':[[pos[a]+v[a]/16 for a in range(3)] for v in (lo,hi)],
                        'cuboids_outside_declared_outline':outside,
                        'within_single_block_cell':all(0<=lo[a]<=hi[a]<=16 for a in range(3))})
            # Only the clear generated strip z=27..28 is assessed. No full-world path claim.
            rows.append({'id':name,'title_zh':zh.get('block.dynasty.'+name),
                'site':sites[style],'style':style,'piece_local_position':pos,
                'variants':variants,'declared_outline_pixels':declared,
                'approach_candidate_local':[pos[0],1,27],
                'approach_status':'SOURCE_CLEAR_STRIP_ONLY; native support, reach and collision pending',
                'nearby_low_boundary_local_z':29,
                'runtime_collision_status':'NOT_EXECUTED'})
    mob_rows=[]
    for mob in ('corpse_beetle','crab_soldier','lantern_ghost','night_watchman'):
        mob_rows.append({'id':mob,
            'biome_modifier':js(R+f'data/dynasty/forge/biome_modifier/secondary_{mob}.json'),
            'biome_tag':js(R+f'data/dynasty/tags/worldgen/biome/secondary/{mob}.json'),
            'loot':js(R+f'data/dynasty/loot_tables/entities/{mob}.json')})
    tags={n:js(R+f'data/dynasty/tags/worldgen/structure/{n}.json') for n in (
        'ecology/tombs','blueprint/ghost_sites','secondary/ruins','ecology/roads','blueprint/military_sites')}
    findings=[
        {'id':'PLACEMENT_STRIP','status':'SOURCE_CONFIRMED','detail_zh':'15个互动均在三个院落的z28行，间隔4格；北侧局部z27可作接近候选。模型均限制在单个格内，不能把形状差异描述成邻近模型互穿。真实地形、玩家走位与视线仍待原生核查。',
         'anchors':[anchor(placement,'set(l,b,5+i*4,1,28,'),anchor(placement,'fill(l,b,0,1,0,30,11,30,Blocks.AIR'),anchor(placement,'walls(l,b,1,1,1,29,1,29,brick)')]},
        {'id':'OUTLINE_NOT_COLLISION','status':'NATIVE_PENDING','detail_zh':'Site只声明getShape，未声明专用getCollisionShape；noOcclusion不应直接解释为无碰撞。所有状态都使用同一声明形状，包括茶摊翻倒、水车修复状态。不得把JSON模型外包围盒直接替换成完整碰撞盒。',
         'anchors':[anchor(behavior,'Site(String id)'),anchor(behavior,'@Override public VoxelShape getShape')]},
        {'id':'SCENE_NPCS','status':'SOURCE_GUARDS_PRESENT_NATIVE_PENDING','detail_zh':'鬼船商人、茶摊商人及义庄病人尝试四向1至2格位置，并检查已加载区块、世界边界、地面承托、noCollision及实体加入。z29低墙及药庐z26水沟使某些方向不可用，但这不能证明所有候选都失败；局部z27仍有候选。方向循环在世界坐标运行，不可把局部北向视为实际第一个尝试。',
         'anchors':[anchor(behavior,'private static com.dynasty.cod3.DynastyNpcEntity sceneMerchant'),anchor(behavior,'private static com.dynasty.cod3.DynastyNpcEntity mortuaryVictim'),anchor(behavior,'if(level.noCollision(npc,npc.getBoundingBox())&&level.addFreshEntity(npc))return npc;')]},
        {'id':'BELLOWS_FURNACE','status':'SOURCE_PLACEMENT_WITHIN_SEARCH','detail_zh':'沙漠院落风箱(17,1,28)与熔炉(17,1,26)相距2格，在assistFurnace的±3水平范围内。空炉并非可工作配方：还须放入有效原料、留出产物空间并满足燃烧上限；不能把等待原料当作风箱离熔炉过远。',
         'anchors':[anchor(placement,'set(l,b,17,1,26,Blocks.FURNACE'),anchor(behavior,'BlockPos.betweenClosed(site.offset(-3,-1,-3),site.offset(3,2,3))'),anchor(behavior,'if(recipe==null||furnace.getItem(0).isEmpty())continue;')]},
        {'id':'MORTUARY_ECOLOGY','status':'SCENE_AND_NATIVE_ACCEPTANCE_PENDING','detail_zh':'药庐的无名墓/义庄方块没有把药庐自动加入ecology/tombs；该标签列出imperial_tomb与chensha_xuangong。尸虫另有低光洞穴路径，不能报告为无法获得。灯笼鬼走ghost_sites/ruins，夜间更夫走roads/military_sites；材料可达性需结合这些真实地点，不只在互动方块旁测试。',
         'anchors':[anchor(J+'expansion/SecondarySpawnHooks.java','if(id.equals("corpse_beetle")'),anchor(J+'expansion/SecondarySpawnHooks.java','case "famished_refugee","lantern_ghost"'),anchor(J+'expansion/SecondarySpawnHooks.java','case "night_watchman"')]}
    ]
    report={'status':'READ_ONLY_SOURCE_REVIEW_NATIVE_PENDING','java_executed':False,
        'runtime_resources_changed':False,'references_added':0,'checklist_deleted':[],
        'coordinate_system':'piece-local; do not use as world coordinates without StructurePiece transform',
        'interactions':rows,'material_mobs':mob_rows,'ecology_tags':tags,'findings':findings,
        'input_sha256':inputs}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sites':len(rows),'variants':sum(len(r['variants']) for r in rows),
        'findings':len(findings),'report':str(OUT)},ensure_ascii=False))


if __name__ == '__main__':
    main()
