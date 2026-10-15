"""Focused checks for canonical body proportions, UV packing and existing timing."""
from create import *
def main():
 report={}
 for id in IDS:
  geo=json.loads((A/'geo/boss_cuboid'/f'{id}.geo.json').read_text())['minecraft:geometry'][0];by={b['name']:b for b in geo['bones']};tex=Image.open(A/'textures/entity/boss_cuboid'/f'{id}.png');occ=np.zeros(tex.size[::-1],bool)
  canonical={'head':[8,8,8],'chest':[8,12,4],'right_arm':[4,12,4],'left_arm':[4,12,4],'right_leg':[4,12,4],'left_leg':[4,12,4]}
  before=json.loads((D/'before'/f'{id}.geo.json').read_text())['minecraft:geometry'][0]
  prior={b['name']:b for b in before['bones']}
  assert set(prior)==set(by),'No new skeleton'
  def structure(c):return {k:v for k,v in c.items() if k!='uv'}
  for n,b in by.items():
   assert {k:v for k,v in b.items() if k!='cubes'}=={k:v for k,v in prior[n].items() if k!='cubes'},n
  for n in canonical:assert structure(by[n]['cubes'][0])==structure(prior[n]['cubes'][0]),n
  for n in ('weapon','seal','mantle'):
   if n in by:assert [structure(c) for c in by[n]['cubes']]==[structure(c) for c in prior[n]['cubes']],n
  for name,size in canonical.items():assert np.allclose(by[name]['cubes'][0]['size'],np.array(size)*S),name
  assert 'foot' not in ' '.join(by)
  for b in by.values():
   if 'parent' in b:assert b['parent'] in by
   for c in b.get('cubes',[]):
    for f,u in c['uv'].items():
     x,y=u['uv'];w,h=u['uv_size'];assert min(x,y)>=0 and w>0 and h>0 and x+w<=tex.width and y+h<=tex.height
     assert not occ[y:y+h,x:x+w].any(),'UV overlap';occ[y:y+h,x:x+w]=True
  assert by['weapon']['parent']=='right_grip' and by['weapon']['pivot']==by['right_grip']['pivot']
  old=json.loads((D/'before'/f'{id}.animation.json').read_text())['animations'];new=json.loads((A/'animations/boss_cuboid'/f'{id}.animation.json').read_text())['animations']
  assert set(old)==set(new)
  assert old==new,'Animation data must remain byte-equivalent after JSON decoding'
  grounding={}
  for name,a in new.items():
   assert a['animation_length']==old[name]['animation_length']
   assert set(a['bones'])<=set(by)
   support=[b for b in geo['bones'] if b['name'] not in ('weapon','seal')]
   lows=[min(v[1] for v in base.vertices(support,a['bones'],float(t))) for t in np.linspace(0,a['animation_length'],121)]
   assert min(lows)>-.02 and max(lows)<.05,(id,name,min(lows),max(lows))
   grounding[name]=[round(min(lows),4),round(max(lows),4)]
  report[id]={'sixCanonicalSteveBlocks':True,'uniformScale':S,'atlas':tex.size,'UVNoOverlap':True,'animationDurationsUnchanged':True,'supportGroundingModelUnits':grounding,'weaponParent':'right_grip'}
 # The accepted general, including V22 glyphs, is not being re-authored.
 import subprocess
 locked=[]
 for p in [A/'geo/boss_cuboid/nine_heaven_general.geo.json',A/'animations/boss_cuboid/nine_heaven_general.animation.json',A/'textures/entity/boss_cuboid/nine_heaven_general.png',R/'src/main/java/com/dynasty/client/TianjiangRuneField.java',R/'src/main/java/com/dynasty/client/TianjiangAura.java']:
  rel=str(p.relative_to(R));assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=R);locked.append(rel)
 report['approvedGeneralUnchanged']=locked
 (D/'asset-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Canonical body, UV, grip, grounding, timing and accepted Tianjiang locks passed.')
if __name__=='__main__':main()
