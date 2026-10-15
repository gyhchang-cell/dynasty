"""Scope lock, UV separation, animated bounds and deterministic export checks."""
from export import *
import zipfile,runpy
sys.path.insert(0,str(R/'tools/art/secondary-cuboid'))
from rig_bounds import vertices
def run():
 geo,tex,_,allowed=assemble();assert json.loads(TARGETS[0].read_text())==geo
 assert Image.open(TARGETS[2]).tobytes()==tex.tobytes()
 oldg=json.loads((D/'before'/TARGETS[0].name).read_text())['minecraft:geometry'][0]
 new=geo['minecraft:geometry'][0];assert new['description']==oldg['description']
 assert TARGETS[1].read_bytes()==(D/'before'/TARGETS[1].name).read_bytes()
 used=np.zeros((128,128),bool)
 for b in new['bones']:
  for c in b.get('cubes',[]):
   for u in c['uv'].values():
    x,y=u['uv'];w,h=u['uv_size'];assert min(x,y,w,h)>0 and x+w<128 and y+h<128
    assert not used[y:y+h,x:x+w].any(),'UV overlap';used[y:y+h,x:x+w]=True
 stats={}
 for n,a in json.loads(TARGETS[1].read_text())['animations'].items():
  points=np.array([vertices(new['bones'],a['bones'],float(t)) for t in np.linspace(0,a['animation_length'],121)])
  low=points.min(axis=(0,1));high=points.max(axis=(0,1));assert np.isfinite(points).all()
  assert low[1]>-.12,(n,'new geometry under floor',low)
  assert max(abs(low[0]),abs(high[0]),abs(low[2]),abs(high[2]))<72 and high[1]<80
  stats[n]={'sampledFrames':121,'minimumYModelUnits':float(low[1]),'minimum':low.tolist(),'maximum':high.tolist()}
 expected=hashes()
 for entry in ['tianjiang-helmet-v17/export.py','tianjiang-steve-v15/create.py','tianjiang-texture-v16/export.py']:
  # Each legacy command runs in a fresh process: module names cannot contaminate guards.
  import subprocess,os
  subprocess.run([sys.executable,str(R/'tools/art'/entry)],check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  assert hashes()==expected,entry+' restored old resources'
 report={'registeredId':'dynasty:'+ID,'bodyAndWeaponGeometryUnchanged':True,'allExistingUVUnchanged':True,'onlyExistingCrestReshaped':True,'newShallowHeadCubes':6,'skeletonAndAnimationUnchanged':True,'bodyAndWeaponPixelsUnchanged':True,'atlasSize':[128,128],'uniqueUVIslands':True,'allThreeExportEntrypointsDeterministic':True,'animatedBounds':stats,'sourceSHA256':hashes()}
 jar=R/'build/libs/dynasty-1.4.0.jar'
 with zipfile.ZipFile(jar) as z:
  for p in TARGETS:
   n=str(p.relative_to(R/'src/main/resources'));assert p.read_bytes()==z.read(n)==(R/'build/resources/main'/n).read_bytes()
 report['sourceProcessedAndJarParity']=True
 (D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':run()
