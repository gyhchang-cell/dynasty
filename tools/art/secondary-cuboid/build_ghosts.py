"""Wet rag spirit, animated paper fan and floating hood: original cuboid assets."""
import json
from PIL import Image, ImageDraw
from build_models import Rig, PALETTES, ASSET, OUT, keys

PALETTES.update({
    'drowning_ghost':['#25393e','#4f7374','#a4b8ad','#a8a977'],
    'paper_money_ghost':['#30313c','#9b8359','#e3d8ac','#c3ac69'],
    'wandering_spirit':['#2e3543','#677b83','#a5b9b6','#d5cda1'],
})

def drowning():
    r=Rig('drowning_ghost');r.bone('root',(0,0,0),None)
    r.bone('body',(0,8,0));r.cube('body',(-2,6,-1.5),(4,4,3),1)
    r.bone('chest',(0,9,0),'body');r.cube('chest',(-2.5,9,-1),(5,2,2),2)
    r.bone('waist',(0,6,0),'body');r.cube('waist',(-1.5,5,-1),(3,2,2),1)
    r.bone('rags',(0,5,0),'waist')
    r.cube('rags',(-2.5,1,-1.5),(2,4,3),4);r.cube('rags',(.5,2,-1.5),(2,3,3),1)
    r.bone('neck',(0,11,0),'chest');r.cube('neck',(-1,11,-1),(2,1,2),2)
    r.bone('head',(0,12,0),'neck');r.cube('head',(-2.5,12,-2),(5,3,4),2)
    r.cube('head',(-2.75,13,-2.25),(2,1,1),0);r.cube('head',(.75,13,-2.25),(2,1,1),0)
    r.cube('head',(-1,12,-3),(2,1,1),3)
    r.bone('jaw',(0,12,-1),'head');r.cube('jaw',(-1.5,11.5,-2.5),(3,.5,2),2)
    r.bone('hair',(0,15,0),'head');r.cube('hair',(-3,15,-2),(6,1,4),0)
    for x,h in [(-3,7),(-1.5,5),(1.5,6),(2,8)]:r.cube('hair',(x,15-h,2),(1,h,1),0)
    for side,s in [('left',1),('right',-1)]:
        arm=r.bone(side+'_fin',(s*2.5,10,0),'chest')
        r.cube(arm,((2.5 if s>0 else -4),6,-.75),(1.5,4,1.5),1)
        fore=r.bone(side+'_forearm',(s*3.25,6,0),arm)
        r.cube(fore,((2.75 if s>0 else -3.75),3,-.5),(1,3,1),2)
        r.cube(fore,((2.5 if s>0 else -4),2,-1),(1.5,1,2),0)
    r.bone('tail',(0,2,1),'waist');r.cube('tail',(-1.5,0,1),(3,1,4),1)
    return r.save()

def paper():
    r=Rig('paper_money_ghost');r.bone('root',(0,0,0),None)
    r.bone('body',(0,14,0));r.cube('body',(-2,10,0),(4,6,1),0)
    r.bone('head',(0,18,0),'body')
    # Square coin frame with an actual aperture, original shape and four colours.
    r.cube('head',(-3,20,-1),(6,1,1),3);r.cube('head',(-3,15,-1),(6,1,1),3)
    r.cube('head',(-3,16,-1),(1,4,1),1);r.cube('head',(2,16,-1),(1,4,1),1)
    for i,(x,y,z) in enumerate([(-5,14,-.5),(5,14,.5),(-7,8,0),(7,8,1),(-5,21,0),(5,21,.5),(-3,4,-.5),(3,4,.5)]):
        b=r.bone('paper_'+str(i),(x,y,z),'body')
        r.by[b]['rotation']=[0,0,(12 if i%2 else -12)]
        r.cube(b,(x-2,y-3,z),(4,6,.5),8)
    r.bone('tail',(0,10,0),'body');r.cube('tail',(-1,5,0),(2,5,.5),2)
    r.bone('tail_tip',(0,5,0),'tail');r.cube('tail_tip',(-1,2,.75),(2,3,.5),1)
    r.save()
    p=ASSET/'textures/entity/secondary/paper_money_ghost.png';im=Image.open(p);d=ImageDraw.Draw(im)
    d.rectangle((0,64,31,95),fill=PALETTES[r.id][2])
    d.rectangle((0,64,1,69),fill=PALETTES[r.id][3]);d.rectangle((2,66,3,67),fill=PALETTES[r.id][0]);im.save(p)
    return r

