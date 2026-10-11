"""Export, check and review the focal pass without rebuilding any body."""
import json,sys,hashlib,runpy
import numpy as np
from PIL import Image,ImageDraw
from build import R,A,IDS,NAMES
from retexture import run as retexture
from focus_motion import refine
import texture_review as v
D=R/'docs/art/boss-presence-v4'
TARGETS=['pilin_zhijinwu','undead_first_emperor','juchui_jinjia_lishi']
SAMPLES={'pilin_zhijinwu':[('idle',0),('sweep',15),('sweep',20),('sweep',45)],
 'undead_first_emperor':[('idle',0),('idle',32),('attack',0),('attack',16)],
 'juchui_jinjia_lishi':[('idle',0),('slam',24),('slam',28),('slam',75)]}
ATTACKS={'undead_first_emperor':'attack','pilin_zhijinwu':'sweep','juchui_jinjia_lishi':'slam'}
LABELS=('BEFORE / 原待机、原PNG','AFTER / 新待机、新PNG · 同相机同比例')

def export():
 retexture(TARGETS,D)
 for id in TARGETS:
  p=A/'animations/boss_forms'/(id+'.animation.json');doc=json.loads(p.read_text())
  refine(doc['animations'],id);p.write_text(json.dumps(doc,indent=2)+'\n')
 runpy.run_path(str(R/'tools/art/boss-forms/export_bbmodel.py'),run_name='__main__')

def validate():
 report={}
 for id in IDS+['hammer_chain']:
  gpath=A/'geo/boss_forms'/(id+'.geo.json');before=D/'before'/(id+'.geo.json')
  assert json.loads(gpath.read_text())==json.loads(before.read_text()),(id,'geometry OR UV changed')
  g=json.loads(gpath.read_text())['minecraft:geometry'][0];im=Image.open(A/'textures/entity/boss_forms'/(id+'.png'))
  assert im.size==(g['description']['texture_width'],g['description']['texture_height'])
  path=A/'animations/boss_forms'/(id+'.animation.json');doc=json.loads(path.read_text());old=json.loads((D/'before'/(id+'.animation.json')).read_text())
  assert set(doc['animations'])==set(old['animations']);names={b['name'] for b in g['bones']}
  lows={}
  for clip,a in doc['animations'].items():
   assert {k:x for k,x in a.items() if k!='bones'}=={k:x for k,x in old['animations'][clip].items() if k!='bones'}
   for bn,ch in a['bones'].items():
    assert bn in names
    for channel,track in ch.items():
     track={'0':track} if isinstance(track,list) else track
     assert min(map(float,track))>=0 and max(map(float,track))<=a['animation_length']+.00001
     assert all(len(x)==3 and np.isfinite(x).all() for x in track.values())
     if a.get('loop'):
      delta=v.r.sample(track,a['animation_length'])-v.r.sample(track,0)
      if channel=='rotation':delta=(delta+180)%360-180
      assert np.max(np.abs(delta))<.001
   if id in TARGETS:
    lows[clip]=round(min(float(np.concatenate([q[0] for q in v.r.geometry(id,clip=clip,tick=float(t*20))])[:,1].min()) for t in np.linspace(0,a['animation_length'],33)),3)
   else:assert doc==old,(id,'non-target animation changed')
  assert all(y>=-.12 for y in lows.values()),(id,'ground penetration',lows)
  if id not in TARGETS+['hammer_chain']:assert im.tobytes()==Image.open(D/'before'/(id+'.png')).tobytes()
  report[id]={'geometryUVRigUnchanged':True,'clipNamesAndDurationsUnchanged':True,'sampledMinY':lows,'pngSha256':hashlib.sha256((A/'textures/entity/boss_forms'/(id+'.png')).read_bytes()).hexdigest()}
 (D/'offline-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS: original geometry/UV/rig, clip clocks, loop seams, and untouched non-target peers. Floor samples:',{i:report[i]['sampledMinY'] for i in TARGETS},flush=True)

