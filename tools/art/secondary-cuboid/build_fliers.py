"""Dedicated raptor, stone-carrying bird, wooden machine and membrane-wing rigs."""
import json
from build_models import Rig, PALETTES, ASSET, OUT, keys

PALETTES.update({
    'gray_falcon':['#313643','#737c85','#babbb0','#d6b872'],
    'jingwei_bird':['#3d3342','#a05045','#d29366','#b7bdad'],
    'wooden_magpie':['#302e35','#805438','#baa16a','#d8c787'],
    'bat_demon':['#2e2838','#68505d','#a27b61','#d8c68a'],
})

def bird(id,mechanical=False,stone=False):
    r=Rig(id);r.bone('root',(0,0,0),None)
    r.bone('body',(0,5,0));r.cube('body',(-2.5,3,-2),(5,4,5),1)
    r.bone('breast',(0,5,-2),'body');r.cube('breast',(-2,3,-3),(4,3,1),2)
    r.bone('neck',(0,7,-1),'body');r.cube('neck',(-1.5,7,-2),(3,1,3),1)
    r.bone('head',(0,8,-2),'neck');r.cube('head',(-2,8,-4),(4,3,3),2 if mechanical else 1)
    r.cube('head',(-2.25,9,-4.25),(1,1,1),0);r.cube('head',(1.25,9,-4.25),(1,1,1),0)
    r.bone('beak',(0,8,-4),'head');r.cube('beak',(-1,8,-6),(2,2,2),0 if mechanical else 3)
    if not stone and not mechanical:r.cube('beak',(-1,7,-6),(2,1,1),0)
    if stone:
        r.bone('crest',(0,11,-2),'head');r.cube('crest',(-1,11,-3),(2,1,2),1)
        r.bone('stone',(0,8,-6),'beak');r.cube('stone',(-1.5,7,-8),(3,2,2),3)
    if mechanical:
        r.bone('gears',(0,5,2),'body')
        r.cube('gears',(-1,3,3),(2,4,1),3)
        r.cube('gears',(-2,4,3),(1,2,1),0);r.cube('gears',(1,4,3),(1,2,1),0)
        r.cube('body',(-2,7,-1),(4,1,3),2)
    for side,s in [('left',1),('right',-1)]:
        wing=r.bone(side+'_wing',(s*2,6,0),'body')
        outer=5 if stone else 6
        r.cube(wing,((2 if s>0 else -outer),5,-1),(outer-2,1,5),2 if mechanical else 1)
        if mechanical:r.cube(wing,((2 if s>0 else -4),5.25,-2.25),(2,2,2),0)
        tip=r.bone(side+'_wingtip',(s*outer,5,1),wing)
        r.cube(tip,((outer if s>0 else -outer-3),4.75,0),(3,1,4),3 if mechanical else 2)
        # Rectangular feathers/boards have coarse step ends, not dense mesh fringes.
        for i in range(2):
            x=outer+i if s>0 else -outer-i-2
            r.cube(tip,(x,4.25,3+i),(2,.5,2),1 if mechanical else 0)
        foot=r.bone(side+'_foot',(s*1.5,3,0),'body')
        r.cube(foot,(s*1.5-.5,1,0),(1,2,1),3)
        r.cube(foot,(s*1.5-1,0,-1),(2,1,3),0 if mechanical else 3)
    r.bone('tail',(0,4,3),'body')
    if mechanical:
        r.cube('tail',(-1.5,3.5,3),(3,1,7),1)
        r.cube('tail',(-1,3,10),(2,1,2),0)
    else:
        r.cube('tail',(-2,3,3),(4,1,4 if stone else 5),0)
        r.cube('tail',(-1,2.5,7 if stone else 8),(2,.5,2),2)
    return r.save()

