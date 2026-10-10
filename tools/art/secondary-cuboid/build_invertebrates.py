"""Original crab, beetle, scorpion and mechanical rat: species-specific cuboids."""
import json
from build_models import Rig, PALETTES, ASSET, OUT, keys

PALETTES.update({
    'crab_soldier':['#303b46','#567d88','#a0b9ac','#d7c39b'],
    'corpse_beetle':['#242d30','#486052','#849167','#c5bd91'],
    'venom_scorpion':['#2c293b','#635065','#ad7751','#ddbd74'],
    'clockwork_rat':['#302f38','#8a6744','#b2a886','#dec985'],
})

def crab():
    r=Rig('crab_soldier');r.bone('root',(0,0,0),None)
    r.bone('body',(0,6,0));r.cube('body',(-6,5,-4),(12,5,8),1)
    r.bone('carapace',(0,9,0),'body');r.cube('carapace',(-5,10,-3),(10,2,6),2)
    r.cube('carapace',(-4,6,4),(8,3,1),0)
    r.bone('neck',(0,8,-4),'body');r.cube('neck',(-4,7,-5),(8,3,1),2)
    r.bone('head',(0,9,-5),'neck');r.cube('head',(-3,7,-6),(6,3,1),1)
    r.cube('head',(-2,7,-7),(4,1,1),0)
    for side,s in [('left',1),('right',-1)]:
        eye=r.bone(side+'_eye',(s*3,10,-4),'head')
        r.cube(eye,(s*3-1,10,-5),(2,3,2),2);r.cube(eye,(s*3-1,13,-5),(2,2,2),0)
        arm=r.bone(side+'_arm',(s*5,9,-2),'body')
        r.cube(arm,((5 if s>0 else -8),8,-4),(3,3,3),4)
        claw=r.bone(side+'_claw',(s*8,9,-4),arm)
        r.cube(claw,((7 if s>0 else -11),8,-7),(4,4,3),1)
        # Two jaws with a deliberate air gap; moving jaw closes in local bone space.
        r.cube(claw,((7 if s>0 else -11),8,-10),(1,4,3),3)
        jaw=r.bone(side+'_pincer',(s*10,9,-7),claw)
        r.cube(jaw,((10 if s>0 else -8),8,-10),(1,3,3),2)
    r.bone('tail',(0,6,4),'body');r.cube('tail',(-3,4,4),(6,3,2),1)
    for i,(s,z) in enumerate([(-1,-3),(1,-3),(-1,0),(1,0),(-1,3),(1,3)]):
        leg=r.bone('leg_'+str(i),(s*5,5,z),'body')
        r.cube(leg,((6 if s>0 else -8),3,z-1),(2,2,2),2)
        foot=r.bone('foot_'+str(i),(s*8,3,z),leg)
        r.cube(foot,((8 if s>0 else -10),0,z-1),(2,3,2),1)
    return r.save()

def beetle():
    r=Rig('corpse_beetle');r.bone('root',(0,0,0),None)
    r.bone('body',(0,4,0));r.cube('body',(-4,2,-3),(8,3,9),0)
    r.bone('neck',(0,4,-3),'body');r.cube('neck',(-3,3,-5),(6,3,2),1)
    r.bone('head',(0,4,-5),'neck');r.cube('head',(-3,3,-7),(6,3,2),2)
    r.cube('head',(-3,5,-8),(2,1,1),0);r.cube('head',(1,5,-8),(2,1,1),0)
    for side,s in [('left',1),('right',-1)]:
        wing=r.bone(side+'_elytron',(s*.5,5,-2),'body')
        r.cube(wing,((.5 if s>0 else -4.5),5,-2),(4,2,7),4)
        r.cube(wing,((.5 if s>0 else -3.5),7,-1),(3,1,5),1)
        jaw=r.bone(side+'_mandible',(s*2,4,-7),'head')
        r.cube(jaw,((2 if s>0 else -4),2,-9),(2,2,2),3)
        r.cube(jaw,((1 if s>0 else -2),2,-10),(1,2,1),3)
        antenna=r.bone(side+'_antenna',(s*2,6,-6),'head')
        r.cube(antenna,((3 if s>0 else -4),6,-8),(1,1,3),1)
    r.bone('tail',(0,3,5),'body');r.cube('tail',(-3,2,6),(6,2,1),1)
    for i,(s,z) in enumerate([(-1,-2),(1,-2),(-1,1),(1,1),(-1,4),(1,4)]):
        leg=r.bone('leg_'+str(i),(s*4,4,z),'body')
        r.cube(leg,((4 if s>0 else -6),2,z-1),(2,2,2),1)
        foot=r.bone('foot_'+str(i),(s*6,2,z),leg)
        r.cube(foot,((6 if s>0 else -8),0,z-1),(2,2,2),2)
    return r.save()

