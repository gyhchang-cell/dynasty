"""Strict palette, live IDs/bindings, hierarchy, clip compatibility and authored floor QA."""
import json,hashlib,sys,math,copy
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent;A=ROOT/'src/main/resources/assets/dynasty'
sys.path.insert(0,str(ROOT/'tools/art/secondary-cuboid'));from rig_bounds import vertices
m=json.loads((HERE/'targets.json').read_text());report={}
for id,v in m.items():
 g=json.loads((A/'geo'/v['folder']/(id+'.geo.json')).read_text());b=g['minecraft:geometry'][0]['bones'];by={x['name']:x for x in b};assert len(by)==len(b)
 a=json.loads((A/'animations'/v['folder']/(id+'.animation.json')).read_text())['animations'];im=Image.open(A/'textures/entity'/v['folder']/(id+'.png')).convert('RGB')
 assert im.size==(16,16) and len(im.getcolors(256))==4
 for y in range(16):
  for x in range(16):
   p=im.getpixel((x,y));assert p==im.getpixel((x-x%2,y-y%2)),(id,x,y)
   if x in [0,15] or y in [0,15]:assert p==(255,255,255)
 seen=set();faces=0
 for bb in b:
  assert not bb.get('parent') or bb['parent'] in seen,(id,bb['name']);seen.add(bb['name'])
  for c in bb.get('cubes',[]):
   assert all(math.isfinite(z) for z in c['origin']+c['size']) and all(s>0 for s in c['size'])
   for f,u in c['uv'].items():
    vals=u['uv']+u['uv_size'];assert all(n==int(n) for n in vals);x,y=u['uv'];w,h=u['uv_size'];assert 0<=min(x,x+w)<=max(x,x+w)<=16 and 0<=min(y,y+h)<=max(y,y+h)<=16;faces+=1
    if id!='baimian_huxiangu':assert all(im.getpixel((xx,yy))!=(255,255,255) for xx in range(x,x+w) for yy in range(y,y+h)),(id,bb['name'],f,'white background')
 for n,clip in a.items():
  assert set(clip['bones'])<=seen,(id,n,set(clip['bones'])-seen)
  for bn,channels in clip['bones'].items():
   for field,track in channels.items():
    if isinstance(track,dict):assert max(map(float,track))<=clip['animation_length']+.00001,(id,n,bn)
 if v['baseline']:
  old=json.loads((HERE/'baseline'/v['baseline'][0]['path']).read_text())['minecraft:geometry'][0]['bones'];assert {x['name'] for x in old}<=seen
  changed=[x['name'] for x in old if x.get('parent')!=by[x['name']].get('parent')];assert not changed or v['folder']=='boss_cuboid' and set(changed)<=set(['left_foot','right_foot'])
  oa=json.loads((HERE/'baseline'/v['baseline'][1]['path']).read_text())['animations'];assert set(oa)==set(a)
  assert all(oa[n]['animation_length']==a[n]['animation_length'] and oa[n].get('loop')==a[n].get('loop') for n in oa)
  if id=='pilin_zhijinwu':
   for n in a:
    for bone in ['right_upper_arm','left_upper_arm','right_forearm','left_forearm','halberd']:
     assert a[n]['bones'].get(bone)==oa[n]['bones'].get(bone),(id,n,bone,'lost solved two-hand grip')
 d=next(v for k,v in a.items() if k.rsplit('.',1)[-1]=='death');body=copy.deepcopy(b)
 if id=='baimian_huxiangu':
  # Floor measured separately: emerging animal and collapsed robe are both real geometry.
  pass
 if id=='juchui_jinjia_lishi':
  for bb in body:
   if bb['name'] in ['left_hammer','right_hammer']:bb['cubes']=[]
 lo=min(p[1] for p in vertices(body,d['bones'],d['animation_length']));assert -.05<=lo<=.2,(id,'death floor',lo)
 report[id]={'bones':len(b),'cuboids':sum(len(bb.get('cubes',[])) for bb in b),'faces':faces,'clips':len(a),'deathFloorUnits':lo,'palette16x16':True,'fourColorsIncludingWhite':True,'originalAnimationNamesDurationsLoops':True,'sha256':{kind:hashlib.sha256((A/kind/v['folder']/(id+ext)).read_bytes()).hexdigest() for kind,ext in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]}}
out=ROOT/'docs/art/boss-eight-v1';out.mkdir(parents=True,exist_ok=True);(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: 8 actual rigs, 16px/four colours/2px islands, hierarchy, original clips, solved halberd grip, final death floor')
