#!/usr/bin/env python3
"""Original upright Chinese water palace; deterministic offline voxel assets.

Client visual data only. No placement, Java, saves, worldgen, audio or device UI.
NBT and client version-1 JSON share the same unshifted local coordinates.
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
DOC = ROOT/'docs/art/cod3-dragon-palace-mirage-v2'
OUTPUT = ROOT/'src/main/resources/data/dynasty/structures/scenic_dragon_palace_mirage.nbt'
CLIENT_OUTPUT = ROOT/'src/main/resources/assets/dynasty/scenic/dragon_palace_mirage.json'
SIZE = (48,24,40)
PIVOT = [24,0,20]
FACE_DELTAS = {'down':(0,-1,0),'up':(0,1,0),'north':(0,0,-1),
               'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}
DIRS = tuple(FACE_DELTAS.values())
STONE = 'smooth_quartz'
EDGE = 'dark_prismarine'
TILE = 'prismarine_bricks'
POST = 'quartz_pillar'
WOOD = 'dark_oak_planks'
ALLOWED = {STONE,EDGE,TILE,POST,WOOD,'polished_diorite','sea_lantern','gold_block'}


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def utf(s):
    raw=s.encode('utf-8')
    return struct.pack('>H',len(raw))+raw


def kind(v):
    return 10 if isinstance(v,dict) else 9 if isinstance(v,list) else 8 if isinstance(v,str) else 3


def payload(v):
    t=kind(v)
    if t==3:return struct.pack('>i',v)
    if t==8:return utf(v)
    if t==10:return b''.join(bytes([kind(a)])+utf(k)+payload(a) for k,a in v.items())+b'\0'
    sub=kind(v[0]) if v else 10
    assert all(kind(a)==sub for a in v)
    return bytes([sub])+struct.pack('>i',len(v))+b''.join(payload(a) for a in v)


def encode(nbt):
    out=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=9) as f:
        f.write(b'\x0a\0\0'+payload(nbt))
    return out.getvalue()


class Reader:
    def __init__(self,b):self.f=io.BytesIO(b)
    def read(self,fmt):return struct.unpack(fmt,self.f.read(struct.calcsize(fmt)))[0]
    def string(self):return self.f.read(self.read('>H')).decode('utf-8')
    def value(self,t):
        if t==3:return self.read('>i')
        if t==8:return self.string()
        if t==9:
            sub=self.read('>B')
            return [self.value(sub) for _ in range(self.read('>i'))]
        if t==10:
            d={}
            while (sub:=self.read('>B')):
                name=self.string();d[name]=self.value(sub)
            return d
        raise ValueError(t)


def read_nbt():
    r=Reader(gzip.decompress(OUTPUT.read_bytes()))
    assert r.read('>B')==10 and r.string()==''
    nbt=r.value(10)
    assert r.f.read()==b''
    return nbt


def design():
    b={};roofs=[];lights=[];columns=[]
    def put(x,y,z,name):
        assert all(0<=v<SIZE[i] for i,v in enumerate((x,y,z))),(x,y,z)
        if name is None:b.pop((x,y,z),None)
        else:b[x,y,z]=name
    def box(x0,y0,z0,x1,y1,z1,name):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):put(x,y,z,name)
    def column(x,z,bottom,top):
        box(x,bottom,z,x,top,z,POST)
        put(x,bottom,z,EDGE);put(x,top,z,WOOD)
        columns.append([x,bottom,z,top])
    def roof(name,x0,z0,x1,z1,y,ridge=True):
        # Broad low hip roof, joined through explicit risers. Tile field is
        # lighter than the dark edge; a short continuous corner upturn reads
        # as an eave rather than an isolated castle merlon.
        for x in range(x0,x1+1):
            for z in range(z0,z1+1):
                inset=min(x-x0,x1-x,z-z0,z1-z)
                top=y+min(3,inset//2)
                put(x,top,z,EDGE if inset==0 else TILE)
                if inset in (2,4,6):put(x,top-1,z,TILE)
                if inset==1:put(x,top-1,z,WOOD)
        if ridge:
            # All major roofs have ridge along X, facing the ceremonial axis.
            center=(z0+z1)//2;top=y+min(3,(z1-z0)//4)+1
            box(x0+3,top,center,x1-3,top,center,EDGE)
            for x in (x0+3,x1-3):put(x,top+1,center,'gold_block')
        for x in (x0,x1):
            for z in (z0,z1):
                sx=1 if x==x0 else -1;sz=1 if z==z0 else -1
                for xx,zz in ((x,z),(x+sx,z),(x,z+sz)):put(xx,y+1,zz,EDGE)
        roofs.append({'name_zh':name,'bounds_xz':[x0,z0,x1,z1],'eave_y':y})
    def lamp(x,y,z):
        put(x,y,z,'sea_lantern');lights.append([x,y,z])

    # Three broad terraces. The first block starts at the waterline y=0.
    # There is no full rectangular terrain tile beneath the two water courts.
    box(10,0,17,37,0,37,'polished_diorite')
    box(11,1,18,36,1,36,STONE)
    box(12,2,19,35,3,35,STONE)
    for x in (12,35):box(x,3,19,x,3,35,EDGE)
    for z in (19,35):box(12,3,z,35,3,z,EDGE)
    # Main bridge leaves open water under the deck between supported piers.
    box(21,1,0,26,1,16,'polished_diorite')
    for z in (0,5,10,14):box(21,0,z,26,0,z,EDGE)
    for z,top in ((14,1),(15,2),(16,3)):
        box(21,0,z,26,top,z,STONE)
    box(21,0,17,26,3,20,STONE)
    for x in (20,27):
        for z in (1,5,9,13):
            box(x,0,z,x,2,z,EDGE)
            put(x,3,z,STONE)
        box(x,2,1,x,2,13,STONE)

    # Two low water galleries: thin roof strips and real pillar gaps, joined
    # to the main terrace; no copy of a four-shop street or shopfront frames.
    for x0,x1 in ((6,10),(37,41)):
        box(x0,1,9,x1,1,29,'polished_diorite')
        for z in (10,16,22,28):
            for x in (x0,x1):
                put(x,0,z,EDGE);column(x,z,2,7)
        for x in (x0,x1):box(x,7,10,x,7,29,WOOD)
        roof('西水廊' if x0<24 else '东水廊',x0-1,10,x1+1,29,8,False)
        # The narrow roof's longitudinal ridge follows the gallery direction.
        cx=(x0+x1)//2;box(cx,10,12,cx,10,27,EDGE)
        for z in (13,25):
            put(cx,8,z,WOOD);lamp(cx,7,z)
    # Side approach steps align the raised main floor with the lower galleries.
    for x,top in ((10,1),(11,2),(12,3),(13,3),(34,3),(35,3),(36,2),(37,1)):
        box(x,0,26,x,top,29,STONE)

    # Twin entry que pavilions, open between their columns, below the main hall.
    for x0,x1,name in ((5,13,'西阙'),(34,42,'东阙')):
        box(x0,0,3,x1,0,10,EDGE)
        box(x0,1,3,x1,1,10,STONE)
        for x in (x0+1,x1-1):
            for z in (4,9):column(x,z,2,7)
        for z in (4,9):box(x0+1,7,z,x1-1,7,z,WOOD)
        for x in (x0+1,x1-1):box(x,7,4,x,7,9,WOOD)
        # Back screen has a broad rectangular opening; no door blocks/entities.
        box(x0+2,2,9,x1-2,5,9,STONE)
        box(x0+3,2,9,x1-3,4,9,None)
        roof(name,x0-1,2,x1+1,11,8)
        lamp((x0+x1)//2,6,4)

    # Central main hall. Its three front bays and side/back windows are actual
    # cavities, with the broad roof held by a column-and-beam ring.
    box(14,4,21,14,11,33,STONE);box(33,4,21,33,11,33,STONE)
    box(14,4,33,33,11,33,STONE)
    for x in (14,20,27,33):
        for z in (21,33):column(x,z,4,11)
    for x in (14,33):
        for z in (25,29):column(x,z,4,11)
        # Window sits between z=25/29 columns; do not sever a support shaft.
        box(x,6,26,x,8,28,None)
        box(x,4,27,x,6,28,None)
    for x0,x1 in ((17,19),(28,30)):
        box(x0,6,33,x1,8,33,None)
    box(14,10,21,33,11,21,WOOD)
    box(14,10,33,33,11,33,WOOD)
    for x in (14,33):box(x,11,21,x,11,33,WOOD)
    # Small bronze/gold joints, not an all-gold facade.
    for x in (14,20,27,33):put(x,10,20,'gold_block')
    roof('主殿下檐',12,19,35,35,12)
    # Upper clerestory is connected to the lower roof/column ring, with a real
    # open center. The second roof is centered and much smaller than the first.
    box(19,13,25,28,17,29,None)
    for x in (18,29):
        for z in (24,30):column(x,z,12,17)
        box(x,14,24,x,16,30,STONE)
        box(x,15,26,x,16,28,None)
    for z in (24,30):
        box(18,14,z,29,16,z,WOOD)
        for x0,x1 in ((20,22),(25,27)):box(x0,15,z,x1,16,z,None)
        box(18,17,z,29,17,z,WOOD)
    for x in (18,29):box(x,17,24,x,17,30,WOOD)
    roof('主殿上檐',16,22,31,32,18)
    # Interior ceremonial pearl stand: pure geometry, no throne occupant,
    # container, inventory, spawner, interaction or hidden logic.
    box(21,4,30,26,4,32,EDGE)
    box(22,5,30,25,5,31,STONE)
    lamp(23,6,31);lamp(24,6,31)
    for x in (15,32):
        for z in (22,32):lamp(x,10,z)
    palette=sorted(set(b.values()));index={name:i for i,name in enumerate(palette)}
    states=[dict(Name='minecraft:'+name,**({'Properties':{'axis':'y'}} if name==POST else {})) for name in palette]
    nbt={'DataVersion':3465,'size':list(SIZE),'palette':states,
         'blocks':[{'pos':list(p),'state':index[name]} for p,name in sorted(b.items())],'entities':[]}
    meta={'id':'dynasty:scenic_dragon_palace_mirage','name_zh':'水中倒城·龙宫幻影','event_id':17,
          'size':list(SIZE),'anchor':[24,0,0],'center_pivot':PIVOT,'front':'-Z','street_axis':'+Z',
          'ground_block_y':0,'water_plane_y':0,'main_hall_floor_y':4,'bridge_walk_y':2,
          'runtime_origin':'center_pivot','runtime_transform':'world = waterCenter + rotation(local - [24,0,20])',
          'runtime_water_plane_y':0,'upright':True,'pre_mirrored':False,
          'water_courts':[{'bounds_xz':[14,3,19,15]},{'bounds_xz':[28,3,33,15]}],
          'landmarks':{'entry':[24,2,0],'main_entry':[24,4,22],
                       'west_gallery':[8,2,20],'east_gallery':[39,2,20],
                       'west_que':[9,2,6],'east_que':[38,2,6]},
          'roofs':roofs,'columns':columns,'lights':lights,'single_lod':True,
          'client_visual_only':True,'place_in_world':False,'automatic_worldgen':False,
          'event_contract':{'dimension':'dynasty:dragon_palace','duration_ticks':1200,
                            'distance':'medium','lods':1,'effect_budget':150,
                            'sound':'water ambience; integration only, no playback'},
          'geometry_notes':'Original axial palace, triple terrace, twin que pavilions, two low water galleries, open courts. Upright only.'}
    return nbt,meta


def client_mesh(nbt,meta):
    blocks=[row['pos']+[row['state']] for row in nbt['blocks']]
    occupied={tuple(row[:3]) for row in blocks}
    faces=[row+[face] for row in blocks for face,delta in FACE_DELTAS.items()
           if tuple(v+d for v,d in zip(row[:3],delta)) not in occupied]
    return {'version':1,'size':nbt['size'],'anchor':meta['anchor'],'centerPivot':meta['center_pivot'],
            'front':meta['front'],'groundBlockY':meta['ground_block_y'],'palette':nbt['palette'],
            'blocks':blocks,'exposedFaces':faces}


def client_bytes(nbt,meta):
    return (json.dumps(client_mesh(nbt,meta),ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')


def build():
    nbt,meta=design()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_bytes(encode(nbt))
    CLIENT_OUTPUT.parent.mkdir(parents=True,exist_ok=True);CLIENT_OUTPUT.write_bytes(client_bytes(nbt,meta))
    dump(DOC/'geometry.json',meta)


def check():
    nbt=read_nbt();meta=json.loads((DOC/'geometry.json').read_text());client=json.loads(CLIENT_OUTPUT.read_text())
    palette=[s['Name'].removeprefix('minecraft:') for s in nbt['palette']]
    b={tuple(r['pos']):palette[r['state']] for r in nbt['blocks']};tests=[]
    def test(name,ok):tests.append({'name':name,'passed':bool(ok)})
    test('within 48x24x40 bounded standard NBT',nbt['size']==list(SIZE) and nbt['DataVersion']==3465
         and all(all(0<=v<SIZE[i] for i,v in enumerate(p)) for p in b))
    test('opaque static vanilla full cubes only',set(palette)<=ALLOWED)
    test('no entities block entities explicit air or block logic',nbt['entities']==[] and 'air' not in palette
         and all(set(r)=={'pos','state'} for r in nbt['blocks']))
    test('no duplicate occupied positions',len(b)==len(nbt['blocks']))
    expected,emeta=design()
    test('editable source matches actual NBT and metadata',expected==nbt and meta==emeta)
    test('repeat NBT export byte identical',encode(design()[0])==encode(design()[0])==OUTPUT.read_bytes())
    test('complete identical client palette and blocks',client['palette']==nbt['palette'] and client['blocks']==[r['pos']+[r['state']] for r in nbt['blocks']])
    test('client JSON deterministic',client_bytes(*design())==client_bytes(*design())==CLIENT_OUTPUT.read_bytes())
    test('upright waterline and center coordinate contract',meta['upright'] and not meta['pre_mirrored']
         and client['centerPivot']==PIVOT and client['anchor']==[24,0,0] and client['groundBlockY']==0
         and client['front']=='-Z' and client['version']==1 and client['size']==list(SIZE)
         and meta['water_plane_y']==meta['runtime_water_plane_y']==0 and min(p[1] for p in b)==0)
    states={tuple(r['pos']):r['state'] for r in nbt['blocks']};face_set=set()
    for (x,y,z),state in states.items():
        for neighbor,face in [((x,y-1,z),'down'),((x,y+1,z),'up'),((x,y,z-1),'north'),
                              ((x,y,z+1),'south'),((x-1,y,z),'west'),((x+1,y,z),'east')]:
            if neighbor not in states:face_set.add((x,y,z,state,face))
    test('all NBT exterior and cavity faces match client with vanilla axes',face_set=={tuple(r) for r in client['exposedFaces']}
         and len(face_set)==len(client['exposedFaces']))
    test('exposed face budget below 10000',len(face_set)<10000)
    seen={next(iter(b))};q=deque(seen)
    while q:
        p=q.popleft()
        for d in DIRS:
            v=tuple(a+dd for a,dd in zip(p,d))
            if v in b and v not in seen:seen.add(v);q.append(v)
    test('all columns roofs beams and foundations face-connected',seen==set(b))
    test('each recorded column remains solid through its full support height',all((x,y,z) in b
         for x,bottom,z,top in meta['columns'] for y in range(bottom,top+1)))
    test('two true open water courts without fake water tiles',all((x,y,z) not in b for court in meta['water_courts']
         for x in range(court['bounds_xz'][0],court['bounds_xz'][2]+1)
         for z in range(court['bounds_xz'][1],court['bounds_xz'][3]+1) for y in range(4)))
    test('main hall three bays and genuine interior space',all((x,y,z) not in b for x in range(21,27) for y in range(4,9) for z in range(21,29)))
    # Walkability is a geometric check only. The mirage has no world collision.
    def walkable(p):
        x,y,z=p
        return p not in b and (x,y+1,z) not in b and (x,y-1,z) in b
    start=tuple(meta['landmarks']['entry']);walked={start};q=deque(walked)
    while q:
        x,y,z=q.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (-1,0,1):
                p=(x+dx,y+dy,z+dz)
                if p in walked or not walkable(p):continue
                # Upsteps require head clearance at the departure cell too.
                if dy==1 and (x,y+2,z) in b:continue
                walked.add(p);q.append(p)
    test('entry on real supported deck',walkable(start))
    for name,p in meta['landmarks'].items():test('route reaches '+name,tuple(p) in walked)
    test('no structure or worldgen registration',not any((ROOT/f'src/main/resources/data/dynasty/worldgen/{folder}/scenic_dragon_palace_mirage.json').exists() for folder in ('structure','structure_set','template_pool')))
    selected=json.loads((DOC/'references/selected-100.json').read_text());history=json.loads((DOC/'references/prior-manifests.json').read_text())
    prior=set();prior_count=0
    for source in history['sources']:
        path=ROOT/source['path'];d=json.loads(path.read_text());rows=d if isinstance(d,list) else d['references']
        prior.update(row['sha256'] for row in rows);prior_count+=len(rows)
        test('prior reference manifest stable '+source['path'],sha(path)==source['sha256'])
    ref_hashes={r['sha256'] for r in selected}
    test('100 new image hashes against 1100 prior records',len(selected)==len(ref_hashes)==100 and prior_count==1100 and not ref_hashes&prior)
    test('individually viewed cached reference image hashes match',all(r['observation_zh'] and sha(DOC/'references'/r['file'])==r['sha256'] for r in selected))
    report={'status':'PASS' if all(t['passed'] for t in tests) else 'FAIL','tests':tests,
            'source_sha256':sha(Path(__file__)),'nbt_sha256':sha(OUTPUT),'client_json_sha256':sha(CLIENT_OUTPUT),
            'occupied_voxels':len(b),'exposed_faces':len(face_set),'connected_voxels':len(seen),
            'reachable_floor_cells':len(walked),'palette_counts':dict(Counter(b.values())),
            'occupied_bounds':{'min':[min(p[i] for p in b) for i in range(3)],'max_inclusive':[max(p[i] for p in b) for i in range(3)]},
            'native_game_verified':False,'java_executed':False,'world_placement_performed':False}
    dump(DOC/'checks.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('tests','palette_counts')},ensure_ascii=False),flush=True)
    if report['status']!='PASS':raise AssertionError([t['name'] for t in tests if not t['passed']])
    return b,meta,report


def review():
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
    import texture_review as r
    b,meta,report=check();textures={};hashes={}
    client=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar'
    if not client.exists():client=client.with_name('client.jar')
    with zipfile.ZipFile(client) as z:
        def texture(name,face):
            key='quartz_block_bottom' if name==STONE else 'quartz_pillar_top' if name==POST and face in ('up','down') else name
            if key not in textures:
                raw=z.read('assets/minecraft/textures/block/'+key+'.png')
                im=Image.open(io.BytesIO(raw)).convert('RGB')
                assert im.width==16 and im.height>=16 and im.height%16==0
                # Animated vanilla block textures (sea lantern) use frame zero
                # for static software review; original PNG hash remains intact.
                textures[key]=np.array(im.crop((0,0,16,16)))
                hashes[key]=hashlib.sha256(raw).hexdigest()
            return textures[key]
        # The existing read-only software helper names east/west oppositely.
        # Map its corners explicitly; exported client directions are vanilla.
        delta=dict(FACE_DELTAS,east=(-1,0,0),west=(1,0,0))
        quads=[]
        for p,name in b.items():
            for face,corners in r.r.FACES.items():
                if tuple(a+d for a,d in zip(p,delta[face])) in b:continue
                quads.append(((np.array(corners)+p)*16,{'uv':[0,0],'uv_size':[16,16],'_tex':texture(name,face)},'building'))
        assert len(quads)==report['exposed_faces']
    # Original 1.8m reference person and 1m reference blocks stand on the actual
    # front bridge, at y=2. They are review-only and absent from the exports.
    scene=quads+r.references(np.array([24.75*16,2*16,1*16]))
    points=np.concatenate([q[0] for q in scene]);fallback=np.zeros((16,16,3),dtype=np.uint8)
    foot='软件预览 · 实际NBT+原版PNG · 1.8米玩家/1米方块 · 正立无倒影 · 非游戏截图'
    views=[('front',0,12),('back',180,12),('left',-90,12),('right',90,12),('three-quarter',45,24)]
    for label,yaw,elevation in views:
        r.labelled(r.raster(scene,fallback,yaw=yaw,elevation=elevation,size=(1280,960),mode='lit',frame_points=points),'水中倒城·龙宫幻影 / '+label,foot).save(DOC/(label+'.png'))
        print('rendered',label,flush=True)
    gray=[(v,dict(uv,_tex=np.full((16,16,3),170,dtype=np.uint8)),bone) for v,uv,bone in scene]
    r.labelled(r.raster(gray,fallback,yaw=45,elevation=24,size=(1280,960),mode='lit',frame_points=points),'龙宫幻影 / 无纹理灰模',foot).save(DOC/'gray.png')
    r.labelled(r.raster(scene,fallback,yaw=45,elevation=24,size=(1280,960),mode='dim',frame_points=points),'龙宫幻影 / 暗光',foot).save(DOC/'dim.png')
    black=[(v,dict(uv,_tex=fallback),bone) for v,uv,bone in quads]
    r.labelled(r.raster(black,fallback,yaw=0,elevation=0,size=(1280,960),mode='unlit',frame_points=points),'龙宫幻影 / 正面黑影','软件剪影 · 全部真实NBT体素 · 无粒子/水雾/倒影 · 非游戏截图').save(DOC/'silhouette.png')
    # Normal eye-level approach. Camera remains above the deck (eye=3.62),
    # not below the waterline; this is an unmirrored perspective geometry check.
    approach=[(v-np.array([24*16,2*16,0]),uv,bone) for v,uv,bone in scene]
    r.labelled(r.raster(approach,fallback,yaw=0,distance=28,size=(1280,960),mode='lit'),'龙宫幻影 / 28米入口视角','软件透视 · 70°垂直FOV / 桥面上1.62米视高 · 正立无倒影 · 非游戏截图').save(DOC/'approach-28m.png')
    plan=Image.new('RGB',(48,40),(207,223,225))
    for x in range(48):
        for zz in range(40):
            cells=[(y,v) for (xx,y,z0),v in b.items() if xx==x and z0==zz]
            if cells:
                top=max(y for y,_ in cells)
                plan.putpixel((x,zz),(50,100,111) if top>=8 else (201,197,174) if top>=3 else (232,231,219))
    r.labelled(plan.resize((960,800),Image.Resampling.NEAREST),'龙宫幻影 / 占地平面','深青=高屋盖；米色=台基；白色=低桥廊；浅蓝=未导出体素的留空。').save(DOC/'plan.png')
    dump(DOC/'preview.json',{'source':'actual exported NBT + actual vanilla PNG pixels','native_screenshot':False,
          'nbt_sha256':sha(OUTPUT),'client_json_sha256':sha(CLIENT_OUTPUT),'texture_source':str(client),
          'texture_png_sha256':hashes,'exposed_faces':len(quads),'person_height':1.8,'person_feet_y':2,
          'water_plane_y':0,'pre_mirrored':False,'gray_mode':'uniform neutral material, not desaturated texture',
          'views':[v[0] for v in views]+['gray','dim','silhouette','approach-28m','plan']})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--review',action='store_true');args=parser.parse_args()
    if args.review:review()
    elif args.check:check()
    else:build();check()
