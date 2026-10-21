#!/usr/bin/env python3
"""Read-only nearest-UV software review, distinct from native game evidence."""
import base64,hashlib,itertools,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='scenic'
A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'docs/art/cod3-xuanwu-v2';D.mkdir(parents=True,exist_ok=True)
IDS=['mountain_xuanwu'];records={}
allq={n:v.r.geometry(n,clip='animation.scenic.idle',tick=0) for n in IDS}
common=np.concatenate([q[0]*4 for quads in allq.values() for q in quads])
for name in IDS:
    geo=json.loads((A/f'geo/scenic/{name}.geo.json').read_text())['minecraft:geometry'][0]
    anim=json.loads((A/f'animations/scenic/{name}.animation.json').read_text())['animations']['animation.scenic.idle']
    tex=np.array(Image.open(A/f'textures/entity/scenic/{name}.png').convert('RGB'))
    th,tw=tex.shape[:2];assert (tw,th)==(geo['description']['texture_width'],geo['description']['texture_height'])
    bones={b['name']:b for b in geo['bones']};assert len(bones)==len(geo['bones'])
    source=json.loads((D/f'blockbench/{name}.bbmodel').read_text())
    assert base64.b64decode(source['textures'][0]['source'].split(',',1)[1])==(A/f'textures/entity/scenic/{name}.png').read_bytes()
    assert json.loads((D/f'blockbench/{name}.animation.json').read_text())['animations']['animation.scenic.idle']==anim
    original_cubes=[c for b in geo['bones'] for c in b.get('cubes',[])]
    assert len(source['elements'])==len(original_cubes)
    for element,cube in zip(source['elements'],original_cubes):
        x,y,z=cube['origin'];w,h,d=cube['size']
        assert element['from']==[-x-w,y,z] and element['to']==[-x,y+h,z+d]
    lod_counts={}
    for lod in ('medium','far'):
        reduced=json.loads((A/f'geo/scenic/{name}_{lod}.geo.json').read_text())['minecraft:geometry'][0]
        assert [{k:v for k,v in b.items() if k!='cubes'} for b in reduced['bones']]==[{k:v for k,v in b.items() if k!='cubes'} for b in geo['bones']]
        for b,full in zip(reduced['bones'],geo['bones']):assert all(c in full['cubes'] for c in b['cubes'])
        lod_counts[lod]=sum(len(b['cubes']) for b in reduced['bones'])
    assert len(original_cubes)>lod_counts['medium']>lod_counts['far']>0
    for b in geo['bones']:
        assert 'parent' not in b or b['parent'] in bones
        for c in b.get('cubes',[]):
            assert min(c['size'])>0
            for f in c['uv'].values():
                u,w=f['uv'];du,dv=f['uv_size'];assert min(u,w)>=1 and u+du<tw and w+dv<th
    assert set(anim['bones'])<=set(bones)
    for channels in anim['bones'].values():
        for track in channels.values():assert track['0']==track['4']
    out=D/name;out.mkdir(exist_ok=True)
    q=allq[name];scaled=[(p*4,uv,bone) for p,uv,bone in q]
    frame=np.concatenate([p for p,_,_ in scaled]);frames=[];bounds=[]
    for tick in np.linspace(0,80,81):
        pose=v.r.geometry(name,clip='animation.scenic.idle',tick=float(tick));points=np.concatenate([x[0] for x in pose])*4
        bounds.append([points.min(0).tolist(),points.max(0).tolist()])
    envelope_lo=np.min([b[0] for b in bounds],axis=0);envelope_hi=np.max([b[1] for b in bounds],axis=0)
    # Use every bounding-box corner. Two diagonal points incorrectly crop opposite 45-degree views.
    motionframe=np.array(list(itertools.product(*zip(envelope_lo,envelope_hi))))
    # All three original rigs face +Z: front is viewed from +Z, not -Z.
    for yaw,label in [(180,'front'),(135,'45'),(90,'right'),(-90,'left'),(0,'back')]:
        v.labelled(v.raster(scaled,tex,yaw=yaw,size=(900,620),mode='lit',frame_points=motionframe),name+' / '+label).save(out/(label+'.png'))
    for mode in ['gray','dim']:
        v.labelled(v.raster(scaled,tex,yaw=135,size=(900,620),mode=mode,frame_points=motionframe),name+' / '+mode).save(out/(mode+'.png'))
    v.labelled(v.raster(scaled,np.zeros_like(tex),yaw=135,size=(900,620),frame_points=motionframe),name+' / silhouette').save(out/'silhouette.png')
    for lod in ('medium','far'):
        reduced=[(p*4,uv,b) for p,uv,b in v.r.geometry(name,clip='animation.scenic.idle',tick=0,geo_path=A/f'geo/scenic/{name}_{lod}.geo.json')]
        v.labelled(v.raster(reduced,tex,yaw=135,size=(900,620),frame_points=motionframe),name+' / '+lod+' LOD').save(out/(lod+'.png'))
    sheet=Image.new('RGB',(1800,620),'#d6dddf')
    for i,label in enumerate(['front','45','right','left','back','gray','silhouette','dim']):
        with Image.open(out/(label+'.png')) as im:sheet.paste(im.resize((450,310),Image.Resampling.NEAREST),(i%4*450,i//4*310))
    sheet.save(out/'overview.png')
    refs=v.references(np.array([-220,0,0]));
    v.labelled(v.raster(scaled+refs,tex,yaw=135,size=(1100,700),frame_points=np.concatenate([common,*[x[0] for x in refs]]),mode='lit'),name+' / x4 world scale / player 1.8m').save(out/'world-scale.png')
    for tick in np.linspace(0,80,17):
        pose=[(p*4,uv,bone) for p,uv,bone in v.r.geometry(name,clip='animation.scenic.idle',tick=float(tick))]
        frames.append(v.labelled(v.raster(pose,tex,yaw=135,size=(600,420),frame_points=motionframe,mode='lit'),name+f' / {tick:.0f} ticks'))
    frames[0].save(out/'idle.webp',save_all=True,append_images=frames[1:],duration=235,loop=0,lossless=True)
    lo=np.min([b[0] for b in bounds],axis=0)/16;hi=np.max([b[1] for b in bounds],axis=0)/16
    records[name]={'samples':81,'lod_cubes':lod_counts,'world_envelope_metres':[lo.tolist(),hi.tolist()],'world_visible_size_metres':(hi-lo).tolist(),'collision':'none','server_entity':'none','source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [A/f'geo/scenic/{name}.geo.json',A/f'geo/scenic/{name}_medium.geo.json',A/f'geo/scenic/{name}_far.geo.json',A/f'animations/scenic/{name}.animation.json',A/f'textures/entity/scenic/{name}.png']},'software_preview_only':True}
dump=D/'software-validation.json';dump.write_text(json.dumps(records,indent=2)+'\n')
print('PASS: independent bones, full face UVs, looping keys, 81 samples each and five angles + gray/black/weak light.')
