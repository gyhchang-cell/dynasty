#!/usr/bin/env python3
"""Audit existing architectural resources offline; never launch Java or edit assets.

Measurements of NBT are exact. Walkability is a conservative full-cell model in
an otherwise empty template volume, not Forge collision or terrain validation.
"""
import hashlib
import json
import re
from collections import Counter, deque
from pathlib import Path

from nbt_read import read

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/architecture/continuation-20261022'
RES=ROOT/'src/main/resources'
JAVA=ROOT/'src/main/java/com/dynasty'
INPUTS={}


def load(path, binary=False):
    path=Path(path)
    raw=path.read_bytes(); INPUTS[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
    return raw if binary else raw.decode()


def js(path): return json.loads(load(path))


def source_anchor(path, text):
    data=load(path); offset=data.find(text)
    if offset<0: raise ValueError(f'Changed source: {path}: {text}')
    return {'path':str(path.relative_to(ROOT)),'line':data[:offset].count('\n')+1,'text':text}


def minerals_and_routes():
    path=RES/'data/dynasty/structures/tiangong_mining_estate.nbt'
    nbt=read(load(path,True)); palette=nbt['palette']
    blocks={tuple(b['pos']):palette[b['state']]['Name'] for b in nbt['blocks']}
    if len(blocks)!=len(nbt['blocks']): raise ValueError('Duplicate mining coordinates')
    ore=lambda n:n.startswith('minecraft:raw_') and n.endswith('_block') or n.endswith('_ore')
    expected=set()
    for tier in range(3):
        height=3+tier*3; z0=14+tier*18
        for x in range(10,39):
            for z in range(z0,z0+13):
                for y in range(1,height+1): expected.update(((x,y,z),(95-x,y,z)))
    benches=len(expected)
    for y in range(1,7):
        for x in range(10+y,39-y):
            for z in range(70+y,88-y): expected.update(((x,y,z),(95-x,y,z)))
    missing=[p for p in expected if not ore(blocks.get(p,''))]
    actual={p for p,n in blocks.items() if ore(n)}
    mismatches=[p for p in actual if blocks.get((95-p[0],p[1],p[2]))!=blocks[p]]
    stand={(x,y+1,z) for (x,y,z),name in blocks.items()
           if name not in ('minecraft:air','minecraft:lantern') and y+2<nbt['size'][1]
           and (x,y+1,z) not in blocks and (x,y+2,z) not in blocks}
    start=(47,1,4); seen={start}; q=deque([start])
    while q:
        x,y,z=q.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (-1,0,1):
                p=(x+dx,y+dy,z+dz)
                if p not in stand or p in seen: continue
                if dy==1 and (x,y+2,z) in blocks: continue
                if dy==-1 and (p[0],p[1]+2,p[2]) in blocks: continue
                seen.add(p); q.append(p)
    targets=[(47,1,90),(40,1,65),(55,1,65),(24,4,16),(71,10,59)]
    chest_rows=[]
    for b in nbt['blocks']:
        if palette[b['state']]['Name']!='minecraft:chest': continue
        items=b.get('nbt',{}).get('Items',[])
        chest_rows.append(dict(position=b['pos'],occupied_slots=len(items),
            unique_slots=len({i['Slot'] for i in items}),items=items))
    gallery=[((10,6,64),'minecraft:smooth_stone'),((85,6,68),'minecraft:smooth_stone')]
    gallery_air=[(24,4,66),(71,4,66),(38,2,66),(57,2,66)]
    result=dict(size=nbt['size'],explicit_blocks=len(blocks),
        mineral_cells=len(actual),expected_bench_cells=benches,expected_former_hall_mound_cells=len(expected)-benches,
        missing_minerals=missing,extra_minerals=list(actual-expected),mirror_mismatches=mismatches,
        raw_block_fraction=sum(n.startswith('minecraft:raw_') for n in blocks.values())/len(actual),
        chests=chest_rows,explicit_air=sum(n.endswith(':air') for n in blocks.values()),
        template_omits_air=True,
        routes=[dict(target=t,reachable=t in seen) for t in targets],
        geometric_reachable_stands=len(seen),
        galleries_have_v6_anchors=all(blocks.get(p)==n for p,n in gallery) and all(p not in blocks for p in gallery_air),
        anchors=[source_anchor(JAVA/'structure/megabuild/MegabuildPiece.java','private int layoutVersion=6;'),
                 source_anchor(JAVA/'structure/megabuild/MegabuildStructures.java','return new MiningEstate(seed).blueprint();'),
                 source_anchor(JAVA/'structure/megabuild/MegabuildTemplateExport.java','if(k==Blueprint.Kind.AIR)continue;')],
        status='STATIC_GEOMETRY_ONLY',native_status='PENDING',natural_manual_equivalence='v6 geometric anchors agree; terrain/air placement differs and remains pending')
    render_mine(blocks)
    return result


def render_mine(blocks):
    from PIL import Image,ImageDraw
    def color(n):
        if n.endswith('_ore') or n.startswith('minecraft:raw_'): return '#a7864b'
        return {'minecraft:chest':'#f59e0b','minecraft:smooth_stone':'#cbd5e1','minecraft:stone_bricks':'#64748b','minecraft:deepslate_bricks':'#334155'}.get(n,'#15803d')
    overview=Image.new('RGB',(768,800),'white'); draw=ImageDraw.Draw(overview)
    for x in range(96):
        for z in range(96):
            ys=[y for y in range(36) if (x,y,z) in blocks]
            if ys: draw.rectangle((x*8,32+z*8,x*8+7,39+z*8),fill=color(blocks[x,max(ys),z]))
    draw.text((6,8),'CURRENT MINING NBT - TOP / z increases down / gold = minerals',fill='black')
    overview.save(OUT/'mining-top.png')
    img=Image.new('RGB',(1000,980),'white'); d=ImageDraw.Draw(img)
    slices=[('Z',20),('Z',38),('Z',56),('Z',66),('Z',78),('X',24),('X',71)]
    for i,(axis,v) in enumerate(slices):
        top=25+i*135; d.text((10,top-15),f'{axis}={v} / real NBT / white = omitted (not explicit air)',fill='black')
        for a in range(96):
            for y in range(12):
                pos=(a,y,v) if axis=='Z' else (v,y,a)
                if pos in blocks: d.rectangle((15+a*10,top+(11-y)*9,24+a*10,top+(12-y)*9-1),fill=color(blocks[pos]))
    img.save(OUT/'mining-sections.png')


def interactions():
    source=load(JAVA/'expansion/SmallInteractions.java')
    ids=re.findall(r'"([a-z_]+)"',re.search(r'IDS=List.of\((.*?)\);',source).group(1))
    zh=js(RES/'assets/dynasty/lang/zh_cn.json'); rows=[]
    groups=[('post_house',['wayside_shrine','old_weapon_rack','puzzle_box','wayside_tea_stall','broken_stele']),
            ('herbal_retreat',['herb_spot','nameless_tomb','sword_scar_wall','mortuary_room','broken_waterwheel']),
            ('desert_caravan',['abandoned_armory','battlefield_remnant','ghost_market_boat','old_bellows','ancient_well'])]
    for name in ids:
        model=js(RES/f'assets/dynasty/models/block/{name}.json')
        state=js(RES/f'assets/dynasty/blockstates/{name}.json')
        elements=model['elements']; lo=[min(e['from'][a] for e in elements) for a in range(3)]
        hi=[max(e['to'][a] for e in elements) for a in range(3)]
        box=[2,0,2,14,5 if name=='herb_spot' else 13,14]
        outside=[i for i,e in enumerate(elements) if any(e['from'][a]<box[a] or e['to'][a]>box[a+3] for a in range(3))]
        group,names=next((g,ns) for g,ns in groups if name in ns)
        structure=js(RES/f'data/dynasty/worldgen/structure/{group}.json')
        ss=js(RES/f'data/dynasty/worldgen/structure_set/{group}.json')
        model_refs=[]
        for variant in state['variants'].values():
            for entry in variant if isinstance(variant,list) else [variant]:
                model_refs.append(entry['model'])
                ns,path=entry['model'].split(':'); js(RES/f'assets/{ns}/models/{path}.json')
        rows.append(dict(id=name,title_zh=zh.get('block.dynasty.'+name),tip_zh=zh.get('interaction.dynasty.'+name),
            elements=len(elements),model_bounds=[lo,hi],declared_getShape_box=box,
            elements_outside_declared_getShape=outside,
            collision_status='PENDING_NATIVE: source shape comparison only',
            natural_site=group,natural_site_style=structure['style'],local_position=[5+names.index(name)*4,1,28],
            structure_set=ss,blockstate_models=model_refs))
    render_shapes(rows)
    material_rows=[]
    for name in ('qimen_cable','soul_incense','crab_steel'):
        material_rows.append(dict(recipe='cod4/'+name,definition=js(RES/f'data/dynasty/recipes/cod4/{name}.json')))
    drops={name:js(RES/f'data/dynasty/loot_tables/entities/{name}.json') for name in ('corpse_beetle','crab_soldier','lantern_ghost','night_watchman')}
    return dict(rows=rows,recipes=material_rows,material_drop_tables=drops,
        survival_chain_zh=['奇门钢索：尸虫/蟹兵掉蟹壳→蟹壳+铁锭合精钢→精钢+2线合钢索。',
                          '安魂香：灯笼鬼/更夫掉灯油→木棍+灯油+纸合安魂香。掉落/配方链存在，实际自然刷怪及玩家生存可达性仍待验。'],
        anchors=[source_anchor(JAVA/'structure/TravelSitePiece.java','String[][] sites'),
                 source_anchor(JAVA/'expansion/SmallInteractions.java','getShape(BlockState state')],
        ecology_structure_tags={name:js(RES/f'data/dynasty/tags/worldgen/structure/{name}.json') for name in ('ecology/tombs','blueprint/ghost_sites','secondary/ruins')},
        pending='Natural placement is present; grouped courtyard placement does not establish full abandoned village/mortuary/cemetery scenes. Survival acquisition and native collision still pending.')


def render_shapes(rows):
    from PIL import Image,ImageDraw
    image=Image.new('RGB',(1500,900),'white'); d=ImageDraw.Draw(image)
    for i,row in enumerate(rows):
        left=(i%5)*300; top=(i//5)*300
        def project(p):
            x,y,z=p
            return (left+145+(x-z)*7,top+205+(x+z)*3-y*7)
        model=json.loads((RES/f"assets/dynasty/models/block/{row['id']}.json").read_text())
        faces=[]
        for e in model['elements']:
            # These production models are axis-aligned; fail rather than silently
            # draw a rotated element as if it were axis-aligned.
            if 'rotation' in e: raise ValueError('Rotated shape preview unsupported')
            x,y,z=e['from']; X,Y,Z=e['to']
            faces.extend([(x+z+X+Z,Y,[(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],'#cbd5e1'),
                          (x+z+X+Z,y,[(X,y,z),(X,y,Z),(X,Y,Z),(X,Y,z)],'#64748b'),
                          (x+z+X+Z,y,[(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],'#94a3b8')])
        for _,__,points,color in sorted(faces,key=lambda f:(f[0],f[1])):
            d.polygon([project(p) for p in points],fill=color,outline='#334155')
        x,y,z,X,Y,Z=row['declared_getShape_box']
        corners=[(a,b,c) for a in (x,X) for b in (y,Y) for c in (z,Z)]
        for j,p in enumerate(corners):
            for q in corners[j+1:]:
                if sum(a!=b for a,b in zip(p,q))==1: d.line([project(p),project(q)],fill='#dc2626',width=2)
        d.text((left+6,top+10),row['id'],fill='#111827')
        d.text((left+6,top+27),'grey = model; red = declared getShape',fill='#111827')
        d.text((left+6,top+275),f"{len(row['elements_outside_declared_getShape'])}/{row['elements']} elements extend outside",fill='#991b1b')
    image.save(OUT/'interaction-shape-comparison.png')


def manor():
    manifest_path=RES/'data/dynasty/sculptures/yunqi_manor.json'; m=js(manifest_path)
    import gzip
    packed=load(RES/'data/dynasty/sculptures/yunqi_manor.vox.gz',True); raw=gzip.decompress(packed)
    structure=js(RES/'data/dynasty/worldgen/structure/yunqi_manor.json')
    ss=js(RES/'data/dynasty/worldgen/structure_set/yunqi_manor.json')
    counts=Counter(raw)
    return dict(size=[m['width'],m['height'],m['length']],
        raw_size_matches=len(raw)==m['voxelCount'],gzip_hash_matches=hashlib.sha256(packed).hexdigest()==m['gzipSha256'],
        raw_hash_matches=hashlib.sha256(raw).hexdigest()==m['sha256'],
        solid_count_matches=len(raw)-counts[0]==m['blockCount'],
        palette_valid=max(counts)<len(m['palette']),structure=structure,structure_set=ss,
        compass_anchor=source_anchor(JAVA/'DynastyCompassBridge.java','new Destination("yunqi_manor","云栖庄园"'),
        native_three_seed_status='PENDING: historical server coordinates are not client compass + on-site evidence',
        historical_seeds=[{'seed':42,'x':-11040,'z':38768},{'seed':2026,'x':-5136,'z':9312},{'seed':-731985,'x':-64256,'z':-26080}],
        shared_exclusion_placement='Both sculpture sets use the same custom Placement. Its candidate footprint chooses site.id, so sculpture_tiles containing only longque does not by itself prove the manor exclusion is missing.')


def arena_and_clearance():
    return dict(arena=dict(
        source_anchor=source_anchor(JAVA/'army/ArmyEncounters.java','for(int x=-25;x<=25;x++)for(int z=-25;z<=25;z++) {'),
        floor_size=[51,51],floor_y_relative=-1,boundary_height=7,
        cover_columns=[{'x':x,'z':z,'height':3} for x in (-15,15) for z in (-8,0,8)],
        player_spawn_relative=[.5,0,-17.5],boss_spawn_relative=[.5,0,12.5],
        geometry_families=1,floor_material_variants=3,cover_material_variants=2,
        status='PENDING: six named stages currently share one floor and cover layout; distinct architecture/circulation is not delivered'),
        clearance=dict(
        natural_anchor=source_anchor(JAVA/'structure/megabuild/NaturalSculptures.java','int clearTop=b.clearTop(localX,localZ);'),
        top_anchor=source_anchor(JAVA/'structure/megabuild/SculptureBlueprint.java','return Math.min(height+4,Math.max(9,top+5));'),
        mining_air_anchor=source_anchor(JAVA/'structure/megabuild/MegabuildPiece.java','placeBlock(level, blockState(kind), x, y, z, box);'),
        status='PENDING_NATIVE_MATRIX',
        limits_zh=['雕塑按列顶+5计算上界，有上限；尚不能据此宣称全部建筑已使用SOLID/INTERIOR_AIR/EXTERIOR_CLEAR三掩码。',
                   '采矿模板导出省略AIR，自然MegabuildPiece则遍历全高写入AIR；清空场地上的形状一致不能证明山坡净空等价。',
                   '平原/森林/山坡/雪地/浅水/跨区块×四朝向及邻近建筑、重载后玩家改建均需原生验收。']))


def frozen_delivery():
    doc=js(ROOT/'docs/art/cod3-ghost-market-v2/BUILDING_READY.json')
    checks=[]
    for path,digest in doc['sha256'].items():
        actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        checks.append(dict(path=path,expected=digest,actual=actual,matches=actual==digest))
    return dict(status=doc['status'],full_scenic_status=doc['full_scenic_status'],hashes=checks,
        resource_anchor=source_anchor(JAVA/'client/ScenicGhostMarketRenderer.java','scenic/ghost_market.json'),
        routing_anchor=source_anchor(JAVA/'cod3/ScenicEvents.java','if(number==22)'),
        note='Preserved existing client-only mirage delivery; not physical natural COD4 mortuary/cemetery architecture.')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report=dict(schema=1,date='2026-10-22',status='PARTIAL_STATIC_REVIEW_NATIVE_PENDING',
        scope=['COD4-1/11/13','COD6-1.5/4/5/6.11'],java_started=False,game_started=False,
        checklist_deleted=[],mining=minerals_and_routes(),interactions=interactions(),
        manor=manor(),arena_clearance=arena_and_clearance(),frozen_ghost_market=frozen_delivery())
    report['input_sha256']=INPUTS
    (OUT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],mineral_cells=report['mining']['mineral_cells'],
        missing_minerals=len(report['mining']['missing_minerals']),
        mirror_mismatches=len(report['mining']['mirror_mismatches']),
        routes=report['mining']['routes'],
        models_beyond_shape=sum(bool(r['elements_outside_declared_getShape']) for r in report['interactions']['rows']),
        frozen_hashes_pass=sum(r['matches'] for r in report['frozen_ghost_market']['hashes']),
        frozen_hashes_total=len(report['frozen_ghost_market']['hashes'])),ensure_ascii=False))


if __name__=='__main__': main()
