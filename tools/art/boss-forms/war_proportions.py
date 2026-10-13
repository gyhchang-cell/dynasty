"""User-approved v7 upper-body and v8 foot correction on the original war-spirit rig.
No extra parts or bones; main blade dimensions and UV remain unchanged.
"""
import copy,math
BODY_SCALE=1.24
LEAN=12

def refine(bones):
 by={b['name']:b for b in bones};old=copy.deepcopy(by);anchor=[0,21,2]
 def frame(v):return [anchor[k]+(v[k]-anchor[k])*BODY_SCALE for k in range(3)]
 def part(name,new_pivot,scale):
  b=by[name];o=old[name];pivot=o['pivot']
  def point(v):return [round(new_pivot[k]+(v[k]-pivot[k])*scale,6) for k in range(3)]
  b['pivot']=list(new_pivot)
  for c,src in zip(b['cubes'],o['cubes']):
   c['origin']=point(src['origin']);c['size']=[round(v*scale,6) for v in src['size']]
   if 'pivot' in src:c['pivot']=point(src['pivot'])
 part('war_frame',anchor,BODY_SCALE);by['war_frame']['rotation']=[LEAN,0,0]
 for n in ['war_core','war_banner']:part(n,frame(old[n]['pivot']),BODY_SCALE)
 part('old_blades',frame(old['old_blades']['pivot']),1.20)
 head=frame(old['broken_helm']['pivot']);head[1]+=1;head[2]-=4
 part('broken_helm',head,1.30)
 part('breach_arm',frame(old['breach_arm']['pivot']),1.08)
 arm=frame(old['weapon_arm']['pivot']);part('weapon_arm',arm,1.12)
 grip=[arm[k]+(old['right_grip']['pivot'][k]-old['weapon_arm']['pivot'][k])*1.12 for k in range(3)]
 part('right_grip',grip,1.08);part('war_glaive',grip,1.0)
 def box(c,center,size):
  c['size']=list(size);c['origin']=[center[k]-size[k]/2 for k in range(3)]
 def beam(c,a,b,width):
  v=[b[k]-a[k] for k in range(3)];length=math.sqrt(sum(x*x for x in v));center=[(a[k]+b[k])/2 for k in range(3)]
  box(c,center,[width,length,width]);c['pivot']=center;c['rotation']=[-math.degrees(math.asin(v[2]/length)),0,math.degrees(math.atan2(v[0],v[1]))]
 for side in [-1,1]:
  cs=by['support_'+str(side)]['cubes']
  beam(cs[0],[side*12,25,4],[side*17,13,8],9)
  box(cs[1],[side*17,13,7],[11,9,10])
  beam(cs[2],[side*17,12,6],[side*17,4.5,0],6.5)
  box(cs[3],[side*17,1.5,-1],[10,3,11])
 return bones
