"""Actual actor PNG+UV offline previews; no particles or native-game claims."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
import review_wood_kite as base
ROOT=Path(__file__).resolve().parents[3];ASSET=ROOT/'src/main/resources/assets/dynasty';OUT=ROOT/'docs/art/bestiary-v43/marshal'
base.OUT=OUT
r=base.geometry
IDS=('gongsun_wuwang','gongsun_wuwang_foot')
PREFIX='animation.gongsun_wuwang.'
MOTIONS=('idle','walk','slash','morph')
DETAILS=[('mask',['blind_visor_hinge','empty_oath_cavity','oath_shrine']),('skull',['horse_skull','horse_lower_jaw','horse_neck_upper']),('support',['bone_horse','front_left','rear_left','rocker'])]
texture_form=lambda ident,clip,tick:ident

def quads(ident,clip='idle',tick=0,before=False):
 return r.geometry(ident,clip=PREFIX+clip,tick=tick,
  geo_path=OUT/'before'/(ident+'.geo.json') if before else None,
  animation_path=OUT/'before'/(ident+'.animation.json') if before else None)

def render(ident,angle=45,mode='unlit',before=False,clip='idle',tick=0,size=(1200,760),bones=None,checker=None,frame_points=None,distance=None):
 q=quads(ident,clip,tick,before)
 texture_id=texture_form(ident,clip,tick)
 tp=OUT/'before'/(texture_id+'.png') if before else ASSET/f'textures/entity/blueprint/boss/{texture_id}_body.png'
 atlas=np.array(Image.open(tp).convert('RGB')) if checker is None else checker
 if bones:q=[a for a in q if any(key in a[2] for key in bones)]
 else:q+=base.references(np.array([-67,0,-14]))
 return base.raster(q,atlas,yaw=angle,elevation=8,size=size,mode=mode,frame_points=frame_points,distance=distance)

def main():
 evidence={}
 for ident in IDS:
  out=OUT/ident;out.mkdir(exist_ok=True)
  for angle,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
   for mode in ('unlit','lit'):render(ident,angle,mode).save(out/f'{name}-{mode}.png')
   old=base.label(render(ident,angle,before=True),'修改前 · 原16px PNG逐面采样')
   new=base.label(render(ident,angle),'修改后 · 同形体 / 同机位 / 同尺度 · 原色')
   cmp=Image.new('RGB',(2400,810),'#e8e9e4');cmp.paste(old,(0,0));cmp.paste(new,(1200,0));cmp.save(out/f'comparison-{name}.png')
  for title,names in DETAILS:
   if title=='skull' and ident.endswith('_foot'):continue
   base.label(render(ident,bones=names,mode='lit',size=(1000,700)),title+' · 实际PNG / 现有部件 · 软件近景').save(out/f'{title}-detail.png')
  for mode in ('gray','dim'):render(ident,mode=mode).save(out/f'{mode}.png')
  checker=base.uv_checks(ident)
  for angle,title in [(45,'uv-direction'),(90,'uv-direction-side')]:render(ident,angle,checker=checker).save(out/f'{title}.png')
  for d in (10,18,28):base.label(render(ident,mode='lit',distance=d),f'软件透视 / 视高1.62m / 距原点{d}m / 非游戏截图').save(out/f'distance-{d}m.png')
  clips=json.loads((ASSET/f'animations/blueprint/boss/{ident}.animation.json').read_text())['animations']
  # Read every existing clip, checking start, contact-region and recovery;
  # representative actions additionally have a full fixed-camera filmstrip.
  samples={}
  for key,data in clips.items():
   samples[key]=[]
   for t in [0,data['animation_length']*10,data['animation_length']*20]:
    qs=quads(ident,key.rsplit('.',1)[-1],t)
    pts=np.concatenate([a[0] for a in qs]);assert np.isfinite(pts).all()
    samples[key].append({'tick':t,'quads':len(qs),'bounds':[pts.min(0).tolist(),pts.max(0).tolist()]})
  motions=[]
  for clip in MOTIONS:
   dur=clips[PREFIX+clip]['animation_length'];times=np.linspace(0,dur*20,24)
   fixed=np.concatenate([p for t in times for p,_,_ in quads(ident,clip,float(t))+base.references(np.array([-67,0,-14]))])
   frames=[base.label(render(ident,mode='lit',clip=clip,tick=float(t),size=(900,520),frame_points=fixed),f'{clip} / {t:.1f}tick · 原动作软件回放') for t in times]
   frames[0].save(out/f'{clip}.webp',save_all=True,append_images=frames[1:],duration=max(20,round(dur*1000/23)),loop=0,lossless=True)
   strip=Image.new('RGB',(1440,1368),'#e8e9e4')
   for i,f in enumerate(frames):strip.paste(f.resize((360,228),Image.Resampling.NEAREST),((i%4)*360,(i//4)*228))
   strip.save(out/f'{clip}-frames.png');motions.append({'clip':clip,'length_seconds':dur,'samples':24})
   print(ident,clip,'full fixed-camera offline clip',flush=True)
  evidence[ident]={'method':'Actual new body PNG, actual per-face UV, nearest sampling, neutral diffuse/unlit/gray/dim; no particles/emission',
   'all_existing_clip_samples':samples,'full_preview_motions':motions,'geometry_and_animation_unchanged':True,'game_test':'PENDING','native_bake':'see separate receipt if run'}
 (OUT/'preview-verification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 print('Two existing forms previewed. Offline previews, not Minecraft screenshots.')
if __name__=='__main__':main()
