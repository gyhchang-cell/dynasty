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
  elif id=='eunuch_mastermind':
   if clip in ('idle','walk'):
    rotate(a,'mask',[(0,[-5,-7,3]),(end*.35,[-3,6,1]),(end*.7,[-6,2,-2]),(end,[-5,-7,3])])
    for s in (-1,1):
     rotate(a,'sleeve_'+str(s),[(0,[4,s*5,s*5]),(end/2,[8,s*7,s*8]),(end,[4,s*5,s*5])])
     rotate(a,'fingers_'+str(s),[(0,[-12,0,0]),(end/2,[-20,0,0]),(end,[-12,0,0])])
   elif clip=='attack':
    # Vanilla melee contact is at swing start; show contact, recoil and settling.
    rotate(a,'mask',[(0,[-9,0,0]),(.18,[-6,0,0]),(.42,[-2,5,2]),(end,[-5,-7,3])])
    track(a,'mask','position',[(0,[0,0,-5]),(.2,[0,0,-3]),(.5,[0,0,0]),(end,[0,0,0])])
    for s in (-1,1):
     rotate(a,'sleeve_'+str(s),[(0,[-24,s*9,s*28]),(.18,[-14,s*7,s*34]),(.5,[7,s*7,s*16]),(end,[4,s*5,s*5])])
     rotate(a,'fingers_'+str(s),[(0,[-38,0,0]),(.25,[-48,0,0]),(.6,[-18,0,0]),(end,[-12,0,0])])
    for k in range(7):rotate(a,'curtain_fan_'+str(k),[(0,[0,(k-3)*6,0]),(.3,[0,(k-3)*9,0]),(end,[0,0,0])])
  elif id=='rebel_general':
   if clip in ('idle','walk'):
    rotate(a,'broken_helm',[(0,[7,-6,0]),(end*.4,[5,4,0]),(end*.7,[6,0,0]),(end,[7,-6,0])])
    rotate(a,'weapon_arm',[(0,[-9,4,0]),(end/2,[-12,3,0]),(end,[-9,4,0])])
    if clip=='idle':rotate(a,'breach_arm',[(0,[5,0,-3]),(end/2,[7,0,-3]),(end,[5,0,-3])])
   elif clip=='attack':
    # CharacterMeleeGoal hits at 12/24 ticks. Raise, cross forward at 12t, recover.
    rotate(a,'weapon_arm',[(0,[-9,4,0]),(.4,[-72,-6,0]),(.5,[-60,-6,0]),(.6,[25,3,0]),(.73,[31,6,0]),(end,[-9,4,0])])
    rotate(a,'war_frame',[(0,[0,0,0]),(.45,[0,-16,0]),(.6,[0,19,0]),(.75,[0,24,0]),(end,[0,0,0])])
    rotate(a,'broken_helm',[(0,[7,-6,0]),(.45,[9,12,0]),(.6,[9,-15,0]),(end,[7,-6,0])])
    rotate(a,'breach_arm',[(0,[5,0,-3]),(.5,[-8,0,-5]),(.6,[8,0,-3]),(.78,[11,0,-3]),(end,[5,0,-3])])
  elif id=='xianzhen_duantoujiang':
   if clip in ('idle','walk'):
    # Rotate the entire hanging assembly about its existing anchor: chain stays attached.
    rotate(a,'bound_head',[(0,[0,-16,5]),(end*.4,[0,-21,8]),(end*.75,[0,-12,3]),(end,[0,-16,5])])
    if clip=='idle':
     rotate(a,'giant_arm_-1',[(0,[4,0,-4]),(end/2,[6,0,-4]),(end,[4,0,-4])])
     rotate(a,'giant_arm_1',[(0,[-6,0,2]),(end/2,[-8,0,2]),(end,[-6,0,2])])
   elif clip=='roar':
    # 24t shout stays aimed forward; the former 48-degree roll hid its face.
    rotate(a,'bound_head',[(0,[0,-16,5]),(.6,[-4,-21,12]),(1.1,[-7,-16,16]),(1.2,[-11,-12,18]),(1.4,[-5,-16,16]),(2.1,[0,-18,7]),(end,[0,-16,5])])
    rotate(a,'giant_arm_-1',[(0,[4,0,-4]),(.9,[-15,0,-9]),(1.2,[-22,0,-12]),(1.5,[-14,0,-8]),(end,[4,0,-4])])
   elif clip=='throw':
    rotate(a,'bound_head',[(0,[0,-16,5]),(.8,[-5,-11,10]),(1,[-8,-8,12]),(1.3,[-2,-18,9]),(end,[0,-16,5])])
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
