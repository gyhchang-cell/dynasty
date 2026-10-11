"""Existing-bone posing only. Clip names, durations and server contact times stay fixed."""
import math

def track(a,bone,channel,keys):
 a['bones'].setdefault(bone,{})[channel]={str(t):v for t,v in keys}

def rotate(a,bone,keys):track(a,bone,'rotation',keys)

def refine(animations,id):
 for name,a in animations.items():
  clip=name.split('.')[-1];end=a['animation_length']
  if id=='undead_first_emperor':
   if clip in ('idle','walk'):
    for s in (-1,1):
     rotate(a,'lid_'+str(s),[(0,[0,s*17,0]),(end/2,[0,s*22,0]),(end,[0,s*17,0])])
    rotate(a,'imperial_mask',[(0,[-4,0,0]),(end*.4,[-4,-5,0]),(end*.65,[-4,4,0]),(end,[-4,0,0])])
    rotate(a,'dragon_skull',[(0,[4,-5,0]),(end/2,[0,5,0]),(end,[4,-5,0])])
    rotate(a,'dragon_jaw',[(0,[7,0,0]),(end/2,[11,0,0]),(end,[7,0,0])])
   elif clip=='attack':
    # The current vanilla melee goal applies damage at swing start. No fictitious
    # wind-up here; this is contact -> recoil -> recovery, with the existing .9s clip.
    rotate(a,'dragon_skull',[(0,[18,0,0]),(.12,[10,0,0]),(.35,[-8,0,0]),(end,[4,-5,0])])
    rotate(a,'dragon_jaw',[(0,[3,0,0]),(.12,[7,0,0]),(.35,[25,0,0]),(end,[7,0,0])])
    for s in (-1,1):rotate(a,'lid_'+str(s),[(0,[0,s*32,0]),(.2,[0,s*40,0]),(end,[0,s*17,0])])
  elif id=='pilin_zhijinwu':
   if clip=='idle':
    rotate(a,'beast_neck',[(0,[6,0,0]),(1.2,[5,-4,0]),(2.8,[7,3,0]),(4,[6,0,0])])
    rotate(a,'beast_mask',[(0,[-2,0,0]),(1.2,[-2,-2,0]),(2.8,[-2,1,0]),(4,[-2,0,0])])
   elif clip=='sweep':
    # The blade's forward crossing is at tick 20, the original server hit.
    rotate(a,'beast_neck',[(0,[6,0,0]),(.75,[10,-12,0]),(1,[8,0,0]),(1.15,[6,16,0]),(end,[6,0,0])])
  elif id=='juchui_jinjia_lishi':
   # The authored observation head is buried in the top shell at bind pose.
   # Its existing slide bone extends 6/16 block, while its rear stays in the shell.
   # This is a bone position track, not a new part or a new collision volume.
   track(a,'inset_face','position',[(0,[0,0,-6]),(end,[0,0,-6])])
   if clip=='idle':
    rotate(a,'inset_face',[(0,[0,-3,0]),(1.5,[0,3,0]),(3,[0,1,0]),(4,[0,-3,0])])
    rotate(a,'hammer_yoke_-1',[(0,[-5,0,-2]),(2,[-6,0,-2]),(4,[-5,0,-2])])
   elif clip=='slam':
    for s in (-1,1):
     rotate(a,'hammer_piston_'+str(s),[(0,[0,0,0]),(.7,[8,0,0]),(1.22,[14,0,0]),(1.4,[0,0,0]),(1.52,[4,0,0]),(2.2,[0,0,0]),(2.3,[2,0,0]),(3,[0,0,0]),(3.1,[1,0,0]),(end,[0,0,0])])
    # Pressure settles on the existing 28/44/60 tick ring pulses, with no extra hit.
    track(a,'inset_face','position',[(0,[0,0,-6]),(1.22,[0,0,-7]),(1.4,[0,0,-6]),(2.2,[0,0,-6.5]),(2.3,[0,0,-6]),(3,[0,0,-6.4]),(end,[0,0,-6])])
 return animations
