#!/usr/bin/env python3
"""Inspect actual two-form exports while user has paused Java/native execution.
This narrowly checks the required floor/joint/weapon-port contract; it is not game proof.
"""
from pathlib import Path
import hashlib, importlib.util, json, math
from functools import lru_cache
from types import SimpleNamespace
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty'
D=R/'docs/blueprint-cod1/evidence/blind-marshal-v1';ID='gongsun_wuwang'
FORMS=(ID,ID+'_foot')
CLIPS={'idle','walk','intro','trample','slash','listen','arrows','morph','onslaught','storm','hurt','death'}
AUX=('marshal_sand_blade','marshal_wall_arrow','marshal_blood_fissure')
ITEMS=('marshal_broken_horse_cleaver','marshal_broken_wing_helmet','marshal_last_city_oath')
paths=[]
def pairs(rows):
    out={}
    for k,v in rows:
        assert k not in out,('duplicate JSON key',k)
        out[k]=v
    return out
def read(p):
    paths.append(p);return json.loads(p.read_text(),object_pairs_hook=pairs)
spec=importlib.util.spec_from_file_location('actual_marshal_geometry',R/'tools/art/secondary-cuboid/review_models.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/boss'
r.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads))
def matrices(g,definition,tick):
    piv={b['name']:np.array(b['pivot'],float) for b in g['bones']};world={}
    for b in g['bones']:
        ch=definition['bones'].get(b['name'],{})
        pos=piv[b['name']]-(piv[b['parent']] if b.get('parent') else np.zeros(3))
        pos+=r.sample(ch.get('position',[0,0,0]),tick/20)
        rot=np.array(b.get('rotation',[0,0,0]),float)+r.sample(ch.get('rotation',[0,0,0]),tick/20)
        sc=r.sample(ch.get('scale',[1,1,1]),tick/20)
        world[b['name']]=(world[b['parent']] if b.get('parent') else np.eye(4))@r.transform(pos,rot,sc)
    return world
def visible(q):
    return [(p,u,b) for p,u,b in q if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))>1e-8]
def geometry(identifier,clip='idle',tick=0):
    return r.geometry(identifier,clip='animation.'+(ID if identifier in FORMS else identifier)+'.'+clip,tick=tick)
report={'source':'actual source/export inspection and software sampling only; no native build/game execution',
        'samplesPerClip':81,'forms':{},'auxiliaryGeometry':{}}
