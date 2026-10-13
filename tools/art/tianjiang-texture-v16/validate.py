"""Targeted acceptance: texture-only scope, exact UV and export/load parity."""
from export import *
import numpy as np,zipfile
def run():
 baseline=json.loads((D/'before-hashes.json').read_text())
 for p in TARGETS[:2]:
  assert hashlib.sha256(p.read_bytes()).hexdigest()==baseline[str(p.relative_to(R))]
  assert p.read_bytes()==(D/'before'/p.name).read_bytes()
 before=Image.open(D/'before.png');im=Image.open(TARGETS[2])
 assert im.size==before.size==(128,128) and im.mode=='RGB'
 geo=json.loads(TARGETS[0].read_text())['minecraft:geometry'][0]
 assert (geo['description']['texture_width'],geo['description']['texture_height'])==im.size
 used=np.zeros((128,128),dtype=bool);coverage={}
 for b in geo['bones']:
  for c in b['cubes']:
   for f,uv in c['uv'].items():
    x,y=uv['uv'];w,h=uv['uv_size'];assert min(x,y,w,h)>0 and x+w<128 and y+h<128
    assert not used[y:y+h,x:x+w].any();used[y:y+h,x:x+w]=True
    tile=np.array(im)[y:y+h,x:x+w];cols={tuple(p) for p in tile.reshape(-1,3)}
    assert cols.issubset(set(PAL.values()))
    coverage.setdefault(b['name'],set()).update(cols)
 # Major metal/body/cloth faces must carry deliberate tonal levels, not a fill.
 for n in ['head','chest','right_arm','left_arm','weapon']:assert len(coverage[n])>=8,(n,'flat')
 export();assert hashes()==json.loads((D/'export-owner.json').read_text())
 fraction=float((np.array(before)[used]!=np.array(im)[used]).any(axis=1).mean())
 report={'registeredId':'dynasty:'+ID,'geometryByteIdentical':True,'skeletonAndAnimationByteIdentical':True,'allUVByteIdentical':True,'atlas':[128,128],'resolutionChanged':False,'productionPNGChanged':True,'changedActivePixelsFraction':round(fraction,4),'actualPaletteColors':len({tuple(x) for x in np.array(im)[used]}),'deterministicReexport':True,'perBoneColorCounts':{n:len(c) for n,c in coverage.items()},'sourceSHA256':hashes()}
 jar=R/'build/libs/dynasty-1.4.0.jar'
 if jar.exists():
  with zipfile.ZipFile(jar) as z:
   for p in TARGETS:
    n=str(p.relative_to(R/'src/main/resources'));assert p.read_bytes()==z.read(n)==(R/'build/resources/main'/n).read_bytes()
  report['packagedAssetParity']=True
 (D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':run()
