#!/usr/bin/env python3
"""Inventory concrete structural implementations in the user's local reference jars.

No assets are extracted into game resources. Deduplicate geometry independent of
palette, translation and four horizontal rotations. This is static structural
research, not proof of 1000 mechanisms or 1000 in-game visual inspections.
"""
import argparse
import hashlib
import json
import struct
from collections import Counter, defaultdict, deque
from pathlib import Path
from zipfile import ZipFile

from nbt_read import read

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ('betterdungeons', '*地牢增强]*.jar', 'https://github.com/YUNG-GANG/YUNGs-Better-Dungeons'),
    ('betterstrongholds', '*要塞优化]*.jar', 'https://github.com/YUNG-GANG/YUNGs-Better-Strongholds'),
    ('dungeons_arise', '*地牢浮现之时]*.jar', 'https://www.curseforge.com/minecraft/mc-mods/when-dungeons-arise'),
    ('kaisyn', '*城镇与塔楼]*.jar', 'https://www.curseforge.com/minecraft/mc-mods/towns-and-towers'),
    ('repurposed_structures', '*结构变体]*.jar', 'https://github.com/TelepathicGrunt/RepurposedStructures'),
]


def role(name):
    if name in ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'):
        return 0
    if name == 'minecraft:structure_void':
        return None
    if name == 'minecraft:jigsaw':
        return 2
    if name in ('minecraft:chest', 'minecraft:trapped_chest', 'minecraft:barrel'):
        return 3
    if name.endswith('spawner'):
        return 4
    if name in ('minecraft:water', 'minecraft:lava'):
        return 5
    return 1


def geometry_hash(cells, size):
    # Positions of explicit air matter: omission and explicit air place differently.
    # All solid materials collapse to one role, so recolouring is not a new entry.
    variants = []
    for rotation in range(4):
        transformed = []
        for (x, y, z), kind in cells.items():
            for _ in range(rotation):
                x, z = -z, x
            transformed.append((x, y, z, kind))
        mins = [min(p[a] for p in transformed) for a in range(3)]
        payload = b''.join(struct.pack('>HHHB', x-mins[0], y-mins[1], z-mins[2], k)
                           for x, y, z, k in sorted(transformed))
        variants.append(hashlib.sha256(payload).hexdigest())
    return min(variants)


def analyse(nbt):
    palette = nbt.get('palette') or nbt.get('palettes', [[]])[0]
    kinds = [role(p['Name']) for p in palette]
    cells, sockets, loot, spawners = {}, [], [], []
    for b in nbt.get('blocks', []):
        pos = tuple(b['pos'])
        kind = kinds[b['state']]
        if kind is not None:
            cells[pos] = kind
        data = b.get('nbt', {})
        if kind == 2:
            sockets.append({'position': pos, **{k:data[k] for k in ('name', 'target', 'pool', 'joint', 'final_state') if k in data}})
        if data.get('LootTable'):
            loot.append({'position':pos, 'table':data['LootTable']})
        if kind == 4:
            spawners.append(pos)
    solids = sum(k not in (0, 2) for k in cells.values())
    if solids < 25 or len(cells) > 140000:
        return None, 'tiny_or_oversize'
    # Conservative full-cell geometric candidates, not Minecraft collision/pathfinding.
    walk = {(x,y,z) for (x,y,z), k in cells.items() if k == 0
            and cells.get((x,y+1,z)) == 0 and cells.get((x,y-1,z)) in (1,3)}
    if not (sockets or loot or spawners or len(walk) >= 8):
        return None, 'no_functional_anchor'
    remaining = set(walk)
    largest = 0
    while remaining:
        q = [remaining.pop()]
        count = 0
        while q:
            x,y,z = q.pop(); count += 1
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                for dy in (-1,0,1):
                    candidate = (x+dx,y+dy,z+dz)
                    if candidate in remaining:
                        remaining.remove(candidate); q.append(candidate)
        largest = max(largest, count)
    size = nbt.get('size', [0,0,0])
    boundary = sum(x in (0,size[0]-1) or z in (0,size[2]-1) for x,y,z in walk)
    levels = Counter(p[1] for p in walk)
    floor = max(levels, key=lambda y:(levels[y],-y)) if levels else size[1]//2
    details = dict(size=size, geometry_sha256=geometry_hash(cells,size),
                   solid_cells=solids, explicit_air=sum(k==0 for k in cells.values()),
                   omitted_cells=size[0]*size[1]*size[2]-len(cells),
                   stand_candidates=len(walk), largest_geometric_component=largest,
                   boundary_stand_candidates=boundary, sockets=sockets, loot=loot,
                   spawners=spawners, floor_slice=floor)
    return (details, cells), None


def make_note(d):
    points=[]
    if d['sockets']:
        points.append(f"{len(d['sockets'])}个实际拼接点；对照接口与道路/房间的衔接")
    if d['loot']:
        points.append(f"{len(d['loot'])}处战利品表锚点；对照生存奖励位置")
    if d['spawners']:
        points.append(f"{len(d['spawners'])}处刷怪笼；对照遭遇区与通行带的分隔")
    points.append(f"显式空气{d['explicit_air']}格、省略{d['omitted_cells']}格；对照净空与不写入的区别")
    if d['stand_candidates']:
        points.append(f"保守双格站立候选{d['stand_candidates']}，最大几何连通分量{d['largest_geometric_component']}；碰撞与门状态未模拟")
    return '；'.join(points)