for identifier in FORMS+AUX:
    g=read(A/f'geo/blueprint/boss/{identifier}.geo.json')['minecraft:geometry'][0]
    anim=read(A/f'animations/blueprint/boss/{identifier}.animation.json')['animations']
    bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones'])
    assert g['description']['texture_width']==g['description']['texture_height']==16
    texture=Image.open(A/f'textures/entity/blueprint/boss/{identifier if identifier in FORMS else ID}.png').convert('RGB')
    for b in bones.values():
        assert all(math.isfinite(x) for x in b['pivot'])
        chain=set();p=b
        while p.get('parent'):
            assert p['name'] not in chain;chain.add(p['name']);p=bones[p['parent']]
        for c in b.get('cubes',[]):
            assert all(x>0 and math.isfinite(x) for x in c['size'])
            assert all(math.isfinite(x) for x in c['origin'])
            for uv in c['uv'].values():
                u,v=uv['uv'];w,h=uv['uv_size']
                assert all(isinstance(x,int) for x in (u,v,w,h)) and min(u,v)>=0 and min(w,h)>0 and u+w<=16 and v+h<=16
                assert len({texture.getpixel((x,y)) for x in range(u,u+w) for y in range(v,v+h)})==1,('UV crosses material island',identifier,b['name'])
    primary=identifier in FORMS;prefix=ID if primary else identifier
    assert set(anim)=={'animation.'+prefix+'.'+c for c in (CLIPS if primary else {'idle'})}
    for name,definition in anim.items():
        assert set(definition['bones'])<=set(bones) and 0<definition['animation_length']<=12
        for ch in definition['bones'].values():
            for channel,track in ch.items():
                if isinstance(track,dict):
                    assert all(0<=float(t)<=definition['animation_length'] for t in track)
                    assert all(math.isfinite(x) for v in track.values() for x in v)
                    if definition.get('loop'):
                        ordered=sorted(track,key=float);diff=np.array(track[ordered[-1]])-track[ordered[0]]
                        if channel=='rotation':diff=(diff+180)%360-180
                        assert np.allclose(diff,0),('loop seam',identifier,name,channel)
                else:assert all(math.isfinite(x) for x in track)
    counts={'bones':len(bones),'cuboids':sum(len(b.get('cubes',[])) for b in bones.values()),'clips':len(anim)}
    if not primary:
        pts=np.concatenate([p for p,u,b in geometry(identifier)]);assert np.isfinite(pts).all()
        if identifier.endswith('fissure'):assert pts[:,1].min()>=0
        if identifier.endswith('wall_arrow'):assert abs(pts[:,1].max())<1e-8,('arrow head must end at native impact anchor',pts[:,1].max())
        if identifier.endswith('sand_blade'):assert pts[:,1].min()/16+1.1>0,('flying blade crosses target floor')
        report['auxiliaryGeometry'][identifier]={'counts':counts,'dimensionsMetres':((pts.max(0)-pts.min(0))/16).round(4).tolist(),'anchorRelativeYMetres':(np.array([pts[:,1].min(),pts[:,1].max()])/16).round(4).tolist()}
        continue
    clips={};jointErrors=[];ports=[]
    for name,definition in anim.items():
        clip=name.rsplit('.',1)[1];samples=[]
        for tick in np.linspace(0,definition['animation_length']*20,81):
            q=geometry(identifier,clip,float(tick));pts=np.concatenate([p for p,u,b in q]);assert np.isfinite(pts).all()
            assert pts[:,1].min()>=-1e-4,('below floor',identifier,clip,tick,pts[:,1].min())
            assert pts[:,1].max()/16<13 and np.abs(pts[:,[0,2]]).max()/16<8,('renderer cull',identifier,clip,tick)
            live=visible(q)
            grounded=sum(any(b==foot and abs(p[:,1].min())<.2 for p,u,b in live) for foot in bones if foot.endswith(('_hoof','_rocker')))
            if clip in ('walk','trample','onslaught'):assert grounded>=(3 if identifier==ID else 2),('lost supports',identifier,clip,tick,grounded)
            if identifier==ID and clip=='trample' and tick<=20:assert grounded==4,('windup must remain planted',tick,grounded)
            if identifier!=ID and clip=='morph':
                assert grounded>=2,('airborne morph',tick,grounded)
                shrineBottom=min(p[:,1].min() for p,u,b in live if b=='oath_shrine')
                supportTop=max(p[:,1].max() for p,u,b in live if b in ('old_bone_horse','left_rocker','right_rocker'))
                assert shrineBottom<=supportTop+.2,('unsupported shrine during morph',tick,shrineBottom,supportTop)
            samples.append({'minimumY':float(pts[:,1].min()),'maximumY':float(pts[:,1].max()),'maximumRadius':float(np.linalg.norm(pts[:,[0,2]],axis=1).max()),'groundedSupports':grounded})
            w=matrices(g,definition,float(tick))
            if clip!='death':
                for foot in (n for n in bones if n.endswith('_hoof')):
                    shin=foot.removesuffix('_hoof')+'_shin'
                    shinScale=np.linalg.norm(w[shin][:3,:3],axis=0);footScale=np.linalg.norm(w[foot][:3,:3],axis=0)
                    if min(shinScale)<1e-6 or not np.allclose(shinScale,footScale,atol=1e-5):continue
                    jointErrors.append(float(np.linalg.norm((w[shin]@np.array([0,-14,0,1])-w[foot]@np.array([0,0,0,1]))[:3])))
        clips[clip]={'minimumY':min(s['minimumY'] for s in samples),'maximumY':max(s['maximumY'] for s in samples),'maximumRadius':max(s['maximumRadius'] for s in samples),'minGroundedSupports':min(s['groundedSupports'] for s in samples),'sampleCount':81}
    assert max(jointErrors)<.04,('serial horse joint detached',identifier,max(jointErrors))
    # Native projectile and warning origin must coincide with the real blade tip.
    # Gecko X conversion and renderer body rotation map model XYZ to (-X,Y,-Z).
    for clip,ticks in (('slash',(16,)),('onslaught',(16,24,32,40,48,56,64))):
        for tick in ticks:
            w=matrices(g,anim['animation.'+ID+'.'+clip],tick)
            port=(w['four_metre_glaive']@np.array([0,48,0,1]))[:3]*[-1,1,-1]/16
            angle=math.radians(120 if identifier==ID else 100)
            expected=np.array([0,((43 if identifier==ID else 27)+50*math.cos(angle))/16,(18+50*math.sin(angle))/16])
            assert np.allclose(port,expected,atol=1e-5),('native blade tip mismatch',identifier,clip,tick,port,expected)
            ports.append({'clip':clip,'sourceTick':tick,'nativeAnchorMetres':port.round(6).tolist(),'maximumErrorMetres':float(np.linalg.norm(port-expected))})
    assert not visible(geometry(identifier,'death',200)),('death mesh remains after200t',identifier)
    live=visible(geometry(identifier));core=np.concatenate([p for p,u,b in live if b not in ('glaive_bearing','two_grip_yoke','four_metre_glaive')]);full=np.concatenate([p for p,u,b in live])
    report['forms'][identifier]={'counts':counts,'clips':clips,'coreAndSupportsDimensionsMetres':((core.max(0)-core.min(0))/16).round(4).tolist(),'restVisibleDimensionsMetres':((full.max(0)-full.min(0))/16).round(4).tolist(),'maximumHorizontalRadiusMetres':round(max(v['maximumRadius'] for v in clips.values())/16,6),'serialHorseJointMaxErrorMetres':round(max(jointErrors)/16,7),'nativeBladePortSamples':ports,'deathMeshInvisibleAtTick':200}
