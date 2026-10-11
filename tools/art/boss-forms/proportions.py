"""Authoritative v7 export: rebalance approved war-spirit parts, preserve v6 painting."""
import json,copy,runpy,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from build import R,A
from war_proportions import refine
import texture_review as v
D=R/'docs/art/boss-proportions-v7';ID='rebel_general';B=D/'before'

def export():
 gp=A/'geo/boss_forms'/(ID+'.geo.json');ap=A/'animations/boss_forms'/(ID+'.animation.json')
 geo=json.loads((B/gp.name).read_text());refine(geo['minecraft:geometry'][0]['bones']);gp.write_text(json.dumps(geo,indent=2)+'\n')
 anim=json.loads((B/ap.name).read_text());track=anim['animations']['death']['bones']['root'].pop('position');ap.write_text(json.dumps(anim,indent=2)+'\n')
 # Re-sample only the existing death floor compensation after the changed foot/body extents.
 lift={}
 for key in track:
  q=v.r.geometry(ID,clip='death',tick=float(key)*20);low=np.concatenate([x[0] for x in q])[:,1].min();lift[key]=[0,round(float(.03-low),5),0]
 anim['animations']['death']['bones']['root']['position']=lift;ap.write_text(json.dumps(anim,indent=2)+'\n')
 # Paint at the approved v6 UV metric, then retain the exact same islands on new parts.
 from retexture import run
 run([ID],D,paint_geometry={ID:json.loads((B/gp.name).read_text())})
 runpy.run_path(str(R/'tools/art/boss-forms/export_bbmodel.py'),run_name='__main__')

def validate():
 gp=A/'geo/boss_forms'/(ID+'.geo.json');ap=A/'animations/boss_forms'/(ID+'.animation.json');tp=A/'textures/entity/boss_forms'/(ID+'.png')
 old=json.loads((B/gp.name).read_text())['minecraft:geometry'][0];new=json.loads(gp.read_text())['minecraft:geometry'][0]
 assert [(b['name'],b.get('parent'),len(b['cubes'])) for b in new['bones']]==[(b['name'],b.get('parent'),len(b['cubes'])) for b in old['bones']]
 for a,b in zip(old['bones'],new['bones']):
  assert [c['uv'] for c in a['cubes']]==[c['uv'] for c in b['cubes']]
  if a['name']=='war_glaive':
   for x,y in zip(a['cubes'],b['cubes']):
    assert x['size']==y['size'] and x.get('rotation')==y.get('rotation')
    assert np.allclose(np.array(x['origin'])-a['pivot'],np.array(y['origin'])-b['pivot'])
 assert tp.read_bytes()==(B/tp.name).read_bytes()
 original=json.loads((B/ap.name).read_text());current=json.loads(ap.read_text());t=current['animations']['death']['bones']['root']['position'];ot=original['animations']['death']['bones']['root']['position']
 assert set(t)==set(ot);current['animations']['death']['bones']['root']['position']=ot;assert original==current
 lows={};bounds={}
 for clip,a in original['animations'].items():
  points=[np.concatenate([x[0] for x in v.r.geometry(ID,clip=clip,tick=float(t))]) for t in np.linspace(0,a['animation_length']*20,65)]
  lows[clip]=round(float(min(q[:,1].min() for q in points)),4);assert lows[clip]>=-.12,(clip,lows[clip])
  for q in points:assert np.isfinite(q).all()
  if clip=='idle':bounds={'min':points[0].min(0).tolist(),'max':points[0].max(0).tolist()}
 report={'rigHierarchyAndCubeCountUnchanged':True,'bladeShapeDimensionsUVAndTextureUnchanged':True,'pngAndUVUnchanged':True,'animationChange':'only existing death root-position values regrounded; keys and all other tracks unchanged','floorSamples':lows,'idleBoundsInModelUnits':bounds,'upperFrameScale':1.24,'headScale':1.3,'frameForwardLeanDegrees':12,'feetBefore':[17,6,22],'feetAfter':[12,5,16]}
 (D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',report,flush=True)

if __name__=='__main__':export();validate()
