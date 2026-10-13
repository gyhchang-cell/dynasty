"""Five distinct professions plus a dedicated folded-paper puppet rig."""
import json
from build_models import Rig, PALETTES, ASSET, OUT, keys

IDS=['bandit_thug','night_watchman','herb_picker','famished_refugee','swindler','paper_cut_child']
PALETTES.update({
    'bandit_thug':['#302c33','#71504a','#a98a61','#dfc79c'],
    'night_watchman':['#29333e','#556d7b','#a69264','#d9c88e'],
    'herb_picker':['#2e3833','#62754d','#af995f','#dbca9c'],
    'famished_refugee':['#353132','#726459','#a28d72','#cfc19e'],
    'swindler':['#302d3d','#665078','#ab9264','#dfcda1'],
    'paper_cut_child':['#352e3d','#a35048','#d28e68','#e5d7ad'],
})

def core(id,thin=False):
    r=Rig(id);r.bone('root',(0,0,0),None);r.bone('body',(0,14,0))
    # Ordinary people: a readable Minecraft face, supported joints, no floating
    # eye blocks or long puppet nose. Existing animation/held-tool anchors stay.
    w=6 if thin else (7.5 if id=='bandit_thug' else 7)
    r.bone('pelvis',(0,13,0),'body');r.cube('pelvis',(-w/2,12,-1.75),(w,2,3.5),1)
    r.bone('waist',(0,14,0),'pelvis');r.cube('waist',(-2.5,14,-1.5),(5,2,3),0)
    r.bone('chest',(0,16,0),'waist');r.cube('chest',(-w/2,16,-1.75),(w,5,3.5),1)
    r.bone('neck',(0,21,0),'chest');r.cube('neck',(-1,21,-1),(2,1,2),3)
    r.bone('head',(0,22,0),'neck');r.cube('head',(-3.25,21.5,-3),(6.5,6.5,6),3)
    r.bone('jaw',(0,22,-1),'head') # Kept for the saved animation contract.
    for side,s in [('left',1),('right',-1)]:
        arm=r.bone(side+'_upper_arm',(s*3.5,20,0),'chest')
        r.cube(arm,((3 if s>0 else -5.5),15,-1.25),(2.5,5,2.5),1)
        elbow=r.bone(side+'_elbow',(s*4,15,0),arm)
        r.cube(elbow,((3 if s>0 else -5.5),14,-1.25),(2.5,1,2.5),2)
        fore=r.bone(side+'_forearm',(s*4,14,0),elbow)
        r.cube(fore,((3 if s>0 else -5.5),10,-1.25),(2.5,4,2.5),3)
        wrist=r.bone(side+'_wrist',(s*4,10,0),fore)
        hand=r.bone(side+'_hand',(s*4,9,-1),wrist)
        r.cube(hand,((2.75 if s>0 else -5.25),8,-2),(2.5,2,2.5),3)
        thigh=r.bone(side+'_thigh',(s*1.75,12,0),'pelvis')
        r.cube(thigh,(s*1.75-1.375,7,-1.25),(2.75,5,2.5),1)
        knee=r.bone(side+'_knee',(s*1.75,7,0),thigh)
        shin=r.bone(side+'_shin',(s*1.75,7,0),knee)
        r.cube(shin,(s*1.75-1.125,2,-1.125),(2.25,5,2.25),2)
        ankle=r.bone(side+'_ankle',(s*1.75,2,0),shin)
        foot=r.bone(side+'_foot',(s*1.75,1,-1),ankle)
        r.cube(foot,(s*1.75-1.5,0,-2.5),(3,2,4),0)
    return r

def bandit():
    r=core('bandit_thug')
    r.bone('helmet',(0,28,0),'head');r.cube('helmet',(-3.75,27,-3.5),(7.5,1.5,7),0)
    r.cube('helmet',(-3,28.5,-2.75),(6,1,5.5),2)
    r.cube('helmet',(-3.75,24,.5),(1,3,2.5),0)
    r.bone('mask',(0,23,-2),'head');r.cube('mask',(-3.25,21.75,-3.5),(6.5,2,.5),1)
    r.bone('armor',(0,18,0),'chest');r.cube('armor',(-4,16.5,-2.5),(8,4,.75),2)
    r.bone('left_pauldron',(3.5,20,0),'left_upper_arm');r.cube('left_pauldron',(3,20,-1.5),(3,2,3),0)
    r.bone('skirt',(0,13,0),'pelvis')
    r.cube('skirt',(-3,10,-2.5),(2.5,3,.75),2);r.cube('skirt',(.5,11,-2.5),(2.5,2,.75),2)
    r.bone('blade',(4,9,-1),'left_hand')
    r.by['blade']['rotation']=[0,0,14]
    r.cube('blade',(3.5,6,-1.5),(1,6,1),0);r.cube('blade',(2.5,12,-1.5),(3,1,1),2)
    r.cube('blade',(3.5,13,-1.5),(1.5,8,1),2);r.cube('blade',(4,21,-1.5),(1,2,1),3)
    return r.save()

