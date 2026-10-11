"""Compatibility and art-integration acceptance for the authored bird resources."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image
from build_model import REPO,GEO,ANIM,TEX,SOURCE,ID
from review_model import geometry,sample

g=json.loads(GEO.read_text())['minecraft:geometry'][0]
before=json.loads((SOURCE/'original.geo.json').read_text())['minecraft:geometry'][0]
a=json.loads(ANIM.read_text())['animations']
old=json.loads((SOURCE/'original.animation.json').read_text())['animations']
contract=lambda m:[(b['name'],b.get('parent')) for b in m['bones']]
assert contract(g)==contract(before) and len(g['bones'])==74
names={b['name'] for b in g['bones']}
assert len(names)==74 and 'face_8' not in names
assert all(f'face_{n}' in names and f'neck_{n}_tip' in names for n in range(8))
assert 'root' in names and 'central_stump' in names
assert set(a)==set(old) and len(a)==7
im=Image.open(TEX).convert('RGB');assert im.size==(16,16)
assert (g['description']['texture_width'],g['description']['texture_height'])==im.size
colors=im.getcolors(256);assert colors is not None and len(colors)==4
white=(255,255,255)
assert all(im.getpixel((x,y))==white for x in range(16) for y in range(16)
           if x in (0,15) or y in (0,15)), 'Missing white margin'
assert all(len(set(im.crop((x,y,x+2,y+2)).getdata()))==1
           for x in range(1,15,2) for y in range(1,15,2)), 'Sub-2x2 colour region'
for b in g['bones']:
    for c in b.get('cubes',[]):
        assert all(math.isfinite(v) for v in c['origin']+c['size']) and all(v>0 for v in c['size'])
        assert set(c['uv'])=={'north','south','east','west','up','down'}
        for f in c['uv'].values():
            assert all(isinstance(v,int) for v in f['uv']+f['uv_size'])
            assert f['uv_size']==[2,2]
            assert all(1<=v and v+s<=15 for v,s in zip(f['uv'],f['uv_size']))
for name,clip in a.items():
    assert clip['animation_length']==old[name]['animation_length']
    assert set(clip['bones'])<=names
    for ch in clip['bones'].values():
        for track in ch.values():
            if isinstance(track,dict):
                assert all(0<=float(k)<=clip['animation_length'] for k in track)
                assert all(len(v)==3 and all(math.isfinite(n) for n in v) for v in track.values())
                if clip['loop']:assert np.allclose(sample(track,0),sample(track,clip['animation_length']))
peck=a['animation.'+ID+'.peck']['bones']
for strike in range(16):
    frame=12+strike*4;track=peck[f'neck_{strike%8}_base']['rotation']
    assert np.isclose(sample(track,frame/20)[0],138)
    assert sample(track,(frame-1)/20)[0]<138 and sample(track,(frame+1)/20)[0]<138
assert np.isclose(sample(a['animation.'+ID+'.bomb']['bones']['neck_0_base']['rotation'],1)[0],25)
assert np.isclose(sample(a['animation.'+ID+'.dive']['bones']['body']['rotation'],1.2)[0],40)
rest=np.concatenate([v for v,_,_ in geometry()]);span=(rest[:,0].max()-rest[:,0].min())/16
assert abs(span-5)<.01
floor=[]
for tick in range(44,101,2):
    pts=np.concatenate([v for v,_,_ in geometry('death',tick)])
    floor.append(float(pts[:,1].min()))
assert min(floor)>=0, f'Corpse geometry below floor: {min(floor)}'
baseline=json.loads((SOURCE/'baseline-sha256.json').read_text())
untouched=['src/main/resources/assets/dynasty/textures/entity/nian_beast.png','src/main/java/com/dynasty/blueprint/elite/GhostCarriageBird.java']
for path in untouched:assert hashlib.sha256((REPO/path).read_bytes()).hexdigest()==baseline[path],path+' changed'
renderer=(REPO/'src/main/java/com/dynasty/blueprint/elite/client/GhostBirdRenderer.java').read_text()
assert 'textures/entity/blueprint/elite/' in renderer and 'textures/entity/nian_beast.png' not in renderer
report={'result':'PASS','bones':74,'cuboids':sum(len(b.get('cubes',[])) for b in g['bones']),
        'clips':list(a),'unchangedHierarchy':True,'wingspanBlocks':span,'textureSize':list(im.size),
        'palette':sorted('#%02x%02x%02x'%c for count,c in colors),'whiteMargin':1,'colourBlockPixels':2,
        'peckContactTicks':list(range(12,73,4)),
        'bloodContactTick':20,'diveStartTick':24,'settledDeathMinY':min(floor),'unchangedFiles':untouched,
        'files':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [GEO,ANIM,TEX]}}
(REPO/'docs/art/guiche-v2/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
