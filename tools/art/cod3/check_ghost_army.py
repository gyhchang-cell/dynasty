from pathlib import Path
import sys,json,math,hashlib,base64,itertools
import numpy as np
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).parent));import scenic_ghost_army as src;import review_ghost_army as view
A=src.A;D=src.D;N=src.NAME

def obb(q):
 p=np.concatenate([a[0] for a in q]);v=q[0][0];x=v[1]-v[0];y=v[3]-v[0];axes=np.array([x/np.linalg.norm(x),y/np.linalg.norm(y),np.cross(x,y)/np.linalg.norm(np.cross(x,y))]);return p,axes

def touches(a,b):
 p,aa=a;q,bb=b
 if np.any(p.max(0)<q.min(0)-1e-5) or np.any(q.max(0)<p.min(0)-1e-5):return False
 for x in list(aa)+list(bb)+[np.cross(x,y) for x in aa for y in bb]:
  if np.linalg.norm(x)<1e-8:continue
  u=p@x;v=q@x
  if u.max()<v.min()-1e-5 or v.max()<u.min()-1e-5:return False
 return True

def check():
 checks=[];allbounds=[];fail=[];maxgrounderr=0;maxslip=0;motion=[]
 for lod in ('','_medium','_far'):
  g=json.loads((A/f'geo/scenic/{N}{lod}.geo.json').read_text())['minecraft:geometry'][0]
  bones=g['bones'];names={b['name'] for b in bones};assert len(names)==len(bones)
  assert all(not b.get('parent') or b['parent'] in names for b in bones)
  labels=[p['label'] for b in bones for p in src.design()[1] if p['bone']==b['name'] and p['lod']>=({'':0,'_medium':1,'_far':2}[lod])]
  dis=[];gripfail=[];penetration=[];legcollide=[];mins=[];foottrack=[]
  for tick in range(81):
   quads=view.pose(tick,lod);points=np.concatenate([p for p,_,_ in quads]);assert np.isfinite(points).all();allbounds.append([points.min(0),points.max(0)])
   boxes=[obb(quads[i:i+6]) for i in range(0,len(quads),6)];assert len(boxes)==len(labels)
   seen={0};todo=[0]
   while todo:
    i=todo.pop()
    for j in range(len(boxes)):
     if j not in seen and touches(boxes[i],boxes[j]):seen.add(j);todo.append(j)
   if len(seen)!=len(boxes):dis.append({'tick':tick,'parts':[labels[j] for j in range(len(boxes)) if j not in seen]})
   shaft=boxes[labels.index('spear_shaft')]
   for n in ('right_palm','right_fingers','right_thumb','right_knuckles'):
    if not touches(boxes[labels.index(n)],shaft):gripfail.append([tick,n])
   for n in ('cuirass_body','hip_undercoat','right_upper_leg','left_upper_leg','head_mass','left_hand_palm'):
    if touches(boxes[labels.index(n)],shaft):penetration.append([tick,n])
   rf=boxes[labels.index('right_foot')][0];lf=boxes[labels.index('left_foot')][0]
   if touches(boxes[labels.index('right_foot')],boxes[labels.index('left_foot')]):legcollide.append(tick)
   y=min(rf[:,1].min(),lf[:,1].min());maxgrounderr=max(maxgrounderr,abs(y));mins.append(y)
   if y<-.025 or y>.025:fail.append([lod,tick,'feet_y',float(y)])
   ft=[]
   for foot in (rf,lf):ft.append({'y_min':float(foot[:,1].min()),'y_spread':float(np.ptp(foot[foot[:,1]<foot[:,1].min()+.1,1])),'z_world':float(foot[:,2].mean()+tick*.16)})
   foottrack.append(ft)
  for i in range(1,len(foottrack)):
   for j,off in enumerate((0,.5)):
    q0=((i-1)/80+off)%1;q1=(i/80+off)%1
    if q0<.59 and q1<.59 and q1>=q0:maxslip=max(maxslip,abs(foottrack[i][j]['z_world']-foottrack[i-1][j]['z_world']))
  seam=float(np.max(np.abs(np.concatenate([q[0] for q in view.pose(0,lod)])-np.concatenate([q[0] for q in view.pose(80,lod)]))))
  checks.append({'lod':lod or 'full','cubes':len(labels),'poses':81,'disconnected':dis,'grip_failures':gripfail,'shaft_body_intersections':penetration,'feet_intersections':legcollide,'loop_seam_error_units':seam,'foot_y_min':float(min(mins))})
  if dis or gripfail or penetration or legcollide or seam>1e-5:fail.append(lod+' contacts or seam')
  if lod=='':motion=foottrack
 hand=json.loads((D/'draft-uv.json').read_text());occ=np.zeros((src.SIDE,src.SIDE),bool)
 for r in hand['islands']:
  x,y,w,h=r['rect'];assert min(x,y,w,h)>0 and x+w<src.SIDE and y+h<src.SIDE;assert not occ[y:y+h,x:x+w].any();occ[y:y+h,x:x+w]=True
 bb=json.loads((D/f'blockbench/{N}.bbmodel').read_text());assert len(bb['elements'])==checks[0]['cubes'];assert (bb['resolution']['width'],bb['resolution']['height'])==(256,256)
 lo=np.min([b[0] for b in allbounds],axis=0);hi=np.max([b[1] for b in allbounds],axis=0)
 result={'status':'PASS' if not fail else 'FAIL','software_only':True,'lod_checks':checks,'uv_overlap':False,'uv_islands':len(hand['islands']),'max_ground_plane_error_units':maxgrounderr,'max_stance_foot_slip_per_tick_units':maxslip,'world_speed_m_per_sec':.2,'cycle_displacement_m':.8,'cycle_seconds':4,'animated_bounds_units':[lo.tolist(),hi.tolist()],'java_started':False,'native_validation':'pending; JSON and software geometry checks do not prove native load','issues':fail}
 src.dump(D/'validation.json',result);src.dump(D/'foot-contact-samples.json',{'tick_rate':20,'speed_units_per_tick':.16,'frames':motion})
 print(result['status'],'grounderr',maxgrounderr,'slip',maxslip,'fail',str(fail)[:500],flush=True)
 print([(c['lod'],len(c['disconnected']),len(c['grip_failures']),len(c['shaft_body_intersections'])) for c in checks],flush=True)
if __name__=='__main__':check()
