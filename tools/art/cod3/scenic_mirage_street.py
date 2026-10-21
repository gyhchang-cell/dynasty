#!/usr/bin/env python3
"""Original mirage street: deterministic sparse NBT, client visual data ONLY.

Never installs, launches Java, places blocks, or writes player saves. --review
reads the production NBT and vanilla PNGs, producing explicitly offline images.
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
DOC = ROOT / 'docs/art/cod3-mirage-street-v2'
OUTPUT = ROOT / 'src/main/resources/data/dynasty/structures/scenic_mirage_street.nbt'
CLIENT_OUTPUT = ROOT / 'src/main/resources/assets/dynasty/scenic/mirage_street.json'
STONE_REFERENCES = ROOT / 'docs/art/cod3-stone-god-v2/references/reference-index.json'
SIZE = (44, 24, 32)
DIRS = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
# Vanilla world axes. Do not reuse the offline raster helper's east/west labels.
FACE_DELTAS = {'down':(0,-1,0),'up':(0,1,0),'north':(0,0,-1),
               'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}
WOOD = 'stripped_dark_oak_log'
ROOF = 'deepslate_tiles'
WALL = 'smooth_sandstone'


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    def __init__(self, raw): self.f = io.BytesIO(raw)
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


def encode(nbt):
    # GzipFile fixes the OS header byte across Python 3.11/3.13; compress(mtime=0)
    # delegates to zlib with a platform-dependent header on some Python builds.
    out=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=9) as f:
        f.write(b'\x0a\0\0'+payload(nbt))
    return out.getvalue()


def read_nbt():
    r = Reader(gzip.decompress(OUTPUT.read_bytes()))
    assert r.read('>B') == 10 and r.string() == ''
    nbt = r.value(10)
    assert r.f.read() == b''
    return nbt


def design():
    b, shops, flags, lights = {}, [], [], []
    def put(x,y,z,name):
        assert all(0<=v<SIZE[a] for a,v in enumerate((x,y,z))), (x,y,z)
        if name is None: b.pop((x,y,z), None)
        else: b[x,y,z] = name
    def box(x0,y0,z0,x1,y1,z1,name):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1): put(x,y,z,name)
    def roof(x0,z0,x1,z1,y):
        # Low hip roof: broad two-block runs, only a few height changes.
        # Single-block eave; risers alone get a second block for face connection.
        for x in range(x0,x1+1):
            for z in range(z0,z1+1):
                inset = min(x-x0,x1-x,z-z0,z1-z)
                top = y + min(3, inset//2)
                put(x,top,z,ROOF)
                if inset in (2,4,6): put(x,top-1,z,ROOF)
                if inset==1: put(x,top-1,z,'spruce_planks')
        if x1-x0 >= z1-z0:
            cz=(z0+z1)//2; ytop=y+min(3,(z1-z0)//4)+1
            box(x0+3,ytop,cz,x1-3,ytop,cz,'polished_deepslate')
        else:
            cx=(x0+x1)//2; ytop=y+min(3,(x1-x0)//4)+1
            box(cx,ytop,z0+3,cx,ytop,z1-3,'polished_deepslate')
        # Short continuous upturns, rather than isolated battlement-like cubes.
        for x in (x0,x1):
            for z in (z0,z1):
                sx=1 if x==x0 else -1
                sz=1 if z==z0 else -1
                put(x,y+1,z,ROOF)
                put(x+sx,y+1,z,ROOF)
                put(x,y+1,z+sz,ROOF)
    # Sparse chamfered ground silhouette. No air entries, terrain replacement,
    # block entities, structures, templates or structure sets are registered.
    for x in range(2,42):
        for z in range(2,32):
            if z<5 and not 12<=x<=31: continue
            if z==31 and not 6<=x<=37: continue
            put(x,0,z,'sandstone')
    box(18,0,0,25,0,31,WALL)
    for x in (18,25): box(x,0,0,x,0,31,'cut_sandstone')

    def shop(name,x0,z0,x1,z1,wall_top,west,flag_color,two_storey=False):
        face=x1 if west else x0
        outward=1 if west else -1
        front=face+outward*2
        mid=(z0+z1)//2
        box(x0,0,z0,x1,0,z1,'cut_sandstone')
        # Solid one-block walls surrounding a real room, not a filled building.
        for y in range(1,wall_top+1):
            for x in range(x0,x1+1):
                for z in range(z0,z1+1):
                    if x in (x0,x1) or z in (z0,z1): put(x,y,z,'cut_sandstone' if y==1 else WALL)
        for x in (x0,x1):
            for z in (z0,z1): box(x,1,z,x,wall_top,z,WOOD)
        for y in (wall_top,):
            box(x0,y,z0,x1,y,z0,WOOD);box(x0,y,z1,x1,y,z1,WOOD)
            box(x0,y,z0,x0,y,z1,WOOD);box(x1,y,z0,x1,y,z1,WOOD)
        # Door and counter window are different openings, both genuinely empty.
        box(face,1,mid-2,face,3,mid,None)
        box(face,2,mid+2,face,3,mid+3,None)
        box(face,1,mid+2,face,1,mid+3,'spruce_planks')
        box(face,4,mid-2,face,4,mid,WOOD)
        back=x0 if west else x1
        box(back,2,mid-1,back,3,mid,None)
        for z in (z0,z1):
            cx=(x0+x1)//2
            box(cx,2,z,cx+1,3,z,None)
            box(cx,1,z,cx+1,1,z,'spruce_planks')
        if two_storey:
            box(x0+1,5,z0+1,x1-1,5,z1-1,'spruce_planks')
            for z in (z0,z1): box(x0,5,z,x1,5,z,WOOD)
            for x in (x0,x1): box(x,5,z0,x,5,z1,WOOD)
            for x in (x0,x1):
                box(x,7,mid-2,x,8,mid-1,None)
                box(x,7,mid+1,x,8,mid+2,None)
                box(x,6,z0,x,6,z1,'spruce_planks')
        roof(x0-1,z0-1,x1+1,z1+1,wall_top+1)
        # A low front awning with ends actually held up by posts; central lane
        # x=18..25 remains free of posts and flags below head height.
        lo,hi=sorted((face,front))
        box(lo,4,z0,hi,4,z1,'spruce_planks')
        for z in (z0,z1): box(front,1,z,front,4,z,WOOD)
        box(lo,5,z0,hi,5,z1,ROOF)
        # Attached two-colour shop flags, static cubes, not banner block entities.
        fz=z1-1
        box(front,5,fz,front,6,fz,WOOD)
        fx=front+outward
        box(min(fx,front),6,fz,max(fx,front),6,fz,WOOD)
        box(fx,3,fz,fx,5,fz,flag_color)
        put(fx,3,fz,'yellow_terracotta')
        flags.append([fx,4,fz])
        lamp=[face+outward,3,z0+1]
        put(*lamp, 'ochre_froglight')
        put(lamp[0],4,lamp[2],WOOD)
        lights.append(lamp)
        shops.append({'name_zh':name,'wall_bounds':[x0,1,z0,x1,wall_top,z1],
                      'door':[face,1,mid-1],'inside':[face-outward,1,mid-1],
                      'faces':'+X' if west else '-X','wall_height':wall_top,
                      'visual_storeys':2 if two_storey else 1})

    shop('西前茶铺',3,9,14,16,6,True,'red_terracotta')
    shop('西后绸铺',4,21,14,29,7,True,'orange_terracotta')
    shop('东前香铺',29,9,39,17,7,False,'orange_terracotta')
    shop('东后客栈',29,22,40,29,10,False,'red_terracotta',True)
    # Main gate: thick bases, open 10-block aperture, one secondary upper frame.
    for x in (15,27):
        box(x-1,0,2,x+2,1,5,'cut_sandstone')
        box(x,2,3,x+1,8,4,WOOD)
        box(x,6,2,x+1,7,5,'spruce_planks')
    box(14,8,3,29,9,4,WOOD)
    box(18,8,2,25,9,2,'red_terracotta')
    roof(12,1,31,6,10)
    for x in (18,25): box(x,11,3,x,14,4,WOOD)
    box(18,14,3,25,14,4,WOOD)
    roof(16,2,27,5,15)
    # Two non-emissive wooden lattice panels leave the upper central hole open.
    for x in (19,24): box(x,12,3,x,13,4,'spruce_planks')
    for x in (16,27):
        put(x,6,6,WOOD);put(x,5,6,'ochre_froglight');lights.append([x,5,6])
    palette=sorted(set(b.values()))
    states=[]
    for name in palette:
        state={'Name':'minecraft:'+name}
        if name in (WOOD,'ochre_froglight'): state['Properties']={'axis':'y'}
        states.append(state)
    index={name:i for i,name in enumerate(palette)}
    nbt={'DataVersion':3465,'size':list(SIZE),'palette':states,
         'blocks':[{'pos':list(p),'state':index[name]} for p,name in sorted(b.items())], 'entities':[]}
    meta={'id':'dynasty:scenic_mirage_street','event_id':14,'name_zh':'蜃楼幻市·荒野长街',
          'size':list(SIZE),'anchor':[22,1,0],'center_pivot':[22,1,16],
          'front':'-Z','street_axis':'+Z','ground_block_y':0,'walking_surface_y':1,
          'runtime_origin':'center_pivot','runtime_transform':'world = eventCenter + rotation(local - [22,1,16])',
          'runtime_walking_surface_y':0,'runtime_ground_block_y':-1,
          'anchor_semantics':'entry landmark only; not the runtime origin',
          'shops':shops,'flags':flags,'lights':lights,'single_lod':True,
          'client_visual_only':True,'place_in_world':False,'explicit_air':False,
          'event_contract':{'dimension':'minecraft:overworld','biome':'desert','time':'deep_night',
                            'weather':'clear','duration_ticks':1800,'distance':'medium',
                            'effect_budget':80,'sound':'faint_market_calls; host integration only'},
          'geometry_notes':'Four distinct shops and one main gate. Sparse opaque vanilla full cubes. No interactive logic.'}
    return nbt,meta


def client_mesh(nbt,meta):
    """Same unshifted local voxel coordinates as NBT; consumer subtracts pivot.

    Every exported palette state is an opaque full cube. Adjacent members of
    that class occlude their shared face even when their materials differ.
    No outside, bottom, cavity or window faces are removed by camera guesses.
    """
    blocks=[row['pos']+[row['state']] for row in nbt['blocks']]
    occupied={tuple(row[:3]) for row in blocks}
    faces=[row+[face] for row in blocks for face,delta in FACE_DELTAS.items()
           if tuple(v+d for v,d in zip(row[:3],delta)) not in occupied]
    return {'version':1,'size':nbt['size'],'anchor':meta['anchor'],
            'centerPivot':meta['center_pivot'],'front':meta['front'],
            'groundBlockY':meta['ground_block_y'],'palette':nbt['palette'],
            'blocks':blocks,'exposedFaces':faces}


def client_bytes(nbt,meta):
    return (json.dumps(client_mesh(nbt,meta),ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')


def build():
    nbt,meta=design()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_bytes(encode(nbt))
    dump(DOC/'geometry.json',meta)
    CLIENT_OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    CLIENT_OUTPUT.write_bytes(client_bytes(nbt,meta))


def check():
    nbt=read_nbt();meta=json.loads((DOC/'geometry.json').read_text())
    palette=[s['Name'].removeprefix('minecraft:') for s in nbt['palette']]
    b={tuple(row['pos']):palette[row['state']] for row in nbt['blocks']}
    tests=[]
    def test(name,ok):tests.append({'name':name,'passed':bool(ok)})
    test('bounds and standard data version',nbt['size']==list(SIZE) and nbt['DataVersion']==3465 and all(all(0<=v<SIZE[i] for i,v in enumerate(p)) for p in b))
    test('unique sparse occupied voxels',len(b)==len(nbt['blocks']) and 'air' not in palette)
    allowed={WOOD,ROOF,WALL,'sandstone','cut_sandstone','polished_deepslate','spruce_planks',
             'red_terracotta','orange_terracotta','yellow_terracotta','ochre_froglight'}
    test('vanilla opaque static full cubes only',set(palette)<=allowed)
    test('no entities or block entity payload',nbt['entities']==[] and all(set(row)=={'pos','state'} for row in nbt['blocks']))
    expected,_=design()
    test('export source matches decoded production NBT',nbt==expected)
    test('repeated generation byte identical',OUTPUT.read_bytes()==encode(design()[0])==encode(design()[0]))
    client=json.loads(CLIENT_OUTPUT.read_text())
    test('client palette complete and identical to NBT',client['palette']==nbt['palette'])
    test('client blocks identical to NBT in order and state',client['blocks']==[row['pos']+[row['state']] for row in nbt['blocks']])
    test('client schema and local-space coordinate contract',client['version']==1 and client['size']==list(SIZE)
         and client['anchor']==[22,1,0] and client['centerPivot']==[22,1,16]
         and client['groundBlockY']==0 and client['front']=='-Z'
         and meta['runtime_walking_surface_y']==0 and meta['runtime_origin']=='center_pivot')
    test('client mesh deterministic bytes',CLIENT_OUTPUT.read_bytes()==client_bytes(*design())==client_bytes(*design()))
    # Independent set reconstruction from decoded NBT, with explicit vanilla axes.
    states={tuple(row['pos']):row['state'] for row in nbt['blocks']}
    expected_faces=set()
    for (x,y,z),state in states.items():
        for neighbor,face in [((x,y-1,z),'down'),((x,y+1,z),'up'),((x,y,z-1),'north'),
                              ((x,y,z+1),'south'),((x-1,y,z),'west'),((x+1,y,z),'east')]:
            if neighbor not in states:expected_faces.add((x,y,z,state,face))
    actual_faces={tuple(row) for row in client['exposedFaces']}
    test('every client face exactly matches NBT exposed face and vanilla direction',actual_faces==expected_faces
         and len(actual_faces)==len(client['exposedFaces']))
    seen={next(iter(b))};queue=deque(seen)
    while queue:
        p=queue.popleft()
        for delta in DIRS:
            q=tuple(x+d for x,d in zip(p,delta))
            if q in b and q not in seen:seen.add(q);queue.append(q)
    test('every block face-connected to ground assembly',len(seen)==len(b))
    test('unobstructed eight-wide central lane',all((x,y,z) not in b and (x,0,z) in b for x in range(18,26) for y in range(1,4) for z in range(32)))
    def walkable(x,z):return (x,0,z) in b and (x,1,z) not in b and (x,2,z) not in b
    walked={(22,0)};queue=deque(walked)
    while queue:
        x,z=queue.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            p=(x+dx,z+dz)
            if p not in walked and walkable(*p):walked.add(p);queue.append(p)
    for shop in meta['shops']:
        x,_,z=shop['inside']
        test(shop['name_zh']+' open door reaches real interior',(x,z) in walked)
    test('four shops and one gate layout',len(meta['shops'])==4 and len(set(s['wall_height'] for s in meta['shops']))==3)
    test('six restrained static lamp voxels',Counter(b.values())['ochre_froglight']==6)
    test('no automatic placement registration',not any((ROOT/f'src/main/resources/data/dynasty/worldgen/{kind}/scenic_mirage_street.json').exists() for kind in ('structure','structure_set','template_pool')))
    selected=json.loads((DOC/'references/selected-100.json').read_text())
    history=json.loads((DOC/'references/prior-manifests.json').read_text())
    prior=set();count=0
    for entry in history['sources']:
        path=ROOT/entry['path'];d=json.loads(path.read_text());rows=d if isinstance(d,list) else d['references']
        prior.update(r['sha256'] for r in rows);count+=len(rows)
        test('prior reference manifest unchanged: '+entry['path'],sha(path)==entry['sha256'])
    refs={row['sha256'] for row in selected}
    test('100 images unique against previous 900 references',len(selected)==len(refs)==100 and count==900 and not refs & prior)
    stone=json.loads(STONE_REFERENCES.read_text())['references']
    stone_overlap=refs & {r['sha256'] for r in stone}
    test('no overlap with concurrent stone god reference batch',len(stone)==100 and not stone_overlap)
    test('selected cached images match individually observed references',all(sha(DOC/'references'/row['file'])==row['sha256'] and row['observation_zh'] for row in selected))
    exposed=sum(tuple(v+d for v,d in zip(p,delta)) not in b for p in b for delta in DIRS)
    report={'status':'PASS' if all(t['passed'] for t in tests) else 'FAIL','tests':tests,
            'nbt_sha256':sha(OUTPUT),'source_sha256':sha(Path(__file__)),'client_json_sha256':sha(CLIENT_OUTPUT),
            'client_json_bytes':CLIENT_OUTPUT.stat().st_size,'client_exposed_faces':len(actual_faces),
            'stone_reference_index_sha256':sha(STONE_REFERENCES),'stone_reference_count':len(stone),
            'stone_reference_overlap':len(stone_overlap),
            'occupied_voxels':len(b),'exposed_faces':exposed,'palette_counts':dict(Counter(b.values())),
            'connected_voxels':len(seen),'reachable_floor_cells':len(walked),
            'java_executed':False,'native_game_verified':False,'placement_performed':False}
    dump(DOC/'checks.json',report)
    if report['status']!='PASS':raise AssertionError([t['name'] for t in tests if not t['passed']])
    print(json.dumps({k:v for k,v in report.items() if k not in ('tests','palette_counts')},ensure_ascii=False),flush=True)
    return b,meta,report


def review():
    import numpy as np
    from PIL import Image,ImageDraw
    sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
    import texture_review as r
    b,meta,report=check()
    client=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar'
    if not client.exists():client=client.with_name('client.jar')
    textures={};texture_hashes={}
    with zipfile.ZipFile(client) as z:
        def texture(name,face):
            horizontal=face in ('up','down')
            key={'sandstone':'sandstone_top' if face=='up' else 'sandstone_bottom' if face=='down' else 'sandstone',
                 'smooth_sandstone':'sandstone_top',
                 'cut_sandstone':'sandstone_top' if horizontal else 'cut_sandstone',
                 WOOD:WOOD+'_top' if horizontal else WOOD,
                 'ochre_froglight':'ochre_froglight_top' if horizontal else 'ochre_froglight_side'}.get(name,name)
            if key not in textures:
                raw=z.read('assets/minecraft/textures/block/'+key+'.png')
                textures[key]=np.array(Image.open(io.BytesIO(raw)).convert('RGB'))
                assert textures[key].shape==(16,16,3)
                texture_hashes[key]=hashlib.sha256(raw).hexdigest()
            return textures[key]
        delta={'north':(0,0,-1),'south':(0,0,1),'east':(-1,0,0),'west':(1,0,0),'up':(0,1,0),'down':(0,-1,0)}
        quads=[]
        for p,name in b.items():
            for face,corners in r.r.FACES.items():
                if tuple(v+d for v,d in zip(p,delta[face])) in b:continue
                quads.append(((np.array(corners)+p)*16,{'uv':[0,0],'uv_size':[16,16],'_tex':texture(name,face)},'building'))
        assert len(quads)==report['exposed_faces']
    # Review-only actual-size person at street entrance, feet on y=1. Not in NBT.
    scene=quads+r.references(np.array([22.75*16,16,0]))
    points=np.concatenate([q[0] for q in scene]);fallback=np.zeros((16,16,3),dtype=np.uint8)
    foot='软件预览 · 实际NBT与原版PNG · 原比例1.8米参照人 · 无粒子 · 非游戏截图'
    views=[('front',0,10),('back',180,10),('left',-90,10),('right',90,10),('three-quarter',45,22)]
    for label,yaw,elevation in views:
        r.labelled(r.raster(scene,fallback,yaw=yaw,elevation=elevation,size=(1280,900),mode='lit',frame_points=points),'蜃楼幻市 / '+label,foot).save(DOC/(label+'.png'))
        print('rendered',label,flush=True)
    for mode in ('gray','dim'):
        q=[(v,dict(uv,_tex=np.full((16,16,3),170,dtype=np.uint8)),bn) for v,uv,bn in scene] if mode=='gray' else scene
        r.labelled(r.raster(q,fallback,yaw=45,elevation=22,size=(1280,900),mode='lit' if mode=='gray' else 'dim',frame_points=points),'蜃楼幻市 / '+mode,foot).save(DOC/(mode+'.png'))
    black=[(v,dict(uv,_tex=fallback),bn) for v,uv,bn in quads]
    r.labelled(r.raster(black,fallback,yaw=0,elevation=0,size=(1280,900),mode='unlit',frame_points=points),'蜃楼幻市 / 纯黑剪影','软件剪影 · 实际NBT全体建筑 · 正视、无特效 · 非游戏截图').save(DOC/'silhouette.png')
    # Near eye-level view down the street, with unchanged coordinates and scale.
    offset=np.array([22*16,16,0])
    street=[(v-offset,uv,bn) for v,uv,bn in scene]
    r.labelled(r.raster(street,fallback,yaw=0,distance=24,size=(1280,900),mode='lit'),'蜃楼幻市 / 街口24米','软件透视 · 1.62米视高 / 70°垂直FOV · 实际NBT · 非游戏截图').save(DOC/'street-24m.png')
    inside=[(v-np.array([22*16,16,12*16]),uv,bn) for v,uv,bn in scene]
    r.labelled(r.raster(inside,fallback,yaw=0,distance=4,size=(1280,900),mode='lit'),'蜃楼幻市 / 街内门面','软件透视 · 相机位于街内z=8 / 1.62米视高 · 实际NBT · 非游戏截图').save(DOC/'street-inside.png')
    plan=Image.new('RGB',(44,32),(235,229,209))
    for x in range(44):
        for zz in range(32):
            if (x,1,zz) in b:plan.putpixel((x,zz),(71,61,51))
            elif (x,0,zz) in b:plan.putpixel((x,zz),(169,179,164) if 18<=x<=25 else (209,187,137))
    plan=plan.resize((1056,768),Image.Resampling.NEAREST)
    r.labelled(plan,'蜃楼幻市 / 地面平面','深色=一格高处实体；绿色=中街；浅黄=可用地面。软件检查。').save(DOC/'plan.png')
    dump(DOC/'preview.json',{'nbt_sha256':sha(OUTPUT),'source':'actual production NBT and vanilla 1.20.1 PNG',
          'native_screenshot':False,'texture_source':str(client),'texture_png_sha256':texture_hashes,
          'exposed_faces':len(quads),'views':[v[0] for v in views]+['gray','dim','silhouette','street-24m','street-inside','plan'],
          'gray_mode':'uniform neutral geometry material, not desaturated textures',
          'person_height_blocks':1.8,'person_ground_y':1})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--review',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.review:review()
    elif args.check:check()
    else:build();check()
