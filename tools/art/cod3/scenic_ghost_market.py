#!/usr/bin/env python3
"""Original secluded valley ghost market; deterministic static voxel assets.

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
DOC = ROOT/'docs/art/cod3-ghost-market-v2'
OUTPUT = ROOT/'src/main/resources/data/dynasty/structures/scenic_ghost_market.nbt'
CLIENT_OUTPUT = ROOT/'src/main/resources/assets/dynasty/scenic/ghost_market.json'
SIZE = (28,16,44)
PIVOT = [14,0,22]
FACE_DELTAS = {'down':(0,-1,0),'up':(0,1,0),'north':(0,0,-1),
               'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}
DIRS = tuple(FACE_DELTAS.values())
WOOD = 'dark_oak_log_y'
ALLOWED = {'stone','cobblestone','mossy_cobblestone','deepslate_bricks','cracked_deepslate_bricks',
           'deepslate_tiles','dark_oak_planks','dark_oak_log','gray_wool','purple_wool',
           'verdant_froglight','bookshelf','dried_kelp_block','dark_prismarine','waxed_oxidized_copper'}


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


def lane_center(z):
    return 14 if z<16 else 13 if z<29 else 14


def design():
    b={};shops=[];lights=[];supports=[];gates=[]
    def put(x,y,z,t):
        assert 0<=x<SIZE[0] and 0<=y<SIZE[1] and 0<=z<SIZE[2],(x,y,z)
        if t is None:b.pop((x,y,z),None)
        else:b[x,y,z]=t
    def box(x0,y0,z0,x1,y1,z1,t):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):put(x,y,z,t)
    def post(x,z,top):
        box(x,1,z,x,top,z,WOOD);supports.append({'base':[x,0,z],'top':[x,top,z]})
    # Uneven-edged common stone terrace; no enclosed rectangular terrain slab.
    for z in range(44):
        edge=5 if z<2 or z>41 else 2 if z<6 else 0
        for x in range(edge,28-edge):
            c=lane_center(z)
            t='deepslate_bricks' if c-3<=x<=c+3 else 'cobblestone'
            if x in (c-4,c+4):t='mossy_cobblestone'
            put(x,0,z,t)
    # Broad separate rock shoulders, with low gaps and changing thickness.
    # Avoid two flat continuous retaining walls masquerading as a valley.
    for z in range(6,42):
        wz=(z-6)%13;ez=(z-4)%15
        west=2+min(wz,12-wz)//2;east=2+min(ez,14-ez)//2
        ww=2+min(2,min(wz,12-wz)//2);ew=2+min(2,min(ez,14-ez)//2)
        for x in range(0,ww):
            h=max(1,west-x//2)
            box(x,1,z,x,h,z,'stone')
            if x==ww-1:put(x,h,z,'mossy_cobblestone')
        for x in range(28-ew,28):
            h=max(1,east-(27-x)//2)
            box(x,1,z,x,h,z,'stone')
            if x==28-ew:put(x,h,z,'mossy_cobblestone')
    def lamp(x,y,z,root_x):
        # Full-cube symbolic lamp hanging from a physically joined bracket.
        box(min(x,root_x),y+1,z,max(x,root_x),y+1,z,'dark_oak_log_x')
        put(x,y,z,'verdant_froglight')
        lights.append({'center':[x+.5,y+.5,z+.5],'voxel':[x,y,z],'kind':'supported_static_lamp','axis':'y'})
    def stall(name,x0,z0,x1,z1,west,height,cloth,goods,room=False):
        front=x1 if west else x0;back=x0 if west else x1
        inner=front-1 if west else front+1;mid=(z0+z1)//2
        # A three-sided shed, with a large genuinely open frontage.
        box(x0,1,z0,x1,2,z0,'deepslate_bricks')
        box(x0,1,z1,x1,2,z1,'deepslate_bricks')
        box(back,1,z0,back,height-1,z1,'dark_oak_planks')
        for x in (x0,x1):
            for z in (z0,z1):post(x,z,height)
        for z in (z0,z1):box(x0,height,z,x1,height,z,'dark_oak_log_x')
        box(front,height,z0,front,height,z1,'dark_oak_log_z')
        box(back,height,z0,back,height,z1,'dark_oak_log_z')
        # Front canopy lower than the rear ridge, each riser joined underneath.
        for x in range(x0,x1+1):
            offset=abs(x-front);top=height+1+offset//3
            box(x,top,z0-1,x,top,z1+1,'deepslate_tiles' if room else 'gray_wool')
            if offset in (3,6):box(x,top-1,z0-1,x,top-1,z1+1,'dark_oak_planks')
        # A small cloth corner marker, not a whole saturated purple roof.
        if not room and cloth=='purple_wool':box(front,height+1,z1-1,front,height+1,z1,cloth)
        # Counter stays on one side, leaving two-block access and empty interior.
        box(front,1,mid+1,front,1,z1-1,'dark_oak_planks')
        box(inner,1,z1-2,inner,2,z1-2,goods)
        if room:
            box(back,2,mid-1,back,3,mid,None)
            box(back,1,mid-1,back,1,mid,'deepslate_bricks')
        # Lamp is joined to the front corner post, beside rather than in the door.
        lx=front+1 if west else front-1
        lamp(lx,height-1,z0,front)
        shops.append({'name_zh':name,'bounds':[x0,1,z0,x1,height+3,z1],
                      'door':[front,1,mid-1],'inside':[inner,1,mid-1],
                      'open_front':'east' if west else 'west','roof_kind':'tile_shed' if room else 'cloth_lean_to',
                      'support_post_count':4,'floor_y':0})
    stall('西口旧纸铺',5,8,10,14,True,4,'gray_wool','bookshelf')
    stall('东口药草棚',19,11,23,17,False,5,'purple_wool','dried_kelp_block')
    stall('西中铜器棚',4,20,9,26,True,5,'gray_wool','waxed_oxidized_copper')
    stall('东中茶供铺',18,22,23,29,False,4,'gray_wool','dried_kelp_block',True)
    stall('西后契书铺',5,31,10,38,True,6,'purple_wool','bookshelf',True)
    stall('东后旧器棚',19,34,23,40,False,5,'gray_wool','waxed_oxidized_copper')
    def gate(name,z,x0,x1,top):
        for x in (x0,x1):
            box(x-1,1,z-1,x+1,1,z+1,'deepslate_bricks');post(x,z,top)
        box(x0,top,z,x1,top,z,'dark_oak_log_x')
        # One compact tier, no upper gate tower or second storey.
        box(x0-2,top+1,z-1,x1+2,top+1,z+1,'deepslate_tiles')
        box(x0-1,top+2,z,x1+1,top+2,z,'dark_prismarine')
        for x in (x0-2,x1+2):put(x,top+2,z,'deepslate_tiles')
        box((x0+x1)//2-1,top-1,z,(x0+x1)//2+1,top-1,z,'waxed_oxidized_copper')
        for x in (x0+1,x1-1):lamp(x,top-2,z,x-1 if x==x0+1 else x+1)
        gates.append({'name_zh':name,'z':z,'posts_x':[x0,x1],'clear_opening':[x0+2,1,z,x1-2,top-2,z],'top_y':top+2})
    gate('入谷低牌楼',3,8,20,6)
    gate('长街尾牌架',41,9,19,5)
    # Modest ground-side offerings, separated from the central walking ribbon.
    for x,z in ((11,18),(17,32)):
        put(x,1,z,'deepslate_bricks');post(x,z,3);lamp(x,3,z+1,x)
        # Lamp bracket extends along Z here; avoid a floating X-only cap.
        put(x,4,z,WOOD);put(x,4,z+1,'dark_oak_log_z')
    tokens=sorted(set(b.values()))
    def state(t):
        if t.startswith('dark_oak_log_'):return {'Name':'minecraft:dark_oak_log','Properties':{'axis':t[-1]}}
        if t=='verdant_froglight':return {'Name':'minecraft:verdant_froglight','Properties':{'axis':'y'}}
        return {'Name':'minecraft:'+t}
    palette=[state(t) for t in tokens];index={t:i for i,t in enumerate(tokens)}
    nbt={'DataVersion':3465,'size':list(SIZE),'palette':palette,'blocks':[{'pos':list(p),'state':index[t]} for p,t in sorted(b.items())],'entities':[]}
    meta={'id':'dynasty:scenic_ghost_market','event_id':22,'name_zh':'幽谷鬼市·鬼火长街',
          'size':list(SIZE),'anchor':[14,0,0],'center_pivot':PIVOT,'front':'-Z','street_axis':'+Z','ground_block_y':0,'walking_feet_y':1,
          'runtime_transform':'world = groundCenter + rotation(local - [14,0,22])',
          'client_visual_only':True,'place_in_world':False,'automatic_worldgen':False,'shops':shops,'gates':gates,'lights':lights,'support_posts':supports,
          'landmarks':{'entry':[14,1,0],'west_lane':[12,1,18],'middle':[13,1,25],'back':[14,1,43]},
          'lane_centerline':[[lane_center(z),1,z] for z in range(44)],
          'event_contract':{'dimension':'dynasty:underworld','time_ticks':[13000,23999],'weather_source':'阴司夜/雾环境，具体雨/区域雾判定由主线按维度实际能力接入','natural_rain_trigger_verified':False,'duration_ticks':1800,'distance':'medium','far_lod':'ghost lights; main integration','effect_budget':200,'sound':'faint market calls; main integration, no playback'},
          'design_zh':'原创44米山谷窄街；两侧低石肩形成山谷收束，六间错位棚铺、单层低牌楼与真实开口；无人物、无棚铺AI。与14不同的纵长占地、错位铺面、单层棚屋及不规则岩肩，未复用其建筑几何。'}
    return nbt,meta


def client_mesh(nbt,meta):
    rows=[r['pos']+[r['state']] for r in nbt['blocks']];occupied={tuple(r[:3]) for r in rows}
    faces=[r+[f] for r in rows for f,d in FACE_DELTAS.items() if tuple(v+a for v,a in zip(r[:3],d)) not in occupied]
    return {'version':1,'size':nbt['size'],'anchor':meta['anchor'],'centerPivot':PIVOT,'front':'-Z','groundBlockY':0,'palette':nbt['palette'],'blocks':rows,'exposedFaces':faces}


def client_bytes(nbt,meta):return (json.dumps(client_mesh(nbt,meta),ensure_ascii=False,separators=(',',':'))+'\n').encode()


def build():
    nbt,meta=design();OUTPUT.parent.mkdir(parents=True,exist_ok=True);CLIENT_OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_bytes(encode(nbt));CLIENT_OUTPUT.write_bytes(client_bytes(nbt,meta));dump(DOC/'geometry.json',meta)


def check():
    nbt=read_nbt();meta=json.loads((DOC/'geometry.json').read_text());client=json.loads(CLIENT_OUTPUT.read_text())
    states={tuple(r['pos']):r['state'] for r in nbt['blocks']};occupied=set(states);tests=[]
    def test(name,ok):tests.append({'name':name,'passed':bool(ok)})
    expected,expected_meta=design()
    test('standard bounded 28x16x44 NBT',nbt['DataVersion']==3465 and nbt['size']==list(SIZE) and all(all(0<=v<SIZE[i] for i,v in enumerate(p)) for p in occupied))
    test('source reproduces actual NBT and metadata',nbt==expected and meta==expected_meta)
    test('deterministic gzip NBT bytes',OUTPUT.read_bytes()==encode(expected)==encode(design()[0]))
    test('sparse unique occupied voxels without air',len(states)==len(nbt['blocks']) and all(s['Name']!='minecraft:air' for s in nbt['palette']))
    test('opaque static vanilla full cubes only',all(s['Name'].removeprefix('minecraft:') in ALLOWED for s in nbt['palette']))
    test('real log and froglight axis properties',all(s.get('Properties')=={'axis':s['Properties']['axis']} and s['Properties']['axis'] in 'xyz' if s['Name'] in ('minecraft:dark_oak_log','minecraft:verdant_froglight') else 'Properties' not in s for s in nbt['palette']))
    test('no entities or block entity payload',nbt['entities']==[] and all(set(r)=={'pos','state'} for r in nbt['blocks']))
    test('client version1 schema exact placement palette and original coordinates',client==client_mesh(nbt,meta) and client['centerPivot']==[14,0,22] and client['anchor']==[14,0,0] and client['groundBlockY']==0 and client['front']=='-Z')
    test('client bytes reproducible',CLIENT_OUTPUT.read_bytes()==client_bytes(nbt,meta))
    independent=set()
    for (x,y,z),s in states.items():
        for p,f in [((x,y-1,z),'down'),((x,y+1,z),'up'),((x,y,z-1),'north'),((x,y,z+1),'south'),((x-1,y,z),'west'),((x+1,y,z),'east')]:
            if p not in states:independent.add((x,y,z,s,f))
    test('all exterior cavity and bottom faces preserve vanilla axes',independent=={tuple(r) for r in client['exposedFaces']} and len(independent)==len(client['exposedFaces']))
    test('strictly below 10000 exposed faces',len(independent)<10000)
    seen={next(iter(occupied))};q=deque(seen)
    while q:
        p=q.popleft()
        for d in DIRS:
            n=tuple(v+a for v,a in zip(p,d))
            if n in occupied and n not in seen:seen.add(n);q.append(n)
    test('all roofs lamps rock shoulders and foundations face connected',seen==occupied)
    def walkable(p):
        x,y,z=p
        return p not in occupied and (x,y+1,z) not in occupied and (x,y-1,z) in occupied
    start=tuple(meta['landmarks']['entry']);walked={start};q=deque(walked)
    while q:
        x,y,z=q.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            p=(x+dx,y,z+dz)
            if p not in walked and walkable(p):walked.add(p);q.append(p)
    test('continuous 44m ground corridor with two block head clearance',all(tuple(p) in walked for p in meta['lane_centerline']))
    for name,p in meta['landmarks'].items():test('connected walking route '+name,tuple(p) in walked)
    for shop in meta['shops']:
        test('true shop opening and accessible empty interior '+shop['name_zh'],tuple(shop['door']) in walked and tuple(shop['inside']) in walked)
    for gate in meta['gates']:
        x0,y0,z0,x1,y1,z1=gate['clear_opening']
        test('real low gate opening '+gate['name_zh'],all((x,y,z0) not in occupied for x in range(x0,x1+1) for y in range(y0,y1+1)))
    test('every post is continuous down to real ground',all(all((s['base'][0],y,s['base'][2]) in occupied for y in range(s['top'][1]+1)) for s in meta['support_posts']))
    test('twelve attached lamps have exact half-block center coordinates',len(meta['lights'])==12 and all(tuple(l['voxel']) in occupied and nbt['palette'][states[tuple(l['voxel'])]]['Name']=='minecraft:verdant_froglight' and l['center']==[v+.5 for v in l['voxel']] for l in meta['lights']))
    test('no automatic worldgen registration',not any((ROOT/f'src/main/resources/data/dynasty/worldgen/{folder}/scenic_ghost_market.json').exists() for folder in ('structure','structure_set','template_pool')))
    test('event22 static asset contract only',meta['event_contract']['duration_ticks']==1800 and meta['event_contract']['effect_budget']==200 and meta['event_contract']['dimension']=='dynasty:underworld' and meta['place_in_world'] is False)
    prior=json.loads((DOC/'references/prior-manifests.json').read_text());selected=json.loads((DOC/'references/selected-100.json').read_text());old=set();count=0
    for row in prior['sources']:
        p=ROOT/row['path'];d=json.loads(p.read_text());rows=d if isinstance(d,list) else d['references'];old.update(r['sha256'] for r in rows);count+=len(rows)
        test('reference manifest unchanged '+row['path'],sha(p)==row['sha256'])
    new={r['sha256'] for r in selected}
    test('100 distinct selected references excluding all 1500 preceding records',len(selected)==len(new)==100 and not new&old and count>=1500)
    test('every selected image viewed with individual geometry observation',all(r.get('viewed') and r.get('observation_zh') and sha(DOC/'references'/r['file'])==r['sha256'] for r in selected))
    decoded=json.loads((DOC/'references/decoded-rgba-audit.json').read_text())
    test('1500 available prior decoded RGBA hashes exclude all 100 selected images',decoded['status']=='PASS' and decoded['prior_records']==count and decoded['raw_overlap']==decoded['decoded_overlap']==0 and decoded['prior_unique_decoded_hashes']==1500 and len({r['decodedRgbaSha256'] for r in selected})==100)
    frozen=json.loads((DOC/'protected-baseline.json').read_text())
    test('accepted preceding assets and ready handoff remain unchanged',all(sha(ROOT/p)==h for p,h in frozen.items()))
    report={'status':'PASS' if all(t['passed'] for t in tests) else 'FAIL','tests':tests,'source_sha256':sha(Path(__file__)),'nbt_sha256':sha(OUTPUT),'client_json_sha256':sha(CLIENT_OUTPUT),'occupied_voxels':len(occupied),'exposed_faces':len(independent),'connected_voxels':len(seen),'reachable_floor_cells':len(walked),'palette_states':len(nbt['palette']),'vanilla_block_types':len({s['Name'] for s in nbt['palette']}),'occupied_bounds':{'min':[min(p[i] for p in occupied) for i in range(3)],'max_inclusive':[max(p[i] for p in occupied) for i in range(3)]},'reference_prior_records':count,'native_game_verified':False,'java_executed':False,'world_placement_performed':False}
    dump(DOC/'checks.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='tests'},ensure_ascii=False),flush=True)
    if report['status']!='PASS':raise AssertionError([t['name'] for t in tests if not t['passed']])
    return nbt,meta,report


def review():
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
    import texture_review as r
    nbt,meta,report=check();client=json.loads(CLIENT_OUTPUT.read_text());states={tuple(row['pos']):nbt['palette'][row['state']] for row in nbt['blocks']}
    source=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar'
    textures={};hashes={};quads=[]
    corners={({'east':'west','west':'east'}.get(f,f)):c for f,c in r.r.FACES.items()}
    with zipfile.ZipFile(source) as z:
        def texture(p,face):
            s=states[p];name=s['Name'].removeprefix('minecraft:');axis=s.get('Properties',{}).get('axis','y')
            ends={'x':('east','west'),'y':('up','down'),'z':('north','south')}[axis]
            key=name
            if name=='dark_oak_log' and face in ends:key+='_top'
            if name=='verdant_froglight':key+='_'+('top' if face in ends else 'side')
            if name=='waxed_oxidized_copper':key='oxidized_copper'
            if name=='dried_kelp_block':key='dried_kelp_'+('top' if face=='up' else 'bottom' if face=='down' else 'side')
            if name=='bookshelf' and face in ('up','down'):key='oak_planks'
            if key not in textures:
                raw=z.read('assets/minecraft/textures/block/'+key+'.png');im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(16,16)
                textures[key]=np.array(im);hashes[key]=hashlib.sha256(raw).hexdigest()
            tex=textures[key]
            if name=='dried_kelp_block' and face in ('south','east'):tex=tex[:,::-1]
            if name=='dark_oak_log' and face not in ends:
                # Align the side grain with the actual state axis in face UV.
                vv=np.array(corners[face]);u=vv[1]-vv[0];v=vv[3]-vv[0];a=np.eye(3,dtype=int)['xyz'.index(axis)]
                if abs(u@a)>abs(v@a):tex=np.rot90(tex)
            return tex
        for x,y,zz,state,face in client['exposedFaces']:
            p=(x,y,zz);quads.append(((np.array(corners[face])+p)*16,{'uv':[0,0],'uv_size':[16,16],'_tex':texture(p,face)},'market'))
    assert len(quads)==report['exposed_faces']
    # Review-only original 1.8m player and 1m material swatches at actual ground.
    scene=quads+r.references(np.array([14*16,16,.75*16]));points=np.concatenate([v for v,_,_ in scene]);fallback=np.zeros((16,16,3),dtype=np.uint8)
    foot='软件预览 · 实际NBT与原版PNG · 1.8米玩家参照同地面 · 无雾/鬼火/音效 · 非游戏截图'
    views=[('front',0,12),('back',180,12),('left',-90,12),('right',90,12),('three-quarter',45,28)]
    for label,yaw,elevation in views:
        r.labelled(r.raster(scene,fallback,yaw=yaw,elevation=elevation,size=(1400,950),mode='lit',frame_points=points),'幽谷鬼市 / '+label,foot).save(DOC/(label+'.png'));print('rendered',label,flush=True)
    gray=[(v,dict(uv,_tex=np.full((16,16,3),170,dtype=np.uint8)),bn) for v,uv,bn in scene]
    r.labelled(r.raster(gray,fallback,yaw=45,elevation=28,size=(1400,950),mode='lit',frame_points=points),'幽谷鬼市 / 灰模',foot).save(DOC/'gray.png')
    r.labelled(r.raster(scene,fallback,yaw=45,elevation=28,size=(1400,950),mode='dim',frame_points=points),'幽谷鬼市 / 暗光',foot).save(DOC/'dim.png')
    black=[(v,dict(uv,_tex=fallback),bn) for v,uv,bn in quads]
    r.labelled(r.raster(black,fallback,yaw=35,elevation=15,size=(1400,950),mode='unlit',frame_points=points),'幽谷鬼市 / 纯黑剪影',foot).save(DOC/'silhouette.png')
    for label,z0,distance in [('entry-18m',0,18),('street-inside',14,4)]:
        offset=np.array([lane_center(z0)*16,16,z0*16]);local=[(v-offset,uv,bn) for v,uv,bn in scene]
        r.labelled(r.raster(local,fallback,yaw=0,distance=distance,size=(1400,950),mode='lit'),'幽谷鬼市 / '+label,'软件地面视角 · 视高1.62米 / 70°垂直FOV · 原尺度 · 非游戏截图').save(DOC/(label+'.png'))
    r.labelled(r.raster(scene,fallback,yaw=0,elevation=75,size=(1400,950),mode='lit',frame_points=points),'幽谷鬼市 / 街道开口俯视',foot).save(DOC/'plan.png')
    dump(DOC/'preview.json',{'source':'actual production NBT and version1 exterior faces plus vanilla 1.20.1 PNG','native_screenshot':False,'nbt_sha256':sha(OUTPUT),'client_json_sha256':sha(CLIENT_OUTPUT),'texture_source':str(source),'texture_png_sha256':hashes,'exposed_faces':len(quads),'views':[v[0] for v in views]+['gray','dim','silhouette','entry-18m','street-inside','plan'],'person_height_m':1.8,'person_feet_y':1,'reference_origin':[14,1,.75],'reference_on_actual_entry_floor':True,'effects_enabled':False,'software_two_sided':True,'runtime_face_culling_not_verified':True})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--review',action='store_true');args=parser.parse_args()
    if args.review:review()
    elif args.check:check()
    else:build();check()


