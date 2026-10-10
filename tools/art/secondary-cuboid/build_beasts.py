"""Four original quadrupeds, with distinct torso/head/hock/tail silhouettes."""
import json
from PIL import Image, ImageDraw
from build_models import Rig, PALETTES, ASSET, OUT, keys

PALETTES.update({
    'gray_wolf':['#30343e','#737982','#aab2b4','#ddd4b6'],
    'wild_boar':['#302a2d','#72513d','#a28153','#ddd2a4'],
    'golden_leopard':['#302b30','#bf8b3f','#e0bd69','#efe0b9'],
    'red_fox':['#302a31','#a45737','#d99153','#e9dbc2'],
})

def legs(r,front_z,rear_z,fox=False,boar=False):
    # Hip, hock and paw are separate; rear shin offsets make the hind profile
    # readable in silhouette rather than copying a four-stick box animal.
    for i,(s,z) in enumerate([(-1,front_z),(1,front_z),(-1,rear_z),(1,rear_z)]):
        x=s*(3 if boar else 2.5)
        upper=r.bone('leg_'+str(i),(x,7,z),'body')
        if i<2:
            r.cube(upper,(x-1,3,z-.75),(2,4,2),1)
        else:
            r.cube(upper,(x-1.5,4,z-1),(3,3,3),1)
        shin=r.bone('shin_'+str(i),(x,4,z+.5),upper)
        r.cube(shin,(x-1,1,z+(1 if i>=2 else -.75)),(2,3 if i>=2 else 2,2),1 if boar else 2)
        foot=r.bone('foot_'+str(i),(x,1,z),shin)
        r.cube(foot,(x-1.5,0,z-2 if i<2 else z),(3,1,3),0 if boar or fox else 3)

def wolf():
    r=Rig('gray_wolf');r.bone('root',(0,0,0),None)
    r.bone('body',(0,8,0));r.cube('body',(-3,6,-3),(6,4,10),1)
    r.bone('chest',(0,8,-2),'body');r.cube('chest',(-4,5,-4),(8,7,4),2)
    r.cube('chest',(-2,5,-5),(4,4,1),3)
    r.bone('neck',(0,10,-3),'chest');r.cube('neck',(-2,9,-5),(4,4,3),1)
    r.bone('head',(0,10,-5),'neck');r.cube('head',(-3,8,-8),(6,4,4),1)
    r.cube('head',(-3.25,10,-8.25),(1,1,1),0);r.cube('head',(2.25,10,-8.25),(1,1,1),0)
    r.cube('head',(-2,9,-11),(4,2,3),2);r.cube('head',(-1,9.5,-12),(2,1,1),0)
    r.bone('jaw',(0,9,-8),'head');r.cube('jaw',(-2,8,-11),(4,1,3),3)
    r.bone('ears',(0,12,-5),'head')
    for x in [-3,1]:
        r.cube('ears',(x,12,-6),(2,2,2),0);r.cube('ears',(x+.5,14,-6),(1,1,2),2)
    r.bone('tail',(0,8,6),'body');r.cube('tail',(-1.5,6,7),(3,3,4),1)
    r.bone('tail_tip',(0,7,10),'tail');r.cube('tail_tip',(-1,4,10),(2,3,3),0)
    legs(r,-2,5)
    return r.save()

