#!/usr/bin/env python3
"""Original ruined frontier wall; deterministic offline static voxel assets.

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
DOC = ROOT/'docs/art/cod3-great-wall-echo-v2'
OUTPUT = ROOT/'src/main/resources/data/dynasty/structures/scenic_great_wall_echo.nbt'
CLIENT_OUTPUT = ROOT/'src/main/resources/assets/dynasty/scenic/great_wall_echo.json'
FLAGS_OUTPUT = ROOT/'src/main/resources/assets/dynasty/scenic/great_wall_echo_flags.json'
LOD_DOC = DOC/'flags-lod'
SIZE = (64,24,32)
PIVOT = [32,0,16]
FACE_DELTAS = {'down':(0,-1,0),'up':(0,1,0),'north':(0,0,-1),
               'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}
DIRS = tuple(FACE_DELTAS.values())
STONE = 'stone_bricks'
BASE = 'cobblestone'
CAP = 'polished_andesite'
WOOD = 'spruce_log'
ALLOWED = {STONE,BASE,CAP,WOOD,'cracked_stone_bricks','mossy_stone_bricks','andesite','spruce_planks','red_wool','black_wool'}


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


def wall_center(x):
    if x<18:return 10
    if x<30:return 10+(x-18)//2
    if x<43:return 16
    if x<55:return 16+(x-42)//3
    return 20


def wall_floor(x):
    if x<6:return 2+x//2
    if x<18:return 5
    if x<24:return 6
    if x<47:return 7
    if x<52:return 6
    if x<56:return 5
    if x<60:return 4
    return max(2,4-(x-60))


def design():
    b={};flags=[]
    def put(x,y,z,name):
        assert all(0<=v<SIZE[i] for i,v in enumerate((x,y,z))),(x,y,z)
        if name is None:b.pop((x,y,z),None)
        else:b[x,y,z]=name
    def box(x0,y0,z0,x1,y1,z1,name):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):put(x,y,z,name)
    def edges(x0,z0,x1,z1,y,name):
        box(x0,y,z0,x1,y,z0,name);box(x0,y,z1,x1,y,z1,name)
        box(x0,y,z0,x0,y,z1,name);box(x1,y,z0,x1,y,z1,name)
    def flag(label,x,z,bottom,top,axis,width=5):
        # Logs and wool are full static cubes, not banner block entities.
        # Swallowtail has two connected ends; every cloth cell joins the pole.
        box(x,bottom,z,x,top,z,WOOD)
        cloth=[];bar=[]
        for u in range(width+1):
            xx=x+u if axis=='X' else x;zz=z if axis=='X' else z+u
            put(xx,top,zz,'spruce_log_'+axis.lower());bar.append([xx,top,zz])
            if not u:continue
            for v in range(4):
                if u>=width-1 and v in (1,2):continue
                yy=top-1-v
                put(xx,yy,zz,'black_wool' if v==3 else 'red_wool')
                cloth.append([xx,yy,zz])
        flags.append({'name_zh':label,'pole_bottom':[x,bottom,z],'pole_top':[x,top,z],
                      'cloth_axis':'+'+axis,'crossbar':bar,'static_cloth':cloth,
                      'attachment_line':[[x,yy,z] for yy in range(top-4,top)],
                      'runtime_animation_included':False})

    # Original folding wall. Foundation follows the wall rather than a large
    # rectangular display tile. Ends descend into broad, supported break faces.
    for x in range(64):
        c=wall_center(x);h=wall_floor(x)
        box(x,0,c-4,x,1,c+4,BASE)
        box(x,2,c-3,x,h,c+3,STONE)
        box(x,h,c-2,x,h,c+2,CAP)
        for z in (c-3,c+3):
            broken=(x<6 or x>59 or (18<=x<=22 and z<c) or (52<=x<=56 and z>c))
            if not broken:
                put(x,h+1,z,STONE)
                if x%4<2:put(x,h+2,z,CAP)
        # Buttress bases widen toward the ground; no separate floating trim.
        if 6<x<59 and x%8 in (0,1):
            for z in (c-4,c+4):box(x,2,z,x,max(2,h-2),z,BASE)
    # Large deliberate crack/moss patches, not pseudo-random surface noise.
    for lo,hi in ((2,5),(19,22),(54,57),(61,63)):
        for x in range(lo,hi+1):
            c=wall_center(x)
            for y in range(2,min(wall_floor(x),4)+1):
                for z in (c-3,c+3):
                    if (x,y,z) in b:put(x,y,z,'cracked_stone_bricks')
    for lo,hi in ((8,11),(25,28),(44,47)):
        for x in range(lo,hi+1):
            c=wall_center(x)
            for y in (2,3):put(x,y,c+3,'mossy_stone_bricks')

    # Western roofless residual lookout: high rear corner, broken front.
    box(7,0,3,18,1,17,BASE);box(8,2,4,17,5,16,STONE)
    box(8,5,4,17,5,16,CAP)
    for x in (8,17):box(x,6,4,x,10,16,STONE)
    box(8,6,16,17,10,16,STONE);box(8,6,4,17,7,4,STONE)
    box(8,8,4,10,9,4,'cracked_stone_bricks')
    box(8,10,14,10,11,16,CAP)
    for x in (8,17):box(x,6,8,x,9,12,None)
    box(11,7,16,14,8,16,None)
    # Low grounded fallen masonry joins the broken wall foot, not loose debris.
    box(7,0,1,12,0,3,BASE);box(8,1,2,10,2,3,'cracked_stone_bricks')

    # Eastern low bastion has a different surviving corner and lower mass.
    box(48,0,14,59,1,27,BASE);box(49,2,15,58,6,26,STONE)
    box(49,6,15,58,6,26,CAP);edges(49,15,58,26,7,STONE)
    box(49,8,25,52,10,26,'cracked_stone_bricks')
    box(49,11,25,50,11,26,CAP)
    for x in (49,58):box(x,7,18,x,9,22,None)
    box(55,7,15,57,7,15,None)
    # Two end transitions retain a route down from the bastion's raised deck.
    for x,h in ((59,5),(60,4),(61,3),(62,2),(63,2)):
        box(x,0,18,x,h,22,STONE);box(x,h,18,x,h,22,CAP)

    # Broad central beacon platform and genuinely hollow upper chamber.
    box(26,0,8,42,1,24,BASE)
    box(27,2,9,41,5,23,STONE)
    box(28,6,10,40,7,22,STONE);box(28,7,10,40,7,22,CAP)
    # Remove the underlying march parapets before building the upper chamber.
    box(28,8,10,40,13,22,None)
    for x in (28,40):box(x,8,10,x,13,22,STONE)
    for z in (10,22):box(28,8,z,40,13,z,STONE)
    # Thick corner piers continue into the roof. Doors never cut the corners.
    for x in (28,39):
        for z in (10,21):box(x,8,z,x+1,13,z+1,STONE)
    box(32,8,10,36,10,11,None);box(33,11,10,35,11,11,None)
    box(32,12,10,36,12,11,'spruce_planks')
    for x in (28,39):box(x,8,14,x+1,11,18,None)
    box(33,8,22,35,10,22,None)
    for x in (30,37):box(x,9,22,x+1,10,22,None)
    # Solid cap and low crenellations; no pointed keep or false floating roof.
    box(27,14,9,41,14,23,CAP)
    edges(28,10,40,22,15,STONE)
    for x in range(28,41):
        for z in (10,22):
            if (x-28)%4<2:put(x,16,z,CAP)
    for z in range(11,22):
        for x in (28,40):
            if (z-10)%4<2:put(x,16,z,CAP)
    # Internal stair rises to roof through a real ceiling opening.
    box(30,14,16,31,14,18,None)
    for i,z in enumerate(range(12,20)):
        box(30,8,z,31,7+i,z,STONE)
        box(30,7+i,z,31,7+i,z,CAP)
    # Front ground-to-march stair: full-cube treads with continuous foundation.
    for z in range(1,11):
        h=min(7,max(0,z-2))
        box(32,0,z,36,h,z,STONE);box(32,h,z,36,h,z,CAP)
    box(31,0,0,38,0,2,CAP)
    # A few dry timber billets identify an unlit beacon hearth, with no fire.
    box(30,15,12,31,15,14,'spruce_log_z')
    flag('西残墩旗',10,6,6,16,'X')
    flag('主烽燧旗',34,18,15,22,'X')
    flag('东残墩旗',54,20,7,16,'Z')

    def state(token):
        if token.startswith('spruce_log'):
            return {'Name':'minecraft:spruce_log','Properties':{'axis':token.rsplit('_',1)[-1] if token[-2]=='_' else 'y'}}
        return {'Name':'minecraft:'+token}
    tokens=sorted(set(b.values()));palette=[state(t) for t in tokens];index={t:i for i,t in enumerate(tokens)}
    nbt={'DataVersion':3465,'size':list(SIZE),'palette':palette,
         'blocks':[{'pos':list(p),'state':index[t]} for p,t in sorted(b.items())],'entities':[]}
    meta={'id':'dynasty:scenic_great_wall_echo','event_id':18,'name_zh':'雾中军阵·长城残影',
          'size':list(SIZE),'anchor':[34,0,1],'center_pivot':PIVOT,'front':'-Z','ground_block_y':0,
          'runtime_transform':'world = groundCenter + rotation(local - [32,0,16])',
          'client_visual_only':True,'place_in_world':False,'automatic_worldgen':False,
          'wall_path':[{'x':x,'center_z':wall_center(x),'floor_block_y':wall_floor(x)} for x in range(64)],
          'flags':flags,'flag_animation_included':False,'entities':[],
          'static_lod':'full architecture; main controls distant flag silhouette LOD',
          'landmarks':{'entry':[34,1,1],'main_entry':[34,8,12],'main_roof':[38,15,20],
                       'west_march':[5,5,10],'west_lookout':[12,6,10],
                       'east_bastion':[53,7,20],'east_end':[63,3,20]},
          'main_chamber_empty_box':[32,8,12,38,11,20],
          'corner_piers':[[x,8,z,x+1,13,z+1] for x in (28,39) for z in (10,21)],
          'event_contract':{'dimension':'minecraft:overworld','site':'dynasty:ruined_battlefield',
                            'time_ticks':[0,2500],'weather_source':'RAIN existing mapping for morning fog',
                            'duration_ticks':1200,'distance':'medium','far_lod':'flag silhouettes',
                            'effect_budget':200,'sound':'faint horn; main integration only, no playback'},
          'design_zh':'原创折线长墙、低宽主烽燧、两端不同残墩、贯通马道与地面石阶；三面残旗直接连接实杆，停用粒子仍完整成立。'}
    return nbt,meta


def client_mesh(nbt,meta):
    blocks=[r['pos']+[r['state']] for r in nbt['blocks']];occupied={tuple(r[:3]) for r in blocks}
    faces=[r+[face] for r in blocks for face,d in FACE_DELTAS.items()
           if tuple(v+dd for v,dd in zip(r[:3],d)) not in occupied]
    return {'version':1,'size':nbt['size'],'anchor':meta['anchor'],'centerPivot':meta['center_pivot'],
            'front':meta['front'],'groundBlockY':0,'palette':nbt['palette'],'blocks':blocks,'exposedFaces':faces}


def client_bytes(nbt,meta):
    return (json.dumps(client_mesh(nbt,meta),ensure_ascii=False,separators=(',',':'))+'\n').encode()


def flag_positions(flag):
    x,bottom,z=flag['pole_bottom'];top=flag['pole_top'][1]
    return ({(x,y,z) for y in range(bottom,top+1)}
            |{tuple(p) for key in ('crossbar','attachment_line','static_cloth') for p in flag[key]})


def flags_mesh(full,meta):
    selected=set().union(*(flag_positions(f) for f in meta['flags']))
    rows=[r for r in full['blocks'] if tuple(r[:3]) in selected]
    assert {tuple(r[:3]) for r in rows}==selected
    result={k:v for k,v in full.items() if k not in ('blocks','exposedFaces')}
    result['blocks']=rows
    # Deliberately recompute against ONLY the selected voxels. Filtering the
    # full mesh face list would lose pole undersides and former wall contacts.
    result['exposedFaces']=[r+[face] for r in rows for face,d in FACE_DELTAS.items()
                            if tuple(v+dd for v,dd in zip(r[:3],d)) not in selected]
    return result


def flags_bytes(full,meta):
    return (json.dumps(flags_mesh(full,meta),ensure_ascii=False,separators=(',',':'))+'\n').encode()


def frozen_delivery_intact():
    protected=json.loads((LOD_DOC/'protected-baseline.json').read_text())
    return all(sha(ROOT/p)==h for p,h in protected.items())


def build():
    # The full building was handed off and is frozen. This extension writes
    # only the flag resource, even on the default export command.
    assert frozen_delivery_intact(),'Frozen full delivery changed; do not overwrite it'
    full=json.loads(CLIENT_OUTPUT.read_text());meta=json.loads((DOC/'geometry.json').read_text())
    FLAGS_OUTPUT.write_bytes(flags_bytes(full,meta))


def check_flags(full,meta,tests):
    flags=json.loads(FLAGS_OUTPUT.read_text());rows=flags['blocks'];occupied={tuple(r[:3]):r[3] for r in rows}
    groups=[flag_positions(f) for f in meta['flags']];expected=set().union(*groups)
    def test(name,ok):tests.append({'name':name,'passed':bool(ok)})
    test('far flag schema and all placement fields match frozen full JSON',set(flags)==set(full)
         and all(flags[k]==full[k] for k in full if k not in ('blocks','exposedFaces')))
    test('far flag palette retains every original index and axis property',flags['palette']==full['palette'])
    test('far flags contain exactly original poles crossbars attachment lines cloth',len(occupied)==len(rows)==len(expected)
         and set(occupied)==expected and rows==[r for r in full['blocks'] if tuple(r[:3]) in expected])
    test('far flags use only original log and wool full cubes',all(flags['palette'][i]['Name'] in
         ('minecraft:spruce_log','minecraft:red_wool','minecraft:black_wool') for i in occupied.values()))
    face_set=set()
    for (x,y,z),state in occupied.items():
        for q,d in [((x,y-1,z),'down'),((x,y+1,z),'up'),((x,y,z-1),'north'),((x,y,z+1),'south'),((x-1,y,z),'west'),((x+1,y,z),'east')]:
            if q not in occupied:face_set.add((x,y,z,state,d))
    test('far exterior faces independently recomputed from subset with vanilla axes',face_set=={tuple(r) for r in flags['exposedFaces']}
         and len(face_set)==len(flags['exposedFaces']))
    full_faces={tuple(r) for r in full['exposedFaces']};new_faces=face_set-full_faces
    test('all three newly exposed pole bottom caps are present',all((*f['pole_bottom'],occupied[tuple(f['pole_bottom'])],'down') in new_faces for f in meta['flags']))
    unseen=set(occupied);components=[]
    while unseen:
        start=unseen.pop();component={start};q=deque([start])
        while q:
            p=q.popleft()
            for d in DIRS:
                n=tuple(v+dd for v,dd in zip(p,d))
                if n in unseen:unseen.remove(n);component.add(n);q.append(n)
        components.append(component)
    test('exactly three individually connected complete flags',len(components)==3 and {frozenset(c) for c in components}=={frozenset(g) for g in groups})
    test('far resource deterministic without moving or compacting palette',FLAGS_OUTPUT.read_bytes()==flags_bytes(full,meta)==flags_bytes(full,meta))
    test('frozen full delivery and original readiness manifest unchanged',frozen_delivery_intact())
    ready=json.loads((DOC/'BUILDING_READY.json').read_text())
    test('historical ready source hash retained in original source archive',sha(LOD_DOC/'full-building-source.py')==ready['sha256'][str(Path(__file__).relative_to(ROOT))])
    return {'path':str(FLAGS_OUTPUT.relative_to(ROOT)),'sha256':sha(FLAGS_OUTPUT),'occupied_voxels':len(rows),
            'exposed_faces':len(face_set),'connected_components':len(components),
            'component_voxel_counts':[len(g) for g in groups],
            'newly_exposed_faces_vs_full':sorted([list(f) for f in new_faces]),
            'occupied_bounds':{'min':[min(p[i] for p in occupied) for i in range(3)],'max_inclusive':[max(p[i] for p in occupied) for i in range(3)]}}


def check():
    nbt=read_nbt();meta=json.loads((DOC/'geometry.json').read_text());client=json.loads(CLIENT_OUTPUT.read_text())
    states={tuple(r['pos']):r['state'] for r in nbt['blocks']};b={p:nbt['palette'][i]['Name'].removeprefix('minecraft:') for p,i in states.items()};tests=[]
    def test(name,ok):tests.append({'name':name,'passed':bool(ok)})
    test('standard bounded 64x24x32 NBT',nbt['size']==list(SIZE) and nbt['DataVersion']==3465 and all(all(0<=v<SIZE[i] for i,v in enumerate(p)) for p in b))
    test('opaque full static vanilla cubes only',set(b.values())<=ALLOWED)
    test('no entities block entities explicit air or logic payload',nbt['entities']==[] and all(set(r)=={'pos','state'} for r in nbt['blocks']))
    test('no duplicate positions',len(states)==len(nbt['blocks']))
    test('source reproduces NBT and geometry metadata',design()==(nbt,meta))
    test('byte identical deterministic NBT',encode(design()[0])==encode(design()[0])==OUTPUT.read_bytes())
    test('client version1 complete identical palette and unshifted voxels',client['version']==1 and client['palette']==nbt['palette'] and client['blocks']==[r['pos']+[r['state']] for r in nbt['blocks']])
    test('byte identical client JSON',client_bytes(*design())==CLIENT_OUTPUT.read_bytes())
    test('center pivot and ground anchor retain Y0',client['centerPivot']==PIVOT and client['anchor']==[34,0,1] and client['front']=='-Z' and client['groundBlockY']==0 and min(p[1] for p in b)==0)
    # Independent explicit neighbor table catches export face-axis mistakes.
    faces=set()
    for (x,y,z),state in states.items():
        for q,d in [((x,y-1,z),'down'),((x,y+1,z),'up'),((x,y,z-1),'north'),((x,y,z+1),'south'),((x-1,y,z),'west'),((x+1,y,z),'east')]:
            if q not in states:faces.add((x,y,z,state,d))
    test('all exterior and cavity faces preserve vanilla axes',faces=={tuple(r) for r in client['exposedFaces']} and len(faces)==len(client['exposedFaces']))
    test('full geometry exposed faces below 10000',len(faces)<10000)
    seen={next(iter(b))};q=deque(seen)
    while q:
        p=q.popleft()
        for d in DIRS:
            n=tuple(v+dd for v,dd in zip(p,d))
            if n in b and n not in seen:seen.add(n);q.append(n)
    test('all foundations walls flags and roof face-connected',seen==set(b))
    test('all central corner piers remain solid',all((x,y,z) in b for x0,y0,z0,x1,y1,z1 in meta['corner_piers'] for x in range(x0,x1+1) for y in range(y0,y1+1) for z in range(z0,z1+1)))
    test('central chamber contains actual empty interior',all((x,y,z) not in b for x in range(32,39) for y in range(8,12) for z in range(12,21)))
    test('front and back doorway sightline remains genuinely open',all((x,y,z) not in b for x in range(33,36) for y in range(8,11) for z in range(10,23)))
    test('both sides of upper room connect to wall march',all((x,y,z) not in b for x in (28,29,39,40) for y in range(8,12) for z in range(14,19)))
    test('three connected full cube flags without banner entities',len(meta['flags'])==3 and not any('banner' in s['Name'] for s in nbt['palette']) and all(b.get(tuple(p)) in ('red_wool','black_wool') for f in meta['flags'] for p in f['static_cloth']))
    test('flag poles continuous and grounded on real platforms',all(all((f['pole_bottom'][0],y,f['pole_bottom'][2]) in b for y in range(f['pole_bottom'][1]-1,f['pole_top'][1]+1)) for f in meta['flags']))
    test('flag crossbars retain correct log axes',all(nbt['palette'][states[tuple(p)]]=={'Name':'minecraft:spruce_log','Properties':{'axis':f['cloth_axis'][-1].lower()}} for f in meta['flags'] for p in f['crossbar']))
    test('nonrectangular foundation leaves front corners open',all((x,0,z) not in b for x in range(5) for z in range(4)))
    def walkable(p):
        x,y,z=p
        return p not in b and (x,y+1,z) not in b and (x,y-1,z) in b
    start=tuple(meta['landmarks']['entry']);walked={start};q=deque(walked)
    while q:
        x,y,z=q.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (-1,0,1):
                p=(x+dx,y+dy,z+dz)
                if p in walked or not walkable(p) or (dy==1 and (x,y+2,z) in b):continue
                walked.add(p);q.append(p)
    test('entry has supported head clearance',walkable(start))
    for name,p in meta['landmarks'].items():test('geometric stair route reaches '+name,tuple(p) in walked)
    test('no automatic structure or worldgen registration',not any((ROOT/f'src/main/resources/data/dynasty/worldgen/{folder}/scenic_great_wall_echo.json').exists() for folder in ('structure','structure_set','template_pool')))
    prior=json.loads((DOC/'references/prior-manifests.json').read_text());sel=json.loads((DOC/'references/selected-100.json').read_text());old=set();count=0
    for row in prior['sources']:
        path=ROOT/row['path'];data=json.loads(path.read_text());rows=data if isinstance(data,list) else data['references'];count+=len(rows);old.update(r['sha256'] for r in rows)
        test('prior reference index stable '+row['path'],sha(path)==row['sha256'])
    hashes={r['sha256'] for r in sel}
    test('100 new reference image hashes against 1200 previous',len(sel)==len(hashes)==100 and count==1200 and not hashes&old)
    test('viewed cached images and individual observations retained',all(r['observation_zh'] and r['viewed'] and sha(DOC/'references'/r['file'])==r['sha256'] for r in sel))
    # Earlier batches are now owned by main and can legitimately change during
    # integration. Recheck this extension against the frozen #18 delivery,
    # rather than reject main's accepted #17 documentation/source updates.
    test('frozen current full building delivery remains unchanged',frozen_delivery_intact())
    flag_report=check_flags(client,meta,tests)
    report={'status':'PASS' if all(r['passed'] for r in tests) else 'FAIL','tests':tests,
            'source_sha256':sha(Path(__file__)),'nbt_sha256':sha(OUTPUT),'client_json_sha256':sha(CLIENT_OUTPUT),
            'occupied_voxels':len(b),'exposed_faces':len(faces),'connected_voxels':len(seen),
            'reachable_floor_cells':len(walked),'palette_counts':dict(Counter(b.values())),
            'occupied_bounds':{'min':[min(p[i] for p in b) for i in range(3)],'max_inclusive':[max(p[i] for p in b) for i in range(3)]},
            'native_game_verified':False,'java_executed':False,'world_placement_performed':False,'flag_lod':flag_report}
    dump(LOD_DOC/'checks.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('tests','palette_counts')},ensure_ascii=False),flush=True)
    if report['status']!='PASS':raise AssertionError([r['name'] for r in tests if not r['passed']])
    return b,meta,report



def review():
    """Render only the independent flag LOD; never rewrite full previews."""
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
    import texture_review as r
    _,meta,report=check();client=json.loads(FLAGS_OUTPUT.read_text());full=read_nbt()
    states={tuple(row[:3]):client['palette'][row[3]] for row in client['blocks']}
    textures={};hashes={};quads=[]
    source=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar'
    if not source.exists():source=source.with_name('client.jar')
    with zipfile.ZipFile(source) as z:
        def texture(p,face):
            state=states[p];name=state['Name'].removeprefix('minecraft:')
            if name=='spruce_log':
                ends={'x':('east','west'),'y':('up','down'),'z':('north','south')}[state['Properties']['axis']]
                if face in ends:name='spruce_log_top'
            if name not in textures:
                raw=z.read('assets/minecraft/textures/block/'+name+'.png')
                im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(16,16)
                textures[name]=np.array(im);hashes[name]=hashlib.sha256(raw).hexdigest()
            return textures[name]
        # Match the helper's reversed east/west corner names to vanilla axes.
        corners_by_face={({'east':'west','west':'east'}.get(f,f)):c for f,c in r.r.FACES.items()}
        for x,y,z0,state,face in client['exposedFaces']:
            p=(x,y,z0)
            quads.append(((np.array(corners_by_face[face])+p)*16,
                         {'uv':[0,0],'uv_size':[16,16],'_tex':texture(p,face)},'flags'))
    assert len(quads)==report['flag_lod']['exposed_faces']
    # Same world frame as full building previews. Do not recenter/scale each flag.
    points=np.concatenate([(np.array(c)+row['pos'])*16 for row in full['blocks'] for c in r.r.FACES.values()]
                          +[v for v,_,_ in r.references(np.array([35*16,16,.5*16]))])
    fallback=np.zeros((16,16,3),dtype=np.uint8)
    foot='软件远景LOD · 仅原位杆/横杆/挂线/旗布 · 与完整建筑同取景 · 静态无雾 · 非游戏截图'
    views=[('front',0,12),('back',180,12),('three-quarter',35,22),('underside',35,-20)]
    for label,yaw,elevation in views:
        r.labelled(r.raster(quads,fallback,yaw=yaw,elevation=elevation,size=(1600,900),mode='lit',frame_points=points),
                   '长城残影 / 远旗 '+label,foot).save(LOD_DOC/(label+'.png'))
    gray=[(v,dict(uv,_tex=np.full((16,16,3),170,dtype=np.uint8)),bone) for v,uv,bone in quads]
    r.labelled(r.raster(gray,fallback,yaw=35,elevation=22,size=(1600,900),mode='lit',frame_points=points),
               '长城残影 / 远旗灰模',foot).save(LOD_DOC/'gray.png')
    black=[(v,dict(uv,_tex=fallback),bone) for v,uv,bone in quads]
    r.labelled(r.raster(black,fallback,yaw=0,elevation=0,size=(1600,900),mode='unlit',frame_points=points),
               '长城残影 / 远旗黑影',foot).save(LOD_DOC/'silhouette.png')
    approach=[(v-np.array([34*16,16,0]),uv,bone) for v,uv,bone in quads]
    r.labelled(r.raster(approach,fallback,yaw=0,distance=80,size=(1600,900),mode='lit'),
               '长城残影 / 80米远旗',foot+' / 70°垂直FOV、视高1.62米').save(LOD_DOC/'approach-80m.png')
    dump(LOD_DOC/'preview.json',{'source':'actual great_wall_echo_flags.json exterior faces plus vanilla PNG',
          'native_screenshot':False,'flags_sha256':sha(FLAGS_OUTPUT),'full_nbt_sha256':sha(OUTPUT),
          'full_json_sha256':sha(CLIENT_OUTPUT),'texture_source':str(source),'texture_png_sha256':hashes,
          'blocks':len(client['blocks']),'exposed_faces':len(quads),'frame':'same world frame as full building, no individual flag scaling',
          'ground_plane_y':0,'centerPivot':client['centerPivot'],'animation_included':False,'effects_enabled':False,
          'views':[v[0] for v in views]+['gray','silhouette','approach-80m']})
    print('Rendered seven independent far flag previews; full previews untouched.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--review',action='store_true');args=parser.parse_args()
    if args.review:review()
    elif args.check:check()
    else:build();check()

