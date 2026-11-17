"""Read-only Bixi numeric-channel diagnostic. Source contract in consumer-contract.json.

Not a GeckoLib runtime, controller-history emulator or native acceptance test.
Coordinates are baked render-local blocks; +Y up, front is -Z; renderer Y+.01 included.
"""
from pathlib import Path
import json, hashlib, math, itertools
import numpy as np
from PIL import Image, ImageDraw

O=Path(__file__).resolve().parent; R=O.parents[3]
A=R/'src/main/resources/assets/dynasty'; ID='juli_bixi_kuilei'
gp=A/f'geo/blueprint/{ID}.geo.json'; ap=A/f'animations/blueprint/{ID}.animation.json'
g=json.loads(gp.read_text())['minecraft:geometry'][0]
animations=json.loads(ap.read_text())['animations']; bones={b['name']:b for b in g['bones']}
legs=['front_left','front_right','rear_left','rear_right']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,x): (O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
prior=json.loads((O.parent/'snapping-turtle-whole-body-research-20261111/target-readonly.json').read_text())
protected=[R/x['path'] for x in prior['hashes']]+[R/'src/main/java/com/dynasty/blueprint/client/TemplateSecondaryMotion.java',R/'src/main/java/com/dynasty/blueprint/AnimationProfile.java',R/'build.gradle']
before={str(p.relative_to(R)):sha(p) for p in protected}
assert all(before[x['path']]==x['sha256'] for x in prior['hashes']), 'Current input changed: reassess scope'

def tr(v):
    m=np.eye(4);m[:3,3]=v;return m
def rot(v):
    x,y,z=v;cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz,-sz,0,0],[sz,cz,0,0],[0,0,1,0],[0,0,0,1]])@np.array([[cy,0,sy,0],[0,1,0,0],[-sy,0,cy,0],[0,0,0,1]])@np.array([[1,0,0,0],[0,cx,-sx,0],[0,sx,cx,0],[0,0,0,1]])
def f32(v):return np.asarray(v,dtype=np.float32).astype(float)
def sample(ch,t,default):
    if ch is None:return np.asarray(default,float)
    assert isinstance(ch,dict)
    # Input map order is retained by Gson: no sorting silently repairs an export.
    items=[(float(k),np.array(v,float)) for k,v in ch.items()]
    assert all(isinstance(v,list) and len(v)==3 and all(isinstance(q,(int,float)) for q in v) for v in ch.values())
    assert all(a[0]<=b[0] for a,b in zip(items,items[1:]))
    prev_t=0;prev=items[0][1]
    for end,val in items:
        if end>t:
            return prev+(val-prev)*((t-prev_t)/(end-prev_t))
        prev_t,prev=end,val
    # EasingType.apply returns endpoint when currentTick>=transitionLength.
    return items[-1][1]
def matrices(clip,t):
    channels=animations['animation.'+ID+'.'+clip]['bones']; world={}
    for n,b in bones.items():
        ch=channels.get(n,{});pivot=f32(np.array(b.get('pivot',[0,0,0]))*[-1,1,1])/16
        # Constant rotations converted to radians/signs by the JSON adapter;
        # AnimationProcessor adds initial rotation, casts to float. No easing override here.
        angle=f32(np.radians(b.get('rotation',[0,0,0]))*[-1,-1,1]+np.radians(sample(ch.get('rotation'),t,[0,0,0]))*[-1,-1,1])
        pos=f32(sample(ch.get('position'),t,[0,0,0]))*[-1,1,1]/16
        scale=f32(sample(ch.get('scale'),t,[1,1,1]));s=np.diag([*scale,1.])
        m=tr(pos)@tr(pivot)@rot(angle)@s@tr(-pivot)
        world[n]=(world[b['parent']] if b.get('parent') else tr([0,.01,0]))@m
    return world
def cube_points(n,i,w):
    b=bones[n];c=b['cubes'][i];o=np.array(c['origin'],float);size=np.array(c['size'],float)
    inf=c.get('inflate',b.get('inflate',0)); lo=(o+[-inf,-inf,-inf]);hi=o+size+inf
    pts=np.array([[*p,1] for p in itertools.product(*zip(lo,hi))]);pts[:,0]*=-1;pts[:,:3]/=16
    pivot=np.array(c.get('pivot',[0,0,0]),float)*[-1,1,1]/16
    m=w[n]@tr(pivot)@rot(np.radians(c.get('rotation',[0,0,0]))*[-1,-1,1])@tr(-pivot)
    return (m@pts.T).T[:,:3]