for p in [A/f'textures/entity/blueprint/boss/{n}.png' for n in FORMS]+[A/f'textures/item/{n}.png' for n in ITEMS]:
    paths.append(p);im=Image.open(p).convert('RGB');assert im.size==(16,16) and 2<=len(set(im.get_flattened_data()))<=4
    for y in range(16):
        for x in range(16):
            c=im.getpixel((x,y))
            if x<2 or x>13 or y<2 or y>13:assert c==(255,255,255)
            assert any(all(im.getpixel((xx,yy))==c for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15),(p,'colour region smaller than2x2',x,y)
data=R/'src/main/resources/data/dynasty'
for p in [data/f'loot_tables/entities/{ID}.json',data/f'advancements/blueprint/kill_{ID}.json',data/'tags/worldgen/structure/blueprint/marshal_yards.json',data/'worldgen/structure/marshal_courtyard.json',data/'worldgen/structure_set/marshal_courtyard.json']:
    read(p)
for n in ITEMS:
    read(A/f'models/item/{n}.json');read(data/f'recipes/blueprint/{n}_recycle.json')
for p in (A/f'models/item/{ID}_spawn_egg.json',A/'blockstates/marshal_oath_socket.json',A/'models/block/marshal_oath_socket.json',A/'models/item/marshal_oath_socket.json'):read(p)
for locale in ('zh_cn','en_us'):
    lang=read(A/f'lang/{locale}.json');assert 'entity.dynasty.'+ID in lang
java=('BlindMarshal','BlindMarshalNoise','MarshalProjectile','BlindMarshalContent','MarshalCourtyardState','MarshalCourtyardPiece','MarshalCourtyardStructure','MarshalCourtyards','BlindMarshalGameTests','client/BlindMarshalRenderer')
paths.extend(R/f'src/main/java/com/dynasty/blueprint/boss/{n}.java' for n in java)
paths.extend(R/p for p in ('src/main/java/com/dynasty/DynastyContent.java','src/main/java/com/dynasty/blueprint/BlueprintVisualEvent.java','src/main/java/com/dynasty/blueprint/client/BlueprintVisuals.java','tools/blueprint/generate_blind_marshal.py','tools/blueprint/review_blind_marshal.py','tools/blueprint/validate_blind_marshal.py','src/main/resources/data/dynasty_army/structures/cauldron_pit_test.nbt'))
report['nativePhysicsDimensionsMetres']={'width':5.2,'height':3.8,'bothFormsSameCollider':True,'phase2CoreHeight':2.8,'projectileAnchorWidth':.35,'projectileAnchorHeight':.35}
report['nativeClientCullMetres']={'bodyHalfXZ':8,'bodyRelativeY':[-1,13],'projectileDistance':96,'projectileFrustumMargin':1.5}
report['nativeArena']={'centreSpanMetres':32,'voxelOutlineWidth':33,'wallHeight':15,'openGateWidth':7,'arrowPorts':8,'summonUUIDCap':1,'wallArrows':24,'ownedEffectCap':32,'maxDamageTargets':16,'nearbyYardTickBudget':2}
report['staticChecks']='PASS_SOURCE_SOFTWARE_ONLY';report['nativeChecks']='NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
D.mkdir(parents=True,exist_ok=True);(D/'validated-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS_SOURCE_SOFTWARE_ONLY',json.dumps({n:v['counts'] for n,v in report['forms'].items()}),'24clips x81samples; native NOT RUN')
