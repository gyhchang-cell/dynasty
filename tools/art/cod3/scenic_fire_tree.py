#!/usr/bin/env python3
"""Original rooted basalt fire tree. Pure Python NBT export and offline review; no JVM.

No automatic worldgen placement: the host must first validate a suitable overworld
ravine and reserve the whole footprint. --review reads the delivered NBT again.
"""
import argparse
import gzip
import hashlib
import io
import json
import struct
import sys
import zipfile
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/art/cod3-fire-tree-v2'
DATA = ROOT / 'src/main/resources/data/dynasty'
SIZE = (47, 43, 47)
ID = 'scenic_fire_tree'
AIR = 'air'
DIRS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def utf(s):
    b = s.encode('utf-8')
    return struct.pack('>H', len(b))+b


def kind(v):
    return 10 if isinstance(v, dict) else 9 if isinstance(v, list) else 8 if isinstance(v, str) else 3


def payload(v):
    t = kind(v)
    if t == 3: return struct.pack('>i', v)
    if t == 8: return utf(v)
    if t == 10: return b''.join(bytes([kind(a)])+utf(k)+payload(a) for k,a in v.items())+b'\0'
    subtype = kind(v[0]) if v else 10
    assert all(kind(a)==subtype for a in v)
    return bytes([subtype])+struct.pack('>i', len(v))+b''.join(payload(a) for a in v)


class Reader:
    def __init__(self, b): self.f = io.BytesIO(b)
    def read(self, fmt): return struct.unpack(fmt, self.f.read(struct.calcsize(fmt)))[0]
    def string(self): return self.f.read(self.read('>H')).decode('utf-8')
    def value(self, t):
        if t == 3: return self.read('>i')
        if t == 8: return self.string()
        if t == 9:
            sub = self.read('>B')
            return [self.value(sub) for _ in range(self.read('>i'))]
        if t == 10:
            out = {}
            while (sub := self.read('>B')):
                name = self.string()
                out[name] = self.value(sub)
            return out
        raise ValueError(t)


def read_nbt():
    reader = Reader(gzip.decompress((DATA/f'structures/{ID}.nbt').read_bytes()))
    assert reader.read('>B') == 10 and reader.string() == ''
    out = reader.value(10)
    assert reader.f.read() == b''
    return out


