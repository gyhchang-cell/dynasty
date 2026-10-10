"""Cuboid serpent, stone annelid and fourteen-insect swarm, no humanoid rigs."""
import json
from build_models import Rig, PALETTES, ASSET, OUT, keys

PALETTES.update({
    'giant_python':['#29392e','#596d43','#a6ad68','#d7c894'],
    'stone_worm':['#2a3037','#6b706a','#b7b094','#c9bc77'],
    'locust_swarm':['#30372f','#75834a','#b8b479','#e0d5a2'],
})

def center_long_rig(r):
    # Keep the root at the entity origin; center the authored tail/head envelope.
    for b in r.bones:
        if b['name']=='root':continue
        b['pivot'][2]-=6
        for c in b.get('cubes',[]):c['origin'][2]-=6
    return r.save()

def crawler(id,stone=False):
    r=Rig(id);r.bone('root',(0,0,0),None)
    r.bone('body',(0,3,0));r.cube('body',(-3,0,-3),(6,4 if not stone else 5,5),4)
    parent='body'
    for i,(x,z,w) in enumerate([(0,2,6),(3,5,6),(4,8,5),(3,11,4),(0,14,3),(-2,17,2)],1):
        b=r.bone('segment_'+str(i),(x,2,z),parent)
        r.cube(b,(x-w/2,0,z),(w,4 if i<4 else 3 if i<6 else 2,3),4 if not stone else 1)
        if stone:r.cube(b,(x-w/2+.5,4 if i<4 else 3 if i<6 else 2,z+.5),(w-1,1,2),2)
        parent=b
    r.bone('neck',(0,3,-3),'body');r.cube('neck',(-2.5,1,-5),(5,4,2),1)
    r.bone('head',(0,4,-5),'neck')
    if stone:
        # Four lip blocks surround a recessed dark cavity, not a painted mouth.
        r.cube('head',(-4,8,-8),(8,2,2),2)
        r.cube('head',(-4,2,-8),(1,6,2),1);r.cube('head',(3,2,-8),(1,6,2),1)
        r.cube('head',(-3,2,-7),(6,6,2),0)
        r.bone('jaw',(0,2,-6),'head');r.cube('jaw',(-4,1,-8),(8,1,2),3)
    else:
        r.cube('head',(-3,2,-7),(6,4,2),1)
        r.cube('head',(-2,4,-8),(4,1,1),2)
        r.cube('head',(-3.25,4,-7.25),(1,1,1),0);r.cube('head',(2.25,4,-7.25),(1,1,1),0)
        r.bone('jaw',(0,2,-6),'head');r.cube('jaw',(-3,1,-7),(6,1,2),3)
        r.bone('tongue',(0,2,-7),'jaw')
        r.cube('tongue',(-1,1.75,-9),(1,.25,2),0);r.cube('tongue',(.25,1.75,-9),(1,.25,2),0)
    return center_long_rig(r)

def locusts():
    r=Rig('locust_swarm');r.bone('root',(0,0,0),None);r.bone('body',(0,8,0))
    positions=[(-6,4,-3),(-2,7,0),(3,5,-4),(6,8,2),(-7,10,3),(-3,13,-2),(1,11,4),(5,14,-1),(-5,6,5),(0,4,6),(7,5,5),(-7,14,-5),(2,8,-6),(6,12,-5)]
    for i,(x,y,z) in enumerate(positions):
        b=r.bone('insect_'+str(i),(x,y,z),'body')
        r.cube(b,(x-1,y,z-1),(2,1,3),1);r.cube(b,(x-1,y,z-2),(2,1,1),2)
        r.cube(b,(x-.25,y,z-3),(.5,1,1),0)
        for side,s in [('left',1),('right',-1)]:
            wing=r.bone('insect_'+str(i)+'_'+side+'_wing',(x+s,y+1,z),b)
            r.cube(wing,(x+(1 if s>0 else -3),y+1,z-1),(2,.5,3),3)
            r.cube(b,(x+(1 if s>0 else -2),y-.5,z),(1,.5,3),0)
    return r.save()

def animations(r):
    clips={}
    for name,length,amp in [('idle',1.8,2),('wander',1.1,7),('hunt',.75,11),('flee',.55,16),('attack',.8,0),('special',1.2,0),('evade',.7,0)]:
        ch={}
        if r.id=='locust_swarm':
            for i in range(14):
                s=1 if i%2 else -1
                ch['insect_'+str(i)]={'position':keys(length,[[0,0,0],[0,s*.75,0],[0,0,0]])}
                for side,side_sign in [('left',1),('right',-1)]:
                    angle=(20 if name=='idle' else 40)*side_sign
                    ch['insect_'+str(i)+'_'+side+'_wing']={'rotation':keys(length,[[0,0,-angle],[0,0,angle],[0,0,-angle]])}
            if name in ['attack','special']:ch['body']={'rotation':keys(length,[[0,0,0],[0,15,0],[0,-15,0],[0,0,0]])}
        else:
            for i in range(1,7):
                a=amp*(1 if i%2 else -1)
                ch['segment_'+str(i)]={'rotation':keys(length,[[0,a,0],[0,-a,0],[0,a,0]])}
            ch['head']={'rotation':keys(length,[[0,-amp/3,0],[0,amp/3,0],[0,-amp/3,0]])}
            if name in ['attack','special']:
                ch['neck']={'rotation':keys(length,[[0,0,0],[-20,0,0],[20,0,0],[0,0,0]])}
                ch['jaw']={'rotation':keys(length,[[0,0,0],[35,0,0],[0,0,0]])}
                if r.id=='stone_worm':ch['body']={'position':keys(length,[[0,0,0],[0,2,0],[0,0,0]])}
            if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,12,0],[0,0,0]])}
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        clips[name]=json.loads(json.dumps(clips['evade' if name in ['return_water','side_charge','circle','burrow'] else 'special']))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for r in [crawler('giant_python'),crawler('stone_worm',stone=True),locusts()]:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    from pixel16 import export
    export();print('Generated two segmented crawlers and fourteen locusts')

if __name__=='__main__':main()
