"""Bake grounded keyframes into actual JSON, without runtime bone overrides.
Two-hinge leg IK keeps feet on the floor while the mechanical body settles.
Grounding works per connected subtree; loose supports never move away from a joint.
"""
import json,math,copy
import numpy as np
from review import r,A,D
from animate import PRIMARY

def matrices(bones,channels,t):
 by={b['name']:b for b in bones};world={}
 for b in bones:
  n=b['name'];ch=channels.get(n,{});p=np.array(b['pivot'],float);relative=p-(np.array(by[b['parent']]['pivot']) if b.get('parent') else 0)
  if 'position' in ch:relative+=r.sample(ch['position'],t)
  rotation=np.array(b.get('rotation',[0,0,0]),float)+(r.sample(ch['rotation'],t) if 'rotation' in ch else 0)
  m=(world[b['parent']] if b.get('parent') else np.eye(4))@r.transform(relative,rotation,r.sample(ch['scale'],t) if 'scale' in ch else [1,1,1]);world[n]=m
 return world

def apply():
 models=json.loads((D/'forms.json').read_text())
 for i,m in enumerate(models):
  id=m['id'];path=A/'animations/boss_forms'/f'{id}.animation.json';animations=json.loads(path.read_text());geo=json.loads((A/'geo/boss_forms'/f'{id}.geo.json').read_text())['minecraft:geometry'][0];bones=geo['bones'];by={b['name']:b for b in bones};prefix='' if i<3 else 'animation.'+id+'.'
  # Bake stance compensation, preserving segment lengths and fixed foot contact.
  if i in [4,5,6]:
   clips=['hurt']+(['death'] if i==4 else ['charge'] if i==5 else [])
   for clip in clips:
    a=animations['animations'][prefix+clip];period=a['animation_length'];original=copy.deepcopy(a['bones']);axis=0 if i==4 else 2;rotationaxis=2 if i==4 else 0
    for n in m['gait']:
     lower=n.replace('outrigger_','link_') if i==4 else n.replace('front_','front_paw_').replace('rear_','rear_paw_');sole=lower+'_sole';target=np.array(by[sole]['pivot'],float)*[-1,1,1]
     # Let the frame's legs spread as it crumples; each foot is still supported.
     times=sorted(set([round(float(t),6) for t in np.linspace(0,period,33)]+[float(t) for ch in original.values() for v in ch.values() if isinstance(v,dict) for t in v]))
     track=[{}, {}, {}];last=np.zeros(2)
     for t in times:
      ch=copy.deepcopy(original);wanted=target.copy()
      if clip=='death':wanted[0]+=np.sign(wanted[0])*14*min(1,t/period)
      def point(q):
       ch.setdefault(n,{})['rotation']=[q[0] if d==rotationaxis else 0 for d in range(3)]
       ch.setdefault(lower,{})['rotation']=[q[1] if d==rotationaxis else 0 for d in range(3)]
       return matrices(bones,ch,t)[sole][:3,3][[axis,1]]
      q=last.copy()
      for iteration in range(35):
       val=point(q);err=wanted[[axis,1]]-val
       if np.linalg.norm(err)<.001:break
       jac=np.column_stack([(point(q+np.eye(2)[j]*.05)-val)/.05 for j in range(2)])
       delta=np.linalg.lstsq(jac,err,rcond=None)[0];q+=np.clip(delta,-10,10)
      last=q.copy();point(q);mat=matrices(bones,ch,t)[lower][:3,:3]
      angle=math.degrees(math.atan2(mat[1,0],mat[0,0])) if rotationaxis==2 else -math.degrees(math.atan2(mat[2,1],mat[1,1]))
      for k,v in enumerate([q[0],q[1],-angle]):track[k][str(t)]=[round(float(v),5) if d==rotationaxis else 0 for d in range(3)]
     for bn,trk in zip([n,lower,sole],track):a['bones'].setdefault(bn,{})['rotation']=trk
  path.write_text(json.dumps(animations,indent=2)+'\n')
  # Ground the body or an arm subtree; never scale geometry to conceal penetration.
  for clip,a in animations['animations'].items():
   name=clip.split('.')[-1]
   targets=[]
   if name=='death':targets=[('root' if i in [0,2,5,6] else PRIMARY[i])]
   elif i==4 and name=='hurt':targets=[PRIMARY[i]]
   elif i==3 and name=='walk':targets=m['gait']
   elif i==7 and name in ['walk','hurt','throw']:targets=['hammer_yoke_-1','hammer_yoke_1']
   for target in targets:
    desc={target}
    for b in bones:
     if b.get('parent') in desc:desc.add(b['name'])
    channel=a['bones'].setdefault(target,{});existing=copy.deepcopy(channel.get('position',[0,0,0]));times=sorted(set([round(float(t),6) for t in np.linspace(0,a['animation_length'],65)]+[float(t) for ch in a['bones'].values() for v in ch.values() if isinstance(v,dict) for t in v]))
    sequence={}
    for t in times:
     points=[v for v,_,b in r.geometry(id,clip=clip,tick=t*20) if b in desc]
     if not points:continue
     bottom=float(np.concatenate(points)[:,1].min());correction=(.03-bottom) if name=='death' and target=='root' else max(0,-bottom)+(.03 if bottom<0 else 0)
     # Parent local Y may tilt. Apply its inverse to a world-space lift.
     parent=by[target].get('parent');mat=matrices(bones,a['bones'],t)[parent] if parent else np.eye(4)
     local=np.linalg.solve(mat[:3,:3],np.array([0,correction,0]))*[-1,1,1]
     sequence[str(t)]=[round(float(v),5) for v in r.sample(existing,t)+local]
    if any(abs(v[1])>.0001 for v in sequence.values()) or 'position' in channel:channel['position']=sequence
  path.write_text(json.dumps(animations,indent=2)+'\n')
 print('Grounded exported animations; no Java invoked.')
if __name__=='__main__':apply()