def build():
    blocks, tree, buds = {}, set(), []
    def put(x,y,z,b,wood=False):
        assert all(0<=a<limit for a,limit in zip((x,y,z),SIZE)), (x,y,z)
        blocks[x,y,z] = b
        if wood: tree.add((x,y,z))
    def disk(cx,cy,cz,r,b,wood=False):
        for dx in range(-r,r+1):
            for dz in range(-r,r+1):
                if abs(dx)+abs(dz)<=max(r,2*r-1): put(cx+dx,cy,cz+dz,b,wood)
    # Chamfered footprint, layered basalt banks and a sealed, sinuous lava trench.
    # Explicit air gives the receiving placement code a bounded clearance contract.
    for x in range(47):
        for z in range(47):
            if abs(x-23)+abs(z-23)>39: continue
            center = 23 + round(2*((z%24)-12)/12)
            distance = abs(x-center)
            channel = 4<=z<=42 and distance<=6
            rim = 10 if distance>=9 else 8 if distance>=7 else 2
            if not 4<=z<=42: rim=10
            # Taper into adjacent rock rather than exporting a vertical podium.
            margin=min(x,46-x,z,46-z,(39-abs(x-23)-abs(z-23))//2)
            rim=min(rim,2+2*max(0,margin))
            # Root island is connected to the solid trench bottom, never floats.
            if abs(x-24)+abs(z-25)<=5: rim=max(rim,9)
            for y in range(43):
                b = AIR
                if y<=rim:
                    b = 'deepslate' if y<2 else 'smooth_basalt'
                    if y==rim and distance>=9: b='tuff'
                    elif y>=3 and (x//3+z//5)%3==0: b='basalt'
                elif channel and y==3: b='lava'
                put(x,y,z,b)
    # Broad continuous approach on each shore. These are supported full blocks.
    for x0 in (5,36):
        for x in range(x0,x0+6):
            for z in range(4,43):
                for y in range(2,11): put(x,y,z,'polished_blackstone_bricks' if y==10 else 'basalt')
                for y in range(11,15): put(x,y,z,AIR)
            for z in range(4):
                top=6+z
                for y in range(top+1):put(x,y,z,'polished_blackstone_bricks' if y==top else 'basalt')
                for y in range(top+1,43):put(x,y,z,AIR)
    # Three small observation bays, never a bridge across the hot central channel.
    for x0,z0 in [(10,18),(10,32),(32,21)]:
        for x in range(x0,x0+5):
            for z in range(z0,z0+7):
                for y in range(2,11): put(x,y,z,'polished_blackstone_bricks' if y==10 else 'basalt')
                for y in range(11,15): put(x,y,z,AIR)
        edge = x0+4 if x0<23 else x0
        for z in range(z0,z0+7): put(edge,11,z,'polished_blackstone_bricks')
    # Segmented, face-connected path. Thin diagonal boughs never meet at a corner only.
    def limb(points):
        for (a,b) in zip(points,points[1:]):
            start, end = a[:3], b[:3]
            steps=max(abs(v-u) for u,v in zip(start,end))
            previous=start
            for i in range(steps+1):
                t=i/max(1,steps)
                target=tuple(round(u+(v-u)*t) for u,v in zip(start,end))
                radius=round(a[3]+(b[3]-a[3])*t)
                chain=[previous]
                p=list(previous)
                for axis in (1,0,2):
                    while p[axis]!=target[axis]:
                        p[axis]+=1 if p[axis]<target[axis] else -1
                        chain.append(tuple(p))
                for x,y,z in chain:
                    for dy in range(-min(1,radius),min(1,radius)+1):
                        disk(x,y+dy,z,radius,'basalt' if radius>=2 else 'blackstone',True)
                previous=target
    roots=[[(24,8,25,3),(20,10,24,2),(16,12,22,1),(13,10,20,1)],
           [(24,8,25,3),(29,10,26,2),(33,12,28,1),(36,10,31,1)],
           [(24,8,25,2),(23,7,30,2),(21,4,34,1)],
           [(24,8,25,2),(27,6,20,1),(28,3,16,1)]]
    for root in roots: limb(root)
    trunk=[(24,8,25,3),(25,14,25,3),(23,20,25,2),(24,25,24,2),(28,31,23,1),(29,36,24,0)]
    limb(trunk)
    boughs=[[(23,20,25,2),(18,23,24,1),(12,24,22,1),(8,27,22,0)],
            [(24,25,24,2),(30,27,24,1),(35,29,26,1),(39,32,25,0)],
            [(25,15,25,2),(24,20,19,1),(20,23,14,1),(18,25,9,0)],
            [(24,25,24,2),(23,29,29,1),(19,31,34,1),(16,34,36,0)],
            [(28,31,23,1),(24,34,19,1),(23,38,16,0)],
            [(18,23,24,1),(15,27,28,0),(12,29,30,0)],
            [(12,24,22,1),(11,27,18,0),(9,29,16,0)],
            [(30,27,24,1),(33,30,19,0),(37,32,17,0)],
            [(35,29,26,1),(35,32,31,0),(37,34,33,0)],
            [(24,20,19,1),(29,24,16,0),(31,27,12,0)],
            [(20,23,14,1),(15,25,13,0),(12,27,11,0)],
            [(23,29,29,1),(27,32,33,0),(30,34,36,0)],
            [(19,31,34,1),(17,34,30,0),(14,36,29,0)],
            [(24,34,19,1),(27,37,16,0),(30,39,15,0)],
            [(28,31,23,1),(31,34,27,0),(32,37,28,0)]]
    for branch in boughs: limb(branch)
    # Mineralized silver blossoms: tiny discrete clusters attached to real tips.
    # No leaf blocks, fire blocks, particles, entities or custom textures.
    for i,branch in enumerate(boughs+[trunk]):
        x,y,z,_=branch[-1]
        put(x,y+1,z,'ochre_froglight' if i%4 else 'shroomlight',True)
        buds.append([x,y+1,z])
        for dx,dz in ([(-1,0),(1,0)] if i%2==0 else [(0,-1),(0,1)]):
            put(x+dx,y+1,z+dz,'calcite',True)
        put(x,y+2,z,'calcite',True)
    # Exposed ember knots in the root collar; body remains rock rather than red leaves.
    for x,y,z in [(21,8,25),(27,10,25),(24,8,22),(24,9,28)]:
        assert (x,y,z) in tree
        put(x,y,z,'shroomlight',True)
    palette=sorted(set(blocks.values()))
    indices={b:i for i,b in enumerate(palette)}
    states=[]
    for b in palette:
        state={'Name':'minecraft:'+b}
        if b in ('basalt','ochre_froglight'): state['Properties']={'axis':'y'}
        if b=='lava': state['Properties']={'level':'0'}
        states.append(state)
    nbt={'DataVersion':3465,'size':list(SIZE),'palette':states,
         'blocks':[{'pos':list(p),'state':indices[b]} for p,b in sorted(blocks.items())],'entities':[]}
    path=DATA/f'structures/{ID}.nbt'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(b'\x0a\0\0'+payload(nbt),mtime=0))
    dump(DATA/f'worldgen/template_pool/{ID}.json',{'name':'dynasty:'+ID,'fallback':'minecraft:empty',
         'elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'dynasty:'+ID,
         'processors':'minecraft:empty','projection':'rigid'}}]})
    manifest={'id':'dynasty:'+ID,'size':SIZE,'origin':'minimum block corner, y=sealed trench bottom',
        'root_anchor':[24,9,25],'effect_anchor':[24.5,26,24.5],'bud_centers':buds,
        'entry':[7,7,0],'east_entry':[39,7,0],
        'observation_points':[[12,11,18],[12,11,37],[34,11,21]],
        'tree_positions':[list(p) for p in sorted(tree)],'palette_counts':dict(Counter(blocks.values())),
        'spawn_entities':0,'block_entities':0,'automatic_worldgen_enabled':False,
        'explicit_air_clears_local_volume':True,'java_integration_pending':True}
    dump(DOC/'geometry.json',manifest)
    return manifest