def scorpion():
    r=Rig('venom_scorpion');r.bone('root',(0,0,0),None)
    r.bone('body',(0,3,0));r.cube('body',(-3,2,-2),(6,3,8),1)
    r.cube('body',(-4,3,-1),(8,3,5),4)
    r.bone('neck',(0,3,-2),'body');r.cube('neck',(-3,2,-4),(6,3,2),2)
    r.bone('head',(0,3,-4),'neck');r.cube('head',(-2,2,-6),(4,3,2),1)
    r.cube('head',(-2,4,-7),(1,1,1),3);r.cube('head',(1,4,-7),(1,1,1),3)
    for side,s in [('left',1),('right',-1)]:
        arm=r.bone(side+'_arm',(s*3,3,-3),'body')
        r.cube(arm,((3 if s>0 else -6),2,-6),(3,2,3),2)
        claw=r.bone(side+'_claw',(s*5,3,-6),arm)
        r.cube(claw,((4 if s>0 else -7),1,-9),(3,3,3),1)
        r.cube(claw,((4 if s>0 else -7),1,-12),(1,2,3),3)
        jaw=r.bone(side+'_pincer',(s*6,2,-9),claw)
        r.cube(jaw,((6 if s>0 else -5),1,-12),(1,2,3),2)
    r.bone('tail',(0,3,6),'body');r.cube('tail',(-2,3,6),(4,2,3),2)
    r.bone('tail_1',(0,4,7),'tail');r.cube('tail_1',(-1.5,4,7.5),(3,3,2),1)
    r.bone('tail_2',(0,6,8),'tail_1');r.cube('tail_2',(-1,6,7.25),(2,3,2),2)
    r.bone('tail_3',(0,8,7),'tail_2');r.cube('tail_3',(-1.25,8,4),(2.5,2,3.5),1)
    r.bone('stinger',(0,9,4),'tail_3');r.cube('stinger',(-1,7,3),(2,3,1),3)
    r.cube('stinger',(-.5,6,3),(1,1,1),0)
    for i,(s,z) in enumerate([(-1,-1),(1,-1),(-1,2),(1,2),(-1,5),(1,5)]):
        leg=r.bone('leg_'+str(i),(s*3,3,z),'body')
        r.cube(leg,((4 if s>0 else -6),1,z-1),(2,2,2),1)
        foot=r.bone('foot_'+str(i),(s*6,1,z),leg)
        r.cube(foot,((6 if s>0 else -8),0,z-1),(2,1,2),2)
    return r.save()

def rat():
    r=Rig('clockwork_rat');r.bone('root',(0,0,0),None)
    r.bone('body',(0,3,0));r.cube('body',(-3,2,-2),(6,4,6),1)
    r.cube('body',(-2,6,-1),(4,1,4),2)
    r.cube('body',(-3.5,3,-1),(1,2,3),0);r.cube('body',(2.5,3,-1),(1,2,3),0)
    r.bone('neck',(0,4,-2),'body');r.cube('neck',(-2,3,-3),(4,3,1),2)
    r.bone('head',(0,4,-3),'neck');r.cube('head',(-2.5,2.5,-6),(5,3,3),1)
    r.cube('head',(-1.5,2.5,-8),(3,2,2),2);r.cube('head',(-1,3,-9),(2,1,1),0)
    r.cube('head',(-3,4,-6.25),(1,1,1),3);r.cube('head',(2,4,-6.25),(1,1,1),3)
    r.bone('ears',(0,5,-3),'head')
    r.cube('ears',(-4,5,-4),(2,2,1),2);r.cube('ears',(2,5,-4),(2,2,1),2)
    r.bone('key',(0,5,4),'body');r.cube('key',(-.5,4.5,4),(1,1,3),0)
    r.cube('key',(-2,3.5,7),(4,1,1),3);r.cube('key',(-2,5.5,7),(4,1,1),3)
    r.cube('key',(-3,3.5,7),(1,3,1),3);r.cube('key',(2,3.5,7),(1,3,1),3)
    r.bone('tail',(0,2,4),'body');r.cube('tail',(-1,1,4),(2,2,3),2)
    parent='tail'
    for i,(z,x) in enumerate([(7,0),(10,1),(13,2)],1):
        b=r.bone('tail_'+str(i),(x,1,z),parent);r.cube(b,(x-.5,.5,z),(1,1,3),1);parent=b
    for i,(s,z) in enumerate([(-1,-1),(1,-1),(-1,3),(1,3)]):
        leg=r.bone('leg_'+str(i),(s*2,3,z),'body')
        r.cube(leg,((2 if s>0 else -4),1,z-.75),(2,2,2 if i<2 else 3),2)
        foot=r.bone('foot_'+str(i),(s*3,1,z),leg)
        r.cube(foot,((2 if s>0 else -4),0,z-2),(2,1,3),0)
    return r.save()