def wandering():
    r=Rig('wandering_spirit');r.bone('root',(0,0,0),None)
    r.bone('body',(0,12,0));r.cube('body',(-3,9,-1.5),(6,7,3),1)
    r.bone('mantle',(0,16,0),'body');r.cube('mantle',(-5,14,-2),(10,3,4),0)
    r.cube('mantle',(-4,17,-1.5),(8,1,3),2)
    r.bone('head',(0,18,0),'mantle')
    r.cube('head',(-3,21,-2),(6,2,4),1)
    r.cube('head',(-3,17,-2),(1,4,4),1);r.cube('head',(2,17,-2),(1,4,4),1)
    r.cube('head',(-2,18,1),(4,3,1),0)
    r.bone('mask',(0,19,-1),'head');r.cube('mask',(-1.5,18,-1.5),(3,2,1),3)
    r.cube('mask',(-1,19,-2),(2,.5,.5),0)
    r.bone('front_robe',(0,13,-2),'body');r.cube('front_robe',(-2,8,-2),(4,6,.5),2)
    for side,s in [('left',1),('right',-1)]:
        b=r.bone(side+'_rag',(s*2,9,0),'body')
        r.cube(b,((1 if s>0 else -3),4,-1),(2,5,2),1)
    r.bone('tail',(0,9,1),'body');r.cube('tail',(-1.5,4,1),(3,5,1),2)
    r.bone('tail_tip',(0,4,1),'tail');r.cube('tail_tip',(-1,1,1),(2,3,1),1)
    r.bone('knot',(0,1,1),'tail_tip');r.cube('knot',(-.5,0,1),(1,1,1),3)
    return r.save()

def animations(r):
    clips={}
    for name,length,amp in [('idle',1.8,3),('wander',1.1,8),('hunt',.75,12),('flee',.55,18),('attack',.8,0),('special',1.2,0),('evade',.7,0)]:
        ch={'body':{'rotation':keys(length,[[0,0,-2],[0,0,2],[0,0,-2]])},'tail':{'rotation':keys(length,[[amp/2,0,0],[-amp/2,0,0],[amp/2,0,0]])}}
        if r.id=='drowning_ghost':
            for side,s in [('left',1),('right',-1)]:ch[side+'_fin']={'rotation':keys(length,[[amp*s,0,0],[-amp*s,0,0],[amp*s,0,0]])}
            ch['hair']={'rotation':keys(length,[[3,0,0],[-3,0,0],[3,0,0]])}
            if name in ['attack','special']:
                for side in ['left','right']:ch[side+'_fin']={'rotation':keys(length,[[0,0,0],[65,0,0],[-25,0,0],[0,0,0]])}
                ch['jaw']={'rotation':keys(length,[[0,0,0],[25,0,0],[0,0,0]])}
        elif r.id=='paper_money_ghost':
            for i in range(8):
                s=1 if i%2 else -1
                amount=55 if name in ['attack','special'] else amp
                ch['paper_'+str(i)]={'rotation':keys(length,[[0,amount*s,0],[0,-amount*s,0],[0,amount*s,0]])}
            ch['head']={'rotation':keys(length,[[0,-10,0],[0,10,0],[0,-10,0]])}
        else:
            for side,s in [('left',1),('right',-1)]:ch[side+'_rag']={'rotation':keys(length,[[amp*s,0,0],[-amp*s,0,0],[amp*s,0,0]])}
            ch['front_robe']={'rotation':keys(length,[[3,0,0],[-3,0,0],[3,0,0]])}
            if name in ['attack','special']:
                ch['mantle']={'rotation':keys(length,[[0,0,0],[-15,0,0],[20,0,0],[0,0,0]])}
                ch['mask']={'rotation':keys(length,[[0,0,0],[0,30,0],[0,0,0]])}
        if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,0,20],[0,0,0]])}
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        clips[name]=json.loads(json.dumps(clips['evade' if name in ['return_water','side_charge','circle','burrow'] else 'special']))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for r in [drowning(),paper(),wandering()]:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    from pixel16 import export
    export();print('Generated three distinct ghost rigs')

if __name__=='__main__':main()