def point(n,p,w):return (w[n]@np.array([-p[0]/16,p[1]/16,p[2]/16,1]))[:3]
def report(clip,t):
    w=matrices(clip,t);row={'seconds':t,'ticks':t*20,'feet':{}}
    for leg in legs:
        n=leg+'_foot'; pts=np.concatenate([cube_points(n,i,w) for i in range(len(bones[n]['cubes']))])
        # Exact separating distance along the shared local Y axis for stomp:
        # foot main cube and piston are axis-aligned in piston coordinates.
        piston=bones[leg+'_piston']['cubes'][0];foot=bones[n]['cubes'][0]
        channels=animations['animation.'+ID+'.'+clip]['bones']
        offset=sample(channels.get(n,{}).get('position'),t,[0,0,0])[1]
        gap=piston['origin'][1]-piston.get('inflate',0)-(foot['origin'][1]+foot['size'][1]+foot.get('inflate',0)+offset)
        row['feet'][leg]={'min_y_blocks':float(pts[:,1].min()),'max_y_blocks':float(pts[:,1].max()),'pivot_blocks':point(n,bones[n]['pivot'],w).tolist(),'piston_to_main_foot_signed_axial_gap_blocks':float(gap/16)}
    row['upper_lip_blocks']=point('head',[0,11,-30],w).tolist()
    row['lower_lip_blocks']=point('jaw',[0,11.02,-30],w).tolist()
    row['lip_marker_distance_blocks']=float(np.linalg.norm(np.array(row['upper_lip_blocks'])-row['lower_lip_blocks']))
    jaw=np.concatenate([cube_points('jaw',i,w) for i in range(2)])
    row['jaw_foremost_z_blocks']=float(jaw[:,2].min())
    row['jaw_min_y_blocks']=float(jaw[:,1].min())
    return row

out={};summaries={}
for clip in ['attack','stomp']:
    data=animations['animation.'+ID+'.'+clip];length=data['animation_length']
    keys=sorted({0.,length}|{float(t) for ch in data['bones'].values() for curve in ch.values() for t in curve})
    ts=sorted(set(keys+[(a+b)/2 for a,b in zip(keys,keys[1:])]+[min(length,i/320) for i in range(math.ceil(length*320)+1)]))
    rows=[report(clip,t) for t in ts];out[clip]=rows
    summaries[clip]={'sample_count':len(rows),'interval_step_seconds':1/320,'foot_extrema':{}}
    for leg in legs:
        summaries[clip]['foot_extrema'][leg]={}
        for field in ['min_y_blocks','piston_to_main_foot_signed_axial_gap_blocks']:
            mi=min(rows,key=lambda row:row['feet'][leg][field]);ma=max(rows,key=lambda row:row['feet'][leg][field])
            summaries[clip]['foot_extrema'][leg][field]={'minimum':mi['feet'][leg][field],'at_min_tick':mi['ticks'],'maximum':ma['feet'][leg][field],'at_max_tick':ma['ticks']}
write('poses.json',out);write('sampling-summary.json',summaries)
selected={clip:[report(clip,t) for t in ts] for clip,ts in {'attack':[0,.7,.8,.9,1.5,2.3],'stomp':[0,.625,1.25,1.55,1.575,1.59375,1.6,1.7,1.875,1.9,3.4]}.items()}
write('selected-poses.json',selected)

# Measured side-projection diagram, not a texture preview or game screenshot.
im=Image.new('RGB',(1440,960),'#f4f1e8');d=ImageDraw.Draw(im)
edges=[(i,j) for i in range(8) for j in range(i+1,8) if (i^j) in [1,2,4]]
for panel,(clip,t) in enumerate([('attack',.7),('attack',.9),('stomp',1.25),('stomp',1.6)]):
    ox=(panel%2)*720+360;oy=(panel//2)*480+400;factor=130
    def xy(p):return (ox-p[2]*factor,oy-p[1]*factor)
    d.line([(ox-325,oy),(ox+325,oy)],fill='#809080',width=2)
    w=matrices(clip,t)
    for n,b in bones.items():
        if n=='stele':continue # body-only diagnostic, not accessory production
        color='#9da39e'
        if n in ['neck_base','neck_tip','head','jaw']:color='#a04c30'
        if n.endswith('_piston'):color='#26758c'
        if n.endswith('_foot'):color='#464caa'
        for i,c in enumerate(b.get('cubes',[])):
            p=cube_points(n,i,w)
            for a,z in edges:d.line([xy(p[a]),xy(p[z])],fill=color,width=2)
    d.text((ox-320,oy-375),f'{clip} / {t*20:g} tick - measured side projection',fill='#202d30')
    for name in ['head','jaw']:
        p=point(name,[0,11 if name=='head' else 11.02,-30],w);x,y=xy(p);d.ellipse([x-4,y-4,x+4,y+4],fill='#c03040')
    d.text((ox-320,oy+28),'Reference plane Y=0; no terrain, particles or native game claim.',fill='#36443f')
im.save(O/'contact-diagram.png')
after={str(p.relative_to(R)):sha(p) for p in protected};assert before==after
write('input-guards.json',dict(before=before,after=after,unchanged=True))
print(json.dumps({'selected_attack_contact':selected['attack'][3], 'stomp_extrema':summaries['stomp'],'protected_unchanged':True},indent=2))