def boar():
    r=Rig('wild_boar');r.bone('root',(0,0,0),None)
    r.bone('body',(0,8,1));r.cube('body',(-4,5,-3),(8,6,11),1)
    r.bone('chest',(0,8,-2),'body');r.cube('chest',(-5,5,-4),(10,7,4),1)
    r.bone('mane',(0,12,-2),'chest');r.cube('mane',(-2,12,-4),(4,2,7),0)
    r.cube('mane',(-1,14,-3),(2,1,4),2)
    r.bone('neck',(0,8,-4),'chest');r.cube('neck',(-3,6,-5),(6,5,2),1)
    r.bone('head',(0,8,-5),'neck');r.cube('head',(-4,5,-8),(8,5,3),1)
    r.cube('head',(-2,5,-11),(4,3,3),2);r.cube('head',(-2,5,-12),(4,3,1),3)
    r.cube('head',(-1.5,6,-12.25),(1,1,.25),0);r.cube('head',(.5,6,-12.25),(1,1,.25),0)
    r.cube('head',(-4.25,8,-8.25),(1,1,1),0);r.cube('head',(3.25,8,-8.25),(1,1,1),0)
    r.bone('tusks',(0,6,-8),'head')
    r.cube('tusks',(-4,4,-11),(2,2,3),3);r.cube('tusks',(2,4,-11),(2,2,3),3)
    r.cube('tusks',(-4,6,-11),(1,2,1),3);r.cube('tusks',(3,6,-11),(1,2,1),3)
    r.bone('ears',(0,10,-6),'head')
    r.cube('ears',(-5,9.5,-6),(2,3,1),0);r.cube('ears',(3,9.5,-6),(2,3,1),0)
    r.bone('jaw',(0,5,-8),'head');r.cube('jaw',(-2,4,-10),(4,1,2),0)
    r.bone('tail',(0,8,8),'body');r.cube('tail',(-.5,7,8),(1,1,3),2)
    r.bone('tail_tip',(0,7,11),'tail');r.cube('tail_tip',(-.5,5,10.5),(1,2,1),0)
    legs(r,-2,6,boar=True)
    return r.save()

def leopard():
    r=Rig('golden_leopard');r.bone('root',(0,0,0),None)
    r.bone('body',(0,8,1));r.cube('body',(-3,6,-3),(6,4,12),4)
    r.bone('chest',(0,8,-2),'body');r.cube('chest',(-3.5,5,-4),(7,6,4),4)
    r.cube('chest',(-2,5,-5),(4,3,1),3)
    r.bone('neck',(0,9,-4),'chest');r.cube('neck',(-2,7,-6),(4,3,2),2)
    r.bone('head',(0,9,-6),'neck');r.cube('head',(-3,7,-9),(6,4,4),2)
    r.cube('head',(-3.25,9,-9.25),(1,1,1),0);r.cube('head',(2.25,9,-9.25),(1,1,1),0)
    r.cube('head',(-2,7.5,-11),(4,2,2),3);r.cube('head',(-1,8.5,-12),(2,1,1),0)
    r.bone('jaw',(0,8,-9),'head');r.cube('jaw',(-2,7,-11),(4,.5,2),1)
    r.bone('ears',(0,11,-7),'head')
    r.cube('ears',(-3,11,-7),(2,2,1),0);r.cube('ears',(1,11,-7),(2,2,1),0)
    r.bone('tail',(0,8,8),'body');r.cube('tail',(-1,7,9),(2,2,4),4)
    parent='tail'
    for i,(z,y) in enumerate([(13,6),(17,5),(21,4)],1):
        b=r.bone('tail_'+str(i),(0,y+1,z),parent);r.cube(b,(-1,y,z),(2,2,4),0 if i==3 else 4);parent=b
    legs(r,-2,7)
    r.save()
    # Pixel rosettes are hand-placed solid 2x2 blocks, no blurred spots/noise.
    p=ASSET/'textures/entity/secondary/golden_leopard.png';im=Image.open(p);d=ImageDraw.Draw(im)
    d.rectangle((0,32,31,63),fill=PALETTES[r.id][1])
    for x,y in [(0,32),(6,36),(12,32),(18,36),(24,32),(0,42),(6,46),(12,42),(18,46),(24,42),(0,52),(6,56),(12,52),(18,56),(24,52)]:
        d.rectangle((x,y,x+1,y+1),fill=PALETTES[r.id][0])
    im.save(p)
    return r