def check():
    nbt=read_nbt();m=json.loads((DOC/'geometry.json').read_text())
    palette=[p['Name'].removeprefix('minecraft:') for p in nbt['palette']]
    b={tuple(r['pos']):palette[r['state']] for r in nbt['blocks']}
    tests=[]
    def test(name,ok):
        tests.append({'name':name,'passed':bool(ok)})
    test('standard dimensions',nbt['size']==list(SIZE))
    test('no entities or block entities',nbt['entities']==[] and all('nbt' not in r for r in nbt['blocks']))
    test('unique coordinates',len(b)==len(nbt['blocks']))
    test('all coordinates bounded',all(all(0<=v<SIZE[i] for i,v in enumerate(p)) for p in b))
    tree=set(map(tuple,m['tree_positions']))
    test('tree entries exist in production NBT',all(b.get(p) not in (None,AIR,'lava') for p in tree))
    seen={next(iter(tree))};q=deque(seen)
    while q:
        p=q.popleft()
        for d in DIRS:
            v=tuple(x+y for x,y in zip(p,d))
            if v in tree and v not in seen:seen.add(v);q.append(v)
    test('all roots branches and blossoms face-connected',seen==tree)
    test('tree tied to solid bottom',any(p[1]<=3 and b.get((p[0],p[1]-1,p[2])) not in (None,AIR,'lava') for p in tree))
    lava={p for p,v in b.items() if v=='lava'}
    test('lava exists',len(lava)>100)
    test('all lava sealed below and horizontally',all(b.get((x+dx,y+dy,z+dz)) not in (None,AIR) for x,y,z in lava for dx,dy,dz in DIRS if dy<=0))
    def walkable(p):
        x,y,z=p
        return b.get(p)==AIR and b.get((x,y+1,z))==AIR and b.get((x,y-1,z)) not in (None,AIR,'lava')
    def flood(start):
        assert walkable(start),start
        seen={start};queue=deque([start])
        while queue:
            x,y,z=queue.popleft()
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                for dy in (0,-1,1):
                    v=(x+dx,y+dy,z+dz)
                    if v in seen or not walkable(v):continue
                    if dy==1 and b.get((x,y+2,z))!=AIR:continue
                    if dy==-1 and b.get((x+dx,y+1,z+dz))!=AIR:continue
                    seen.add(v);queue.append(v)
        return seen
    west=flood(tuple(m['entry']));east=flood(tuple(m['east_entry']))
    for i,p in enumerate(m['observation_points']):
        test(f'observation {i+1} reachable and returnable',tuple(p) in (west if i<2 else east))
    # A continuous three-block-wide same-height corridor allows return without jumping.
    for x0,label in ((6,'west'),(38,'east')):
        test(label+' three-wide safe path',all(walkable((x,11,z)) for x in range(x0,x0+3) for z in range(4,43)))
        test(label+' path has continuous solid foundation',all(b.get((x,y,z)) not in (None,AIR,'lava') for x in range(x0,x0+3) for z in range(4,43) for y in range(11)))
        test(label+' entry stair has one-block risers',all(walkable((x,z+7,z)) for x in range(x0,x0+3) for z in range(4)))
    for i,(x,y,z) in enumerate(m['bud_centers']):
        test(f'blossom {i+1} supported', (x,y-1,z) in tree and b[x,y,z] in ('ochre_froglight','shroomlight'))
        test(f'blossom {i+1} luminous core exposed',any(b.get((x+dx,y,z+dz))==AIR for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))))
    crown=[p for p in tree if p[1]>=20]
    density=len(crown)/((max(p[0] for p in crown)-min(p[0] for p in crown)+1)*(max(p[1] for p in crown)-19)*(max(p[2] for p in crown)-min(p[2] for p in crown)+1))
    test('crown volume at least 80 percent negative space',density<.2)
    test('glow blocks sparse',sum(v in ('ochre_froglight','shroomlight') for v in b.values())<=20)
    out={'status':'PASS' if all(t['passed'] for t in tests) else 'FAIL','java_executed':False,'native_game_verified':False,
         'tests':tests,'tree_blocks':len(tree),'crown_solid_fraction':density,'lava_blocks':len(lava),
         'west_walkable':len(west),'east_walkable':len(east),'geometry_sha256':hashlib.sha256((DATA/f'structures/{ID}.nbt').read_bytes()).hexdigest()}
    dump(DOC/'validation.json',out)
    print(json.dumps({k:v for k,v in out.items() if k!='tests'},ensure_ascii=False))
    failed=[t for t in tests if not t['passed']]
    if failed:raise AssertionError(failed)
    return b,m