def review():
 v.D=D
 for id in TARGETS:
  i=IDS.index(id);out=D/id;tex=np.array(Image.open(A/'textures/entity/boss_forms'/(id+'.png')));oldtex=np.array(Image.open(D/'before'/(id+'.png')))
  pre='' if i<3 else 'animation.'+id+'.';idle=pre+'idle'
  q=v.r.geometry(id,clip=idle,tick=0);oldq=v.r.geometry(id,clip=idle,tick=0,geo_path=D/'before'/(id+'.geo.json'),animation_path=D/'before'/(id+'.animation.json'))
  samples=[v.r.geometry(id,clip=pre+c,tick=t) for c,t in SAMPLES[id]]
  frame=np.concatenate([a[0] for s in samples+[q,oldq] for a in s]);check=v.checker(id)
  for angle,name in [(45,'uv-direction'),(90,'uv-direction-side')]:
   v.labelled(v.raster(q,check,yaw=angle,frame_points=frame),NAMES[i]+' / 编号及方向检查 · 仅预览').save(out/(name+'.png'))
  for name,angle in [('front',0),('side',90),('back',180),('three-quarter',45)]:
   for mode in ('unlit','lit','gray'):
    v.labelled(v.raster(q,tex,yaw=angle,mode=mode,frame_points=frame),NAMES[i]+' / '+name+' / '+mode).save(out/(name+'-'+mode+'.png'))
  for mode in ('unlit','lit','gray'):
   ims=[v.labelled(v.raster(qq,tt,size=(900,680),mode=mode,frame_points=frame),label) for qq,tt,label in [(oldq,oldtex,LABELS[0]),(q,tex,LABELS[1])]]
   combined=Image.new('RGB',(1800,760));combined.paste(ims[0],(0,0));combined.paste(ims[1],(900,0));combined.save(out/('comparison-'+mode+'.png'))
  sheet=Image.new('RGB',(1600,1260),(232,233,228))
  for k,((clip,t),qq) in enumerate(zip(SAMPLES[id],samples)):
   state=['待机','警戒 / 已有动作','接触 / 既有时间点','恢复'][k]
   if clip=='idle' and k==1:state='独立观察 / 待机循环'
   im=v.labelled(v.raster(qq,tex,mode='lit',size=(800,550),frame_points=frame),NAMES[i]+f' / {state} / {clip} · {t}t')
   im.save(out/f'state-{k}.png');sheet.paste(im,(k%2*800,k//2*630))
  sheet.save(out/'states.png')
  attack=ATTACKS[id];a=json.loads((A/'animations/boss_forms'/(id+'.animation.json')).read_text())['animations'][pre+attack];frames=[]
  # Fixed camera/framing across the complete attack, no per-frame autozoom.
  clipqs=[v.r.geometry(id,clip=pre+attack,tick=float(t*20)) for t in np.linspace(0,a['animation_length'],40)]
  aframe=np.concatenate([x[0] for qs in clipqs for x in qs])
  for k,qq in enumerate(clipqs):frames.append(v.labelled(v.raster(qq,tex,size=(800,600),mode='lit',frame_points=aframe),NAMES[i]+f' / {attack} · {k*a["animation_length"]*20/39:.1f} tick'))
  frames[0].save(out/'action.webp',save_all=True,append_images=frames[1:],duration=round(a['animation_length']*1000/40),loop=0,lossless=True)
  refs=v.references(np.array([-72,0,-4]));scene=q+refs
  v.labelled(v.raster(scene,tex,mode='lit',size=(1200,820)),NAMES[i]+' / 1.8m玩家、1m石砖与木材 / 软件基础光照').save(out/'scene.png')
  for distance in (10,18,28):v.labelled(v.raster(scene,tex,mode='lit',distance=distance,size=(1200,820)),NAMES[i]+f' / 玩家视高 / 距离 {distance}m / 软件透视').save(out/f'distance-{distance}m.png')
  print('Rendered',id,flush=True)
 if True:
  sheet=Image.new('RGB',(1800,900),(232,233,228))
  for j,id in enumerate(IDS):
   pre='' if j<3 else 'animation.'+id+'.';tex=np.array(Image.open(A/'textures/entity/boss_forms'/(id+'.png')))
   im=v.labelled(v.raster(v.r.geometry(id,clip=pre+'idle',tick=0),tex,mode='gray',size=(450,370)),NAMES[j]);sheet.paste(im,(j%4*450,j//4*450))
  sheet.save(D/'eight-hierarchy-check.png')

if __name__=='__main__':
 if '--review-only' not in sys.argv:export();validate()
 if '--export-only' not in sys.argv:review()