def thumbnail(cells, details):
    from PIL import Image, ImageDraw
    w,h,l = details['size']; y = details['floor_slice']
    img = Image.new('RGB', (max(1,w),max(1,l)), '#e5e7eb')
    pix=img.load()
    colors={0:'#f9fafb',1:'#374151',2:'#c084fc',3:'#f59e0b',4:'#ef4444',5:'#38bdf8'}
    for (x,by,z),k in cells.items():
        if by == y and 0 <= x < w and 0 <= z < l:
            pix[x,z]=tuple(bytes.fromhex(colors[k][1:]))
    scale = min(146 / img.width, 108 / img.height)
    img = img.resize((max(1,round(img.width*scale)),max(1,round(img.height*scale))), Image.Resampling.NEAREST)
    return img


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mods',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'docs/architecture/continuation-20261022/references')
    p.add_argument('--limit',type=int,default=1000)
    args=p.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    sources=[]; queues=[]; skips=Counter(); fingerprints={}; rows=[]; sheets=[]
    for namespace,pattern,url in SOURCES:
        matches=list(args.mods.glob(pattern))
        if len(matches)!=1: raise ValueError((pattern,matches))
        path=matches[0]; archive=ZipFile(path)
        pools=defaultdict(list)
        for member in archive.namelist():
            if '/worldgen/template_pool/' not in member or not member.endswith('.json'): continue
            data=json.loads(archive.read(member))
            def visit(value):
                if isinstance(value,dict):
                    loc=value.get('location')
                    if isinstance(loc,str): pools[loc].append(member)
                    for v in value.values(): visit(v)
                elif isinstance(value,list):
                    for v in value: visit(v)
            visit(data)
        names=sorted(n for n in archive.namelist() if '/structures/' in n and n.endswith('.nbt'))
        sources.append(dict(id=namespace,local_jar=str(path),jar_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),official_url=url,nbt_candidates=len(names)))
        queues.append((namespace,archive,deque(names),pools))
    scanned=0
    while len(rows)<args.limit and any(q for _,_,q,_ in queues):
        for namespace,archive,q,pools in queues:
            if len(rows)>=args.limit or not q: continue
            name=q.popleft(); scanned+=1
            parts=name.split('/'); location=parts[1]+':'+name.split('/structures/',1)[1][:-4]
            if not pools.get(location):
                skips['no_pool_reference']+=1; continue
            raw=archive.read(name); nbt=read(raw)
            result,skip=analyse(nbt)
            if skip: skips[skip]+=1; continue
            d,cells=result
            if d['geometry_sha256'] in fingerprints:
                skips['geometry_duplicate']+=1; continue
            rid=len(rows)+1; fingerprints[d['geometry_sha256']]=rid
            row=dict(index=rid,source=namespace,archive_member=name,resource=location,
                     resource_sha256=hashlib.sha256(raw).hexdigest(),
                     pool_references=sorted(set(pools.get(location,[]))),**d)
            row['observation_zh']=make_note(d)
            row['applicability_zh']='COD4互动场景/生存奖励锚点；COD6入口、阵型通道及有限空气掩码'
            rows.append(row)
            if (rid-1)%100==0:
                sheets.append(Image.new('RGB',(1600,1400),'#ffffff'))
            sheet=sheets[-1]; i=(rid-1)%100; x=(i%10)*160; y=(i//10)*140
            im=thumbnail(cells,d); sheet.paste(im,(x+(160-im.width)//2,y))
            draw=ImageDraw.Draw(sheet)
            draw.text((x+3,y+109),f'{rid:04d} {namespace[:15]}',fill='#111827')
            draw.text((x+3,y+122),name.rsplit('/',1)[-1][:23],fill='#374151')
            if rid%100==0: print(f'{rid} unique components, {scanned} scanned',flush=True)
    for i,sheet in enumerate(sheets): sheet.save(args.output/f'floor-slices-{i+1:02}.png')
    report=dict(schema=2,kind='STATIC_STRUCTURAL_COMPONENT_RESEARCH',
                reference_unit='distinct concrete NBT component geometry with functional anchor; not independent projects or mechanism types',
                visual_scope='one actual floor slice per component; not full building visual or native acceptance',
                sources=sources,scanned=scanned,unique_components=len(rows),skips=dict(skips),
                counts=dict(Counter(r['source'] for r in rows)),
                dedup='material-independent roles, translation and four Y rotations; explicit air kept distinct from omitted cells',
                component_scan_target=args.limit,component_scan_target_met=len(rows)>=args.limit,
                full_building_reference_requirement=dict(
                    register='full-buildings.json',minimum=1000,
                    automatic_credit_from_components=0,
                    status='COMPONENT_SCAN_DOES_NOT_ESTABLISH_FULL_BUILDING_REFERENCE_COMPLETION'),
                rows=rows)
    (args.output/'components.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with (args.output/'components.tsv').open('w') as out:
        out.write('index\tsource\tarchive_member\tresource_sha256\tgeometry_sha256\tobservation_zh\n')
        for r in rows: out.write('\t'.join(str(r[k]) for k in ('index','source','archive_member','resource_sha256','geometry_sha256','observation_zh'))+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','sources')},ensure_ascii=False))


if __name__=='__main__': main()