def review():
    import numpy as np
    from PIL import Image,ImageDraw
    sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
    import texture_review as r
    b,m=check();solid={p:v for p,v in b.items() if v!=AIR}
    client=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar'
    if not client.exists(): client=client.with_name('client.jar')
    textures={}
    with zipfile.ZipFile(client) as z:
        def texture(name,face):
            key={'basalt':'basalt_top' if face in ('up','down') else 'basalt_side',
                 'deepslate':'deepslate_top' if face in ('up','down') else 'deepslate',
                 'blackstone':'blackstone_top' if face in ('up','down') else 'blackstone',
                 'ochre_froglight':'ochre_froglight_top' if face in ('up','down') else 'ochre_froglight_side',
                 'lava':'lava_still'}.get(name,name)
            if key not in textures:
                with Image.open(io.BytesIO(z.read('assets/minecraft/textures/block/'+key+'.png'))) as im:
                    # Animated vanilla lava: first frame only, no artificial glow.
                    textures[key]=np.array(im.convert('RGB').crop((0,0,16,16)))
            return textures[key]
        delta={'north':(0,0,-1),'south':(0,0,1),'east':(-1,0,0),'west':(1,0,0),'up':(0,1,0),'down':(0,-1,0)}
        quads=[];treequads=[];tree=set(map(tuple,m['tree_positions']))
        for p,name in solid.items():
            for face,corners in r.r.FACES.items():
                neighbor=tuple(a+d for a,d in zip(p,delta[face]))
                if neighbor in solid:continue
                item=((np.array(corners)+p)*16,{'uv':[0,0],'uv_size':[16,16],'_tex':texture(name,face)},'block')
                quads.append(item)
                if p in tree:treequads.append(item)
        # Review-only 1.8m human scale reference on the west bank, never exported to NBT.
        quads+=r.references(np.array([8*16+12,11*16,8*16]))
        points=np.concatenate([v[0] for v in quads]);fallback=np.zeros((16,16,3),dtype=np.uint8)
        for yaw,label in [(0,'front'),(90,'side'),(180,'back'),(45,'three-quarter')]:
            r.labelled(r.raster(quads,fallback,yaw=yaw,elevation=18,size=(1200,1000),mode='lit',frame_points=points),
                '深谷火树 / '+label,'软件检查 · 实际NBT+原版PNG · 原比例1.8米参照人 · 无特效 · 非游戏截图').save(DOC/(label+'.png'))
        for mode in ('gray','dim'):
            r.labelled(r.raster(quads,fallback,yaw=45,elevation=18,size=(1200,1000),mode=mode,frame_points=points),
                '深谷火树 / '+mode,'软件检查 · 实际NBT · 无粒子/发光模拟 · 非游戏截图').save(DOC/(mode+'.png'))
        black=[(v,dict(uv,_tex=fallback),bone) for v,uv,bone in treequads]
        r.labelled(r.raster(black,fallback,yaw=0,elevation=8,size=(1200,1000),mode='unlit',frame_points=points),
            '深谷火树 / 树体剪影','软件检查 · 仅隐藏地形以检查树根和枝冠 · 同比例 · 非游戏截图').save(DOC/'silhouette.png')
        plan=Image.new('RGB',(47,47),(225,226,222))
        for x in range(47):
            for zz in range(47):
                col=[(y,v) for (xx,y,z0),v in solid.items() if xx==x and z0==zz and y<=11]
                if not col:continue
                y,v=max(col);color=(220,91,31) if v=='lava' else (62,67,71) if (x,y,zz) in tree else (132,140,143)
                if b.get((x,11,zz))==AIR and b.get((x,10,zz))=='polished_blackstone_bricks':color=(63,145,156)
                plan.putpixel((x,zz),color)
        plan=plan.resize((752,752),Image.Resampling.NEAREST);draw=ImageDraw.Draw(plan)
        for p in [m['entry'],m['east_entry']]+m['observation_points']:
            x,y,z0=p;draw.ellipse((x*16+3,z0*16+3,x*16+12,z0*16+12),fill=(255,240,121))
        r.labelled(plan,'观景路线 / 平面 x,z','青色=铺装通路；黄点=入口/观察点；橙色=低位熔岩。软件图。').save(DOC/'routes.png')
        dump(DOC/'preview.json',{'source':'actual exported NBT + local vanilla PNG','native_screenshot':False,
             'texture_source':str(client),'texture_sha256':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in textures.items()},
             'exposed_faces':len(quads),'views':['front','side','back','three-quarter','gray','dim','silhouette','routes']})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--review',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.review:review()
    elif args.check:check()
    else:build();check()
