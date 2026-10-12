"""Verify this requested shape, actual atlas, six clips and packaged asset parity."""
from create import *
import zipfile
g=json.loads(TARGETS[0].read_text())['minecraft:geometry'][0];by={b['name']:b for b in g['bones']};names=list(by)
expected={'head':[8,8,8],'chest':[8,12,4],'right_arm':[4,12,4],'left_arm':[4,12,4],'right_leg':[4,12,4],'left_leg':[4,12,4]}
for n,s in expected.items():assert np.allclose(by[n]['cubes'][0]['size'],np.array(s)*SCALE),(n,'Steve main body changed')
assert len(by)==len(g['bones']);assert sum(len(b['cubes']) for n,b in by.items() if n not in ['weapon'])==10
assert len(by['right_arm']['cubes'])==len(by['left_arm']['cubes'])==1,'Added bulky arms'
tex=Image.open(TARGETS[2]);assert tex.size==(g['description']['texture_width'],g['description']['texture_height'])==(128,128)
used=np.zeros(tex.size[::-1],dtype=bool);pixels={tuple(c) for c in np.array(tex).reshape(-1,3)};assert pixels.issubset(set(PAL.values()))
for n,b in by.items():
 if b.get('parent'):assert names.index(b['parent'])<names.index(n)
 for c in b['cubes']:
  assert np.isfinite(c['origin']+c['size']).all() and min(c['size'])>0
  assert set(c['uv'])==set(FACES)
  for f,u in c['uv'].items():
   x,y=u['uv'];w,h=u['uv_size'];assert min(x,y,w,h)>0 and x+w<tex.width and y+h<tex.height
   assert not used[y:y+h,x:x+w].any(),(n,f,'overlap');used[y:y+h,x:x+w]=True
an=json.loads(TARGETS[1].read_text())['animations'];old=json.loads((D/'before'/f'{ID}.animation.json').read_text())['animations'];assert list(an)==list(old)
report={'sixSteveCuboidsUnchanged':True,'uniformScale':SCALE,'bareBodyHeightBlocks':2*SCALE,'extraBodyCuboids':4,'weaponCuboids':len(by['weapon']['cubes']),'atlas':tex.size,'paletteColors':len(pixels),'clips':{}}
support=[b for b in g['bones'] if b['name']!='weapon']
for clip,a in an.items():
 assert a['animation_length']==old[clip]['animation_length'] and a['loop']==old[clip].get('loop',False)
 assert set(a['bones']).issubset(names)
 for channels in a['bones'].values():
  for track in channels.values():
   for val in (track.values() if isinstance(track,dict) else [track]):assert len(val)==3 and np.isfinite(val).all()
 ts=np.linspace(0,a['animation_length'],481)
 vs=[np.array(vertices(g['bones'],a['bones'],float(t))) for t in ts]
 floor=float(min(p[:,1].min() for p in vs));assert floor>-.04,(clip,'below floor',floor)
 span=np.concatenate(vs);desc=g['description'];half=desc['visible_bounds_width']*8
 assert np.abs(span[:,[0,2]]).max()<half,(clip,'weapon exceeds declared render bounds')
 assert span[:,1].max()<(desc['visible_bounds_offset'][1]+desc['visible_bounds_height']/2)*16
 if a['loop']:assert np.allclose(vs[0],vs[-1],atol=1e-4),(clip,'loop seam')
 body=np.array(vertices(support,a['bones'],0));report['clips'][clip]={'seconds':a['animation_length'],'minimumYBlocks':round(floor/16,6),'heightIncludingCrestBlocks':round(float(body[:,1].max())/16,3)}
assert list(an['attack']['bones']['right_arm']['rotation'])==['0','0.09','0.15','0.3'],'Six-tick attack contact changed'
assert hashes()==json.loads((D/'export-owner.json').read_text())
jar=R/'build/libs/dynasty-1.4.0.jar'
if jar.exists():
 with zipfile.ZipFile(jar) as z:
  for p in TARGETS:
   name=str(p.relative_to(R/'src/main/resources'));assert p.read_bytes()==z.read(name)==(R/'build/resources/main'/name).read_bytes()
 report['packagedAssetParity']=True
(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