def watchman():
    r=core('night_watchman')
    r.bone('cap',(0,28,0),'head');r.cube('cap',(-3.75,27.5,-3.5),(7.5,1,7),0)
    r.cube('cap',(-3,28.5,-2.5),(6,1,5),1)
    r.bone('vest',(0,18,0),'chest');r.cube('vest',(-3.5,16,-2.25),(7,5,.75),4)
    r.cube('vest',(-2.5,15,-2.25),(5,1,.75),2)
    r.bone('lantern',(4,9,-1),'left_hand')
    r.cube('lantern',(3.5,7,-1.5),(1,4,1),0)
    r.cube('lantern',(2.5,3,-2.5),(3,3,3),3)
    r.cube('lantern',(2,6,-3),(4,1,4),2);r.cube('lantern',(2,2,-3),(4,1,4),0)
    r.bone('clapper',(-4,9,-1),'right_hand');r.cube('clapper',(-4.5,6,-1.5),(1,7,1),2)
    r.by['clapper']['rotation']=[15,0,0]
    return r.save()

def herb():
    r=core('herb_picker')
    r.bone('hat',(0,28,0),'head');r.cube('hat',(-4.5,28,-4),(9,1,8),2)
    r.cube('hat',(-3.5,29,-3),(7,1,6),3)
    r.bone('basket',(0,16,1.5),'chest')
    r.cube('basket',(-3.5,12,1.5),(7,7,4),4)
    r.cube('basket',(-4,19,1.5),(8,1,4),2)
    r.cube('basket',(-2,20,2),(2,2,2),1);r.cube('basket',(1,20,3),(2,3,2),1)
    r.bone('straps',(0,20,0),'chest')
    r.cube('straps',(-2.5,16,-2),(1,5,.5),0);r.cube('straps',(1.5,16,-2),(1,5,.5),0)
    r.bone('sickle',(-4,9,-1),'right_hand');r.cube('sickle',(-4.5,7,-1.5),(1,6,1),0)
    r.by['sickle']['rotation']=[0,0,-14]
    r.cube('sickle',(-4.5,13,-1.5),(3,1,1),2);r.cube('sickle',(-2.5,11,-1.5),(1,2,1),2)
    return r.save()

def refugee():
    r=core('famished_refugee',thin=True)
    r.by['chest']['rotation']=[12,0,0]
    r.bone('rags',(0,15,0),'waist')
    r.cube('rags',(-3,11,-2),(2,5,.5),2);r.cube('rags',(1,12,-2),(2,4,.5),0)
    r.bone('hood',(0,28,0),'head');r.cube('hood',(-3.5,27.5,-2.5),(7,1,6),1)
    r.cube('hood',(-3.5,24,3),(7,3.5,1),1)
    r.bone('bundle',(0,17,1.5),'chest');r.cube('bundle',(-2.5,16,1.5),(5,4,3),2)
    r.cube('bundle',(-.5,15,4.5),(1,5,.5),0)
    r.bone('staff',(4,9,-1),'left_hand');r.cube('staff',(3.5,0,-1.5),(1,17,1),1)
    r.by['staff']['rotation']=[15,0,0]
    return r.save()

def swindler():
    r=core('swindler')
    r.bone('robe',(0,14,0),'waist')
    r.cube('robe',(-4,8,-2.25),(3.5,6,.75),1);r.cube('robe',(.5,8,-2.25),(3.5,6,.75),1)
    r.cube('robe',(-4,8,1.5),(8,6,.75),4)
    r.bone('crown',(0,28,0),'head');r.cube('crown',(-3.5,28,-3.25),(7,1,6.5),0)
    r.cube('crown',(-1.5,29,-2),(3,2,4),2)
    for side,s in [('left',1),('right',-1)]:
        b=r.bone(side+'_cuff',(s*4,15,0),side+'_elbow')
        r.cube(b,((3 if s>0 else -5.5),13,-1.5),(2.5,2,3),1)
    r.bone('abacus',(-4,9,-1),'right_hand')
    r.cube('abacus',(-6,7,-2.5),(4,1,.5),0);r.cube('abacus',(-6,11,-2.5),(4,1,.5),0)
    r.cube('abacus',(-6,8,-2.5),(1,3,.5),2);r.cube('abacus',(-3,8,-2.5),(1,3,.5),2)
    r.cube('abacus',(-5,8.5,-2.5),(2,1,.5),3)
    r.cube('abacus',(-4.25,8.75,-2),(.5,.5,1),2)
    return r.save()