def animations(r):
    clips={};leg_count=4 if r.id=='clockwork_rat' else 6
    for name,length,amp in [('idle',1.6,1),('wander',.8,10),('hunt',.55,18),('flee',.4,24),('attack',.7,0),('special',1.2,0),('evade',.6,0)]:
        ch={'head':{'rotation':keys(length,[[0,-amp/4,0],[0,amp/4,0],[0,-amp/4,0]])}}
        for i in range(leg_count):
            s=1 if i%3==0 else -1
            axis=2 if r.id=='crab_soldier' else 0
            a=[0,0,0];a[axis]=amp*s;b=[-v for v in a]
            ch['leg_'+str(i)]={'rotation':keys(length,[a,b,a])}
            ch['foot_'+str(i)]={'rotation':keys(length,[b,a,b])}
        if r.id=='crab_soldier':
            for side,s in [('left',1),('right',-1)]:
                ch[side+'_eye']={'rotation':keys(length,[[0,0,-2*s],[0,0,2*s],[0,0,-2*s]])}
                if name in ['attack','special']:
                    ch[side+'_arm']={'rotation':keys(length,[[0,0,0],[15,0,20*s],[30,0,-15*s],[0,0,0]])}
                    ch[side+'_pincer']={'rotation':keys(length,[[0,0,0],[0,25*s,0],[0,-12*s,0],[0,0,0]])}
            if name=='special':ch['body']={'position':keys(length,[[0,0,0],[0,2,0],[0,0,0]])}
        elif r.id=='corpse_beetle':
            for side,s in [('left',1),('right',-1)]:
                ch[side+'_antenna']={'rotation':keys(length,[[0,-4*s,0],[0,4*s,0],[0,-4*s,0]])}
                if name in ['attack','special']:
                    ch[side+'_mandible']={'rotation':keys(length,[[0,0,0],[0,28*s,0],[0,-12*s,0],[0,0,0]])}
                if name=='special':ch[side+'_elytron']={'rotation':keys(length,[[0,0,0],[0,0,-45*s],[0,0,0]])}
        elif r.id=='venom_scorpion':
            for i in range(1,4):ch['tail_'+str(i)]={'rotation':keys(length,[[0,-amp/4,0],[0,amp/4,0],[0,-amp/4,0]])}
            for side,s in [('left',1),('right',-1)]:
                if name in ['attack','special']:
                    ch[side+'_pincer']={'rotation':keys(length,[[0,0,0],[0,25*s,0],[0,-10*s,0],[0,0,0]])}
            if name in ['attack','special']:
                ch['tail']={'rotation':keys(length,[[0,0,0],[-25,0,0],[30,0,0],[0,0,0]])}
                for i in range(1,4):ch['tail_'+str(i)]={'rotation':keys(length,[[0,0,0],[-10,0,0],[25,0,0],[0,0,0]])}
                ch['stinger']={'rotation':keys(length,[[0,0,0],[20,0,0],[-30,0,0],[0,0,0]])}
        else:
            for i in range(1,4):ch['tail_'+str(i)]={'rotation':keys(length,[[0,amp/3,0],[0,-amp/3,0],[0,amp/3,0]])}
            ch['key']={'rotation':keys(length,[[0,0,-30],[0,0,30],[0,0,-30]])}
            if name in ['attack','special']:
                ch['head']={'rotation':keys(length,[[0,0,0],[-18,0,0],[25,0,0],[0,0,0]])}
                ch['body']={'rotation':keys(length,[[0,0,0],[-8,0,0],[12,0,0],[0,0,0]])}
        if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,0,12],[0,0,0]])}
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        src='evade' if name in ['burrow','return_water','side_charge','dive','circle'] else 'special'
        clips[name]=json.loads(json.dumps(clips[src]))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for r in [crab(),beetle(),scorpion(),rat()]:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    from pixel16 import export
    export()
    print('Generated four species rigs:',[(i,manifest[i]['cuboids']) for i in ['crab_soldier','corpse_beetle','venom_scorpion','clockwork_rat']])

if __name__=='__main__':main()
