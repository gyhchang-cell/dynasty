#!/usr/bin/env python3
"""Inspect actual exports, UVs, serial joints and combat ports. No Java/native execution."""
from pathlib import Path
import hashlib, importlib.util, json, math
from functools import lru_cache
from types import SimpleNamespace
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[2]
A=R/'src/main/resources/assets/dynasty'
D=R/'docs/blueprint-cod1/evidence/taoyan-cauldron-v1'
ID='taoyan_zhishi'
CLIPS={'idle','walk','intro','ram','whip','oil','bells','transition','slam','drink','hurt','death'}
paths=[]
def pairs(rows):
    out={}
    for k,v in rows:
        assert k not in out,('duplicate JSON key',k)
        out[k]=v
    return out
def read(p):
    paths.append(p)
    return json.loads(p.read_text(),object_pairs_hook=pairs)
spec=importlib.util.spec_from_file_location('actual_cauldron_geometry',R/'tools/art/secondary-cuboid/review_models.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/boss'
# Memoize parsing in the unchanged geometry reader; changed file contents produce a new key.
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
    prefix=ID if identifier in (ID,ID+'_phase2') else identifier
    return r.geometry(identifier,clip='animation.'+prefix+'.'+clip,tick=tick)
report={'source':'actual source/export inspection and software sampling only; native build/game not run',
        'samplesPerClip':81,'forms':{},'auxiliaryGeometry':{}}
for identifier in (ID,ID+'_phase2','taoyan_bounded_corpse_oil','taoyan_growing_fire_fissure'):
    g=read(A/f'geo/blueprint/boss/{identifier}.geo.json')['minecraft:geometry'][0]
    anim=read(A/f'animations/blueprint/boss/{identifier}.animation.json')['animations']
    bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones'])
    assert g['description']['texture_width']==g['description']['texture_height']==16
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
                texture=identifier if identifier in (ID,ID+'_phase2') else ID
                im=Image.open(A/f'textures/entity/blueprint/boss/{texture}.png').convert('RGB')
                assert len({im.getpixel((x,y)) for x in range(u,u+w) for y in range(v,v+h)})==1,('UV crosses material island',identifier,b['name'])
    primary=identifier in (ID,ID+'_phase2');prefix=ID if primary else identifier
    assert set(anim)=={'animation.'+prefix+'.'+c for c in (CLIPS if primary else {'idle'})}
    for name,definition in anim.items():
        assert set(definition['bones'])<=set(bones) and 0<definition['animation_length']<=10
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
        pts=np.concatenate([p for p,u,b in geometry(identifier)])
        assert np.isfinite(pts).all() and pts[:,1].min()>=0
        report['auxiliaryGeometry'][identifier]={'counts':counts,'dimensionsMetres':((pts.max(0)-pts.min(0))/16).round(4).tolist()}
        continue
    clips={};jointErrors=[];whipErrors=[];ports=[]
    for name,definition in anim.items():
        clip=name.rsplit('.',1)[1];samples=[]
        for tick in np.linspace(0,definition['animation_length']*20,81):
            q=geometry(identifier,clip,float(tick));pts=np.concatenate([p for p,u,b in q]);assert np.isfinite(pts).all()
            assert pts[:,1].min()>=-1e-4,('below floor',identifier,clip,tick,pts[:,1].min())
            assert pts[:,1].max()/16<9 and np.abs(pts[:,[0,2]]).max()/16<9,('renderer cull',identifier,clip,tick)
            live=visible(q);grounded=sum(any(b==foot and abs(p[:,1].min())<.2 for p,u,b in live) for foot in bones if foot.endswith('_foot'))
            if clip=='walk':assert grounded>=(2 if identifier==ID else 7),('lost walking supports',identifier,tick,grounded)
            if clip=='transition' and identifier!=ID:assert grounded>=3,('airborne morph',tick,grounded)
            samples.append({'minimumY':float(pts[:,1].min()),'maximumY':float(pts[:,1].max()),'maximumRadius':float(np.linalg.norm(pts[:,[0,2]],axis=1).max()),'groundedFeet':grounded})
            w=matrices(g,definition,float(tick))
            if clip!='death':
                for foot in (n for n in bones if n.endswith('_foot')):
                    n=foot.removesuffix('_foot');shin=n+'_shin'
                    if not np.allclose(np.linalg.norm(w[shin][:3,:3],axis=0),1,atol=1e-5) or not np.allclose(np.linalg.norm(w[foot][:3,:3],axis=0),1,atol=1e-5):continue
                    jointErrors.append(float(np.linalg.norm((w[shin]@np.array([0,-14,0,1])-w[foot]@np.array([0,0,0,1]))[:3])))
            for i in range(11):
                whipErrors.append(float(np.linalg.norm((w['bone_whip_'+str(i)]@np.array([-6,0,0,1])-w['bone_whip_'+str(i+1)]@np.array([0,0,0,1]))[:3])))
        clips[clip]={'minimumY':min(s['minimumY'] for s in samples),'maximumY':max(s['maximumY'] for s in samples),'maximumRadius':max(s['maximumRadius'] for s in samples),'minGroundedFeet':min(s['groundedFeet'] for s in samples),'sampleCount':81}
    assert max(jointErrors)<.04,('serial support detached',identifier,max(jointErrors))
    assert max(whipErrors)<1e-5,('serial whip detached',identifier,max(whipErrors))
    # Compare actual straight whip direction/anchor to all six native damage frames,
    # including Gecko X conversion and the renderer's180-degree body rotation.
    for tick in (18,23,28,33,38,43):
        w=matrices(g,anim['animation.'+ID+'.whip'],tick)
        start=(w['bone_whip_0']@np.array([0,0,0,1]))[:3]*[-1,1,-1]/16
        end=(w['bone_whip_11']@np.array([-6,0,0,1]))[:3]*[-1,1,-1]/16
        a=math.radians(-135+(tick-18)*270/29);native=np.array([-math.sin(a),0,math.cos(a)])
        d=(end-start)/np.linalg.norm(end-start)
        assert np.linalg.norm(d-native)<1e-5 and np.allclose(start,[27/16,15/16,0],atol=1e-5),(identifier,'whip native port',tick,start,d,native)
        ports.append({'tick':tick,'nativeAnchorMetres':start.round(6).tolist(),'maximumDirectionError':float(np.linalg.norm(d-native))})
    assert not visible(geometry(identifier,'death',160)),('death mesh remains after160t',identifier)
    body=np.concatenate([p for p,u,b in visible(geometry(identifier)) if b in ('war_cauldron','boiling_oil','cauldron_maw','maw_lower_hinge') or b.startswith(('tripod_','bone_strut_'))])
    full=np.concatenate([p for p,u,b in visible(geometry(identifier))])
    report['forms'][identifier]={'counts':counts,'clips':clips,'coreAndSupportsDimensionsMetres':((body.max(0)-body.min(0))/16).round(4).tolist(),'restVisibleDimensionsMetres':((full.max(0)-full.min(0))/16).round(4).tolist(),'maximumHorizontalRadiusMetres':round(max(v['maximumRadius'] for v in clips.values())/16,6),'serialSupportMaxErrorMetres':round(max(jointErrors)/16,7),'serialWhipMaxErrorMetres':round(max(whipErrors)/16,7),'nativeWhipPortSamples':ports,'deathMeshInvisibleAtTick':160}
for p in [A/f'textures/entity/blueprint/boss/{n}.png' for n in (ID,ID+'_phase2')]+[A/f'textures/item/{n}.png' for n in ('taoyan_bronze_cauldron_ear','taoyan_quenched_siege_stake','taoyan_army_soul_crystal')]:
    paths.append(p);im=Image.open(p).convert('RGB');assert im.size==(16,16) and 2<=len(set(im.get_flattened_data()))<=4
    for y in range(16):
        for x in range(16):
            c=im.getpixel((x,y))
            if x<2 or x>13 or y<2 or y>13:assert c==(255,255,255)
            assert any(all(im.getpixel((xx,yy))==c for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15),(p,'colour region smaller than2x2',x,y)
data=R/'src/main/resources/data/dynasty'
for p in [data/f'loot_tables/entities/{ID}.json',data/f'advancements/blueprint/kill_{ID}.json',data/'tags/worldgen/structure/blueprint/cauldron_pits.json',data/'worldgen/structure/cauldron_pit.json',data/'worldgen/structure_set/cauldron_pit.json',data/'damage_type/taoyan_crushing.json',R/'src/main/resources/data/minecraft/tags/damage_type/bypasses_shield.json']:
    read(p)
for n in ('taoyan_bronze_cauldron_ear','taoyan_quenched_siege_stake','taoyan_army_soul_crystal'):
    read(A/f'models/item/{n}.json');read(data/f'recipes/blueprint/{n}_recycle.json')
read(A/f'models/item/{ID}_spawn_egg.json')
for n in ('cauldron_bone_ritual','cauldron_abyss_oil'):
    read(A/f'blockstates/{n}.json');read(A/f'models/block/{n}.json')
read(A/'models/item/cauldron_bone_ritual.json')
for locale in ('zh_cn','en_us'):
    lang=read(A/f'lang/{locale}.json');assert 'entity.dynasty.'+ID in lang
paths.extend((R/'src/main/java/com/dynasty/blueprint/boss').rglob('*.java'))
paths.extend(R/p for p in ('src/main/java/com/dynasty/DynastyContent.java','src/main/java/com/dynasty/blueprint/BlueprintVisualEvent.java','src/main/java/com/dynasty/blueprint/client/BlueprintVisuals.java','tools/blueprint/generate_taoyan_cauldrons.py','tools/blueprint/review_taoyan_cauldrons.py','tools/blueprint/validate_taoyan_cauldrons.py','src/main/resources/data/dynasty_army/structures/cauldron_pit_test.nbt'))
report['nativePhysicsDimensionsMetres']={'width':4.8,'height':4.5,'bothFormsSameCollider':True,'spellAnchorWidth':.1,'spellAnchorHeight':.1}
report['nativeClientCullMetres']={'bodyHalfXZ':9,'bodyRelativeY':[-1,9],'spellDistance':96,'oilRadiusMargin':6.5,'fissureActualEndpointMargin':1}
report['nativeArena']={'centreSpanMetres':40,'voxelOutlineWidth':41,'safePlatformRadius':17,'pillars':12,'boneOfferings':3,'summonUUIDCap':1,'environmentEditBudgetPer10Ticks':64,'nearbyPitTickBudget':2}
report['staticChecks']='PASS_SOURCE_SOFTWARE_ONLY'
report['nativeChecks']='NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
D.mkdir(parents=True,exist_ok=True);(D/'validated-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS_SOURCE_SOFTWARE_ONLY',json.dumps({n:v['counts'] for n,v in report['forms'].items()}),'24clips x81samples; native NOT RUN')