def paper_child():
    # Dedicated thin sheet puppet: articulated fold lines and cut-out clothing,
    # retaining legacy anatomical names solely for saved animation contracts.
    r=Rig('paper_cut_child');r.bone('root',(0,0,0),None);r.bone('body',(0,14,0))
    r.bone('pelvis',(0,13,0),'body');r.cube('pelvis',(-2,12,-.25),(4,2,.5),1)
    r.bone('waist',(0,14,0),'pelvis');r.cube('waist',(-1.5,14,-.25),(3,2,.5),3)
    r.bone('chest',(0,16,0),'waist')
    r.cube('chest',(-3,16,-.25),(2,5,.5),1);r.cube('chest',(1,16,-.25),(2,5,.5),1)
    r.cube('chest',(-1,19,-.25),(2,2,.5),3)
    r.bone('neck',(0,21,0),'chest');r.cube('neck',(-1,21,-.25),(2,1,.5),3)
    r.bone('head',(0,22,0),'neck');r.cube('head',(-2,22,-.25),(4,4,.5),3)
    r.cube('head',(-2,25,-.5),(4,1,.25),0)
    r.cube('head',(-1.5,24,-.5),(1,1,.25),0);r.cube('head',(.5,24,-.5),(1,1,.25),0)
    r.bone('bow',(0,26,0),'head')
    r.cube('bow',(-4,25,-.25),(2,2,.5),0);r.cube('bow',(2,25,-.25),(2,2,.5),0)
    r.cube('bow',(-3.5,27,-.25),(2,1,.5),1);r.cube('bow',(1.5,27,-.25),(2,1,.5),1)
    for side,s in [('left',1),('right',-1)]:
        arm=r.bone(side+'_upper_arm',(s*3,20,0),'chest')
        r.cube(arm,((3 if s>0 else -5),15,-.25),(2,5,.5),1)
        elbow=r.bone(side+'_elbow',(s*4,15,0),arm)
        fore=r.bone(side+'_forearm',(s*4,15,0),elbow)
        r.cube(fore,((3.5 if s>0 else -4.5),10,-.25),(1,5,.5),3)
        wrist=r.bone(side+'_wrist',(s*4,10,0),fore)
        hand=r.bone(side+'_hand',(s*4,9,0),wrist);r.cube(hand,((3 if s>0 else -5),8,-.25),(2,2,.5),1)
        thigh=r.bone(side+'_thigh',(s*1.5,12,0),'pelvis');r.cube(thigh,(s*1.5-1,7,-.25),(2,5,.5),1)
        knee=r.bone(side+'_knee',(s*1.5,7,0),thigh)
        shin=r.bone(side+'_shin',(s*1.5,7,0),knee);r.cube(shin,(s*1.5-.5,2,-.25),(1,5,.5),3)
        ankle=r.bone(side+'_ankle',(s*1.5,2,0),shin)
        foot=r.bone(side+'_foot',(s*1.5,1,0),ankle);r.cube(foot,(s*1.5-1.5,0,-.25),(3,2,.5),0)
    r.bone('ribbons',(0,14,.5),'waist')
    r.cube('ribbons',(-3,8,.5),(1,6,.5),2);r.cube('ribbons',(2,6,.5),(1,8,.5),2)
    return r.save()

def animations(r):
    clips={};paper=r.id=='paper_cut_child'
    for name,length,amp in [('idle',1.8,2),('wander',1.0,16),('hunt',.65,25),('flee',.5,32),('attack',.8,0),('special',1.2,0),('evade',.7,0)]:
        ch={'head':{'rotation':keys(length,[[0,-3,0],[0,3,0],[0,-3,0]])}}
        for side,s in [('left',1),('right',-1)]:
            a=[amp*s,0,0];b=[-amp*s,0,0]
            if paper:a=[0,0,amp*s];b=[0,0,-amp*s]
            ch[side+'_upper_arm']={'rotation':keys(length,[a,b,a])}
            ch[side+'_thigh']={'rotation':keys(length,[b,a,b])}
            ch[side+'_knee']={'rotation':keys(length,[[0,0,0],[amp/3,0,0],[0,0,0]])}
        if name in ['attack','special']:
            if paper:
                ch['chest']={'rotation':keys(length,[[0,0,0],[0,20,0],[0,-20,0],[0,0,0]])}
                ch['ribbons']={'rotation':keys(length,[[0,0,0],[15,0,15],[-15,0,-15],[0,0,0]])}
            else:
                active='left' if r.id in ['bandit_thug','night_watchman','famished_refugee'] else 'right'
                ch[active+'_upper_arm']={'rotation':keys(length,[[0,0,0],[-25,0,0],[65,0,0],[0,0,0]])}
                ch[active+'_elbow']={'rotation':keys(length,[[0,0,0],[20,0,0],[35,0,0],[0,0,0]])}
                ch['chest']={'rotation':keys(length,[[0,0,0],[0,-12,0],[0,15,0],[0,0,0]])}
        if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,0,12],[0,0,0]])}
        if r.id=='herb_picker':ch['basket']={'rotation':keys(length,[[2,0,0],[-2,0,0],[2,0,0]])}
        if r.id=='famished_refugee':ch['rags']={'rotation':keys(length,[[3,0,0],[-3,0,0],[3,0,0]])}
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        clips[name]=json.loads(json.dumps(clips['evade' if name in ['return_water','side_charge','circle','burrow'] else 'special']))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for r in [bandit(),watchman(),herb(),refugee(),swindler(),paper_child()]:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    from pixel16 import export
    export();print('Generated five professions and a dedicated paper puppet')

if __name__=='__main__':main()