def fox():
    r=Rig('red_fox');r.bone('root',(0,0,0),None)
    r.bone('body',(0,7,0));r.cube('body',(-2.5,5,-3),(5,4,9),1)
    r.bone('chest',(0,7,-2),'body');r.cube('chest',(-3,5,-4),(6,5,3),2)
    r.cube('chest',(-2,5,-5),(4,3,1),3)
    r.bone('neck',(0,9,-3),'chest');r.cube('neck',(-2,8,-5),(4,3,2),1)
    r.bone('head',(0,10,-5),'neck');r.cube('head',(-2.5,8,-8),(5,4,4),1)
    r.cube('head',(-2.75,10,-8.25),(1,1,1),0);r.cube('head',(1.75,10,-8.25),(1,1,1),0)
    r.cube('head',(-1.5,8,-10),(3,2,2),3);r.cube('head',(-1,9,-11),(2,1,1),0)
    r.bone('jaw',(0,9,-8),'head');r.cube('jaw',(-1.5,7.5,-10),(3,.5,2),2)
    r.bone('ears',(0,12,-5),'head')
    for x in [-3,1]:
        r.cube('ears',(x,12,-6),(2,2,2),0);r.cube('ears',(x+.5,14,-6),(1,2,2),1)
    r.bone('tail',(0,7,5),'body');r.cube('tail',(-2,4,6),(4,4,4),1)
    r.bone('tail_mid',(0,6,9),'tail');r.cube('tail_mid',(-2.5,4.5,10),(5,5,4),2)
    r.bone('tail_tip',(0,6,13),'tail_mid');r.cube('tail_tip',(-2,5,14),(4,4,3),3)
    legs(r,-2,4,fox=True)
    return r.save()

def animations(r):
    clips={}
    for name,length,amp in [('idle',1.8,1),('wander',1.0,14),('hunt',.65,24),('flee',.5,32),('attack',.7,0),('special',1.1,0),('evade',.6,0)]:
        ch={'head':{'rotation':keys(length,[[0,-amp/5,0],[0,amp/5,0],[0,-amp/5,0]])},'tail':{'rotation':keys(length,[[0,-6,0],[0,6,0],[0,-6,0]])}}
        for i in range(4):
            s=1 if i in [0,3] else -1
            ch['leg_'+str(i)]={'rotation':keys(length,[[amp*s,0,0],[-amp*s,0,0],[amp*s,0,0]])}
            ch['shin_'+str(i)]={'rotation':keys(length,[[-amp*s/2,0,0],[amp*s/2,0,0],[-amp*s/2,0,0]])}
        if name in ['attack','special']:
            ch['jaw']={'rotation':keys(length,[[0,0,0],[25,0,0],[0,0,0]])}
            if r.id=='wild_boar':
                ch['neck']={'rotation':keys(length,[[0,0,0],[22,0,0],[-20,0,0],[0,0,0]])}
                ch['chest']={'rotation':keys(length,[[0,0,0],[10,0,0],[-12,0,0],[0,0,0]])}
            elif r.id=='golden_leopard':
                ch['body']={'position':keys(length,[[0,0,0],[0,-2,0],[0,1,0],[0,0,0]])}
                for i in [0,1]:ch['leg_'+str(i)]={'rotation':keys(length,[[0,0,0],[40,0,0],[-45,0,0],[0,0,0]])}
            elif r.id=='gray_wolf':
                ch['neck']={'rotation':keys(length,[[0,0,0],[-16,0,0],[20,0,0],[0,0,0]])}
                ch['body']={'rotation':keys(length,[[0,0,0],[-10,0,0],[10,0,0],[0,0,0]])}
            else:
                ch['tail_mid']={'rotation':keys(length,[[0,0,0],[0,18,12],[0,-18,-12],[0,0,0]])}
                ch['head']={'rotation':keys(length,[[0,0,0],[-10,0,0],[15,0,0],[0,0,0]])}
        if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,0,15],[0,0,0]])}
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        src='evade' if name in ['burrow','return_water','side_charge','dive','circle'] else 'special'
        clips[name]=json.loads(json.dumps(clips[src]))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for r in [wolf(),boar(),leopard(),fox()]:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Generated four distinct beasts')

if __name__=='__main__':main()