def bat():
    r=Rig('bat_demon');r.bone('root',(0,0,0),None)
    r.bone('body',(0,5,0));r.cube('body',(-2,3,-1),(4,4,3),1)
    r.cube('body',(-1.5,3,-2),(3,3,1),2)
    r.bone('neck',(0,7,0),'body');r.cube('neck',(-1,7,-1),(2,1,2),1)
    r.bone('head',(0,8,-1),'neck');r.cube('head',(-2,8,-3),(4,3,3),1)
    r.cube('head',(-2.25,9,-3.25),(1,1,1),3);r.cube('head',(1.25,9,-3.25),(1,1,1),3)
    r.bone('jaw',(0,8,-3),'head');r.cube('jaw',(-1.5,7.5,-4),(3,1,1),0)
    r.cube('jaw',(-1.5,6.5,-4),(1,1,1),3);r.cube('jaw',(.5,6.5,-4),(1,1,1),3)
    r.bone('ears',(0,11,-1),'head')
    r.cube('ears',(-3,10.5,-2),(2,2.5,1),0);r.cube('ears',(1,10.5,-2),(2,2.5,1),0)
    for side,s in [('left',1),('right',-1)]:
        wing=r.bone(side+'_wing',(s*2,6,0),'body')
        r.cube(wing,((2 if s>0 else -7),6,-1),(5,1,1),0)
        r.cube(wing,((2 if s>0 else -6),3.5,0),(4,2.5,.5),2)
        tip=r.bone(side+'_wingtip',(s*6,6,0),wing)
        r.cube(tip,((6 if s>0 else -11),6,-1),(5,1,1),0)
        r.cube(tip,((6 if s>0 else -10),4,0),(4,2,.5),1)
        r.cube(tip,((6 if s>0 else -9),2.5,0),(3,1.5,.5),2)
        r.cube(tip,((6 if s>0 else -8),2,0),(2,.5,.5),1)
        foot=r.bone(side+'_foot',(s,3,1),'body')
        r.cube(foot,(s-.5,1,1),(1,2,1),0);r.cube(foot,(s-.5,0,0),(1,1,2),3)
    r.bone('tail',(0,3,2),'body');r.cube('tail',(-1,2,2),(2,1,3),1)
    return r.save()

def animations(r):
    clips={}
    for name,length,amp in [('idle',1.6,7),('wander',.9,24),('hunt',.65,34),('flee',.45,42),('attack',.7,0),('special',1.1,0),('evade',.6,0)]:
        ch={'head':{'rotation':keys(length,[[0,-3,0],[0,3,0],[0,-3,0]])}}
        for side,s in [('left',1),('right',-1)]:
            ch[side+'_wing']={'rotation':keys(length,[[0,0,-amp*s],[0,0,amp*s],[0,0,-amp*s]])}
            ch[side+'_wingtip']={'rotation':keys(length,[[0,0,-amp*s/2],[0,0,amp*s/2],[0,0,-amp*s/2]])}
            ch[side+'_foot']={'rotation':keys(length,[[8,0,0],[15,0,0],[8,0,0]])}
        ch['tail']={'rotation':keys(length,[[-3,0,0],[3,0,0],[-3,0,0]])}
        if r.id=='wooden_magpie':ch['gears']={'rotation':keys(length,[[0,0,-30],[0,0,30],[0,0,-30]])}
        if name in ['attack','special']:
            ch['body']={'rotation':keys(length,[[0,0,0],[25,0,0],[-15,0,0],[0,0,0]])}
            ch['head']={'rotation':keys(length,[[0,0,0],[20,0,0],[-20,0,0],[0,0,0]])}
            for side,s in [('left',1),('right',-1)]:ch[side+'_wing']={'rotation':keys(length,[[0,0,0],[0,0,45*s],[0,0,-25*s],[0,0,0]])}
            if r.id=='jingwei_bird':ch['stone']={'rotation':keys(length,[[0,0,0],[10,0,0],[0,0,0]])}
            if r.id=='bat_demon':ch['jaw']={'rotation':keys(length,[[0,0,0],[22,0,0],[0,0,0]])}
        if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,0,30],[0,0,0]])}
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        clips[name]=json.loads(json.dumps(clips['evade' if name in ['return_water','side_charge','circle','burrow'] else 'special']))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for r in [bird('gray_falcon'),bird('jingwei_bird',stone=True),bird('wooden_magpie',mechanical=True),bat()]:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Generated four distinct flying rigs')

if __name__=='__main__':main()
