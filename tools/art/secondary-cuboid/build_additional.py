"""Second group: fish, snail hybrid, hanging lantern and low stone creature."""
import json
from build_models import Rig, PALETTES, ASSET, OUT, keys

PALETTES.update({
    'carp_spirit':['#352f32','#a54b3d','#d9a75b','#eee1b8'],
    'snail_maiden':['#293930','#6b9271','#b49162','#ebd9ae'],
    'lantern_ghost':['#342b2b','#84573d','#d7a84f','#eee0b1'],
    'stone_sprite':['#30353a','#646d73','#9ea590','#d4b96e'],
})


def carp():
    r=Rig('carp_spirit');r.bone('root',(0,0,0),None);r.bone('body',(0,8,0))
    r.cube('body',(-3,5,-6),(6,6,12),4);r.cube('body',(-2,11,-3),(4,1,8),2)
    r.bone('neck',(0,8,-6),'body');r.bone('head',(0,8,-6),'neck')
    r.cube('head',(-3,6,-10),(6,4,4),3)
    r.cube('head',(-4,8,-9),(1,2,2),0);r.cube('head',(3,8,-9),(1,2,2),0)
    r.bone('jaw',(0,6,-9),'head');r.cube('jaw',(-2,6,-11),(4,1,1),1)
    r.cube('head',(-3,6,-12),(1,2,2),2);r.cube('head',(2,6,-12),(1,2,2),2)
    r.bone('dorsal',(0,11,0),'body');r.cube('dorsal',(-1,12,-1),(2,3,6),1)
    for side,s in [('left',1),('right',-1)]:
        b=r.bone(side+'_fin',(s*3,7,0),'body')
        r.cube(b,((3 if s>0 else -6),6,-1),(3,1,6),2)
    r.bone('tail',(0,8,6),'body');r.cube('tail',(-2,6,6),(4,4,3),1)
    r.bone('tail_tip',(0,8,9),'tail');r.cube('tail_tip',(-1,6,9),(2,3,2),2)
    r.bone('tail_fan',(0,8,11),'tail_tip');r.cube('tail_fan',(-1,6,11),(2,3,2),1)
    r.cube('tail_fan',(-1,3,12),(2,3,2),2);r.cube('tail_fan',(-1,9,12),(2,4,2),2)
    r.bone('belly_fin',(0,5,0),'body');r.cube('belly_fin',(-1,3,-2),(2,2,4),2)
    return r.save()


def snail():
    r=Rig('snail_maiden');r.bone('root',(0,0,0),None);r.bone('body',(0,4,0))
    r.cube('body',(-4,0,-4),(8,2,10),1);r.cube('body',(-3,2,-3),(6,2,8),3)
    r.bone('tail',(0,2,5),'body');r.cube('tail',(-3,0,6),(6,2,4),1)
    r.bone('pelvis',(0,4,0),'body');r.cube('pelvis',(-3,4,-2),(6,3,4),1)
    r.bone('waist',(0,7,0),'pelvis');r.cube('waist',(-1,7,-1),(2,2,2),2)
    r.bone('chest',(0,9,0),'waist');r.cube('chest',(-2,9,-2),(4,3,3),1)
    r.bone('neck',(0,12,0),'chest');r.cube('neck',(-1,12,-1),(2,1,2),3)
    r.bone('head',(0,13,0),'neck');r.cube('head',(-2,13,-2),(4,4,4),3)
    r.cube('head',(-2,14,-3),(1,1,1),0);r.cube('head',(1,14,-3),(1,1,1),0)
    r.bone('hair',(0,15,1),'head');r.cube('hair',(-2,17,-2),(4,.5,4),0)
    r.cube('hair',(-2,13,2),(4,4.5,1),0)
    for side,s in [('left',1),('right',-1)]:
        b=r.bone(side+'_fin',(s*2,11,0),'chest')
        r.cube(b,((2 if s>0 else -4),8,-1),(2,4,2),1)
        hand=r.bone(side+'_hand',(s*3,8,0),b)
        r.cube(hand,((2 if s>0 else -4),6,-1),(2,2,2),3)
    r.bone('shell',(0,6,3),'body');r.cube('shell',(-4,3,3),(8,9,3),0)
    r.cube('shell',(-3,4,6),(6,7,2),2);r.cube('shell',(-2,5,8),(4,5,1),3)
    r.cube('shell',(-1,6,9),(2,3,1),2)
    return r.save()


def lantern():
    r=Rig('lantern_ghost');r.bone('root',(0,0,0),None);r.bone('body',(0,10,0))
    r.cube('body',(-4,5,-4),(8,1,8),1)
    for x in [-4,2]:
        for z in [-4,2]:r.cube('body',(x,6,z),(2,9,2),1)
    r.bone('head',(0,15,0),'body');r.cube('head',(-4,15,-4),(8,1,8),0)
    r.cube('head',(-3,16,-3),(6,2,6),1)
    r.bone('hanger',(0,18,0),'head');r.cube('hanger',(-1,18,-1),(2,3,2),0)
    r.bone('ribs',(0,14,0),'body')
    for side,origin,size,pivot in [
        ('front',(-2,6,-4),(4,9,1),(0,14,-4)),
        ('back',(-2,6,3),(4,9,1),(0,14,4)),
        ('left',(3,6,-2),(1,9,4),(4,14,0)),
        ('right',(-4,6,-2),(1,9,4),(-4,14,0))]:
        b=r.bone('paper_'+side,pivot,'ribs');r.cube(b,origin,size,3)
        if side=='front':
            r.cube(b,(-2,11,-5),(1,2,1),0);r.cube(b,(1,11,-5),(1,2,1),0)
            r.cube(b,(-1,8,-5),(2,1,1),2)
    r.bone('tail',(0,5,0),'body');r.cube('tail',(-1,3,-1),(2,2,2),2)
    r.bone('tassel',(0,3,0),'tail');r.cube('tassel',(-1,0,-1),(2,3,2),1)
    for i,(x,z) in enumerate([(-3,-3),(3,-3),(-3,3),(3,3)]):
        b=r.bone('cord_'+str(i),(x,5,z),'tail');r.cube(b,(x-1,1,z-1),(2,4,2),2)
    return r.save()


def stone():
    r=Rig('stone_sprite');r.bone('root',(0,0,0),None);r.bone('body',(0,6,0))
    r.cube('body',(-5,4,-4),(10,6,8),1)
    r.bone('boulder',(0,10,0),'body');r.cube('boulder',(-4,10,-3),(8,3,6),2)
    r.cube('boulder',(-1,13,-1),(4,.5,3),1)
    r.bone('neck',(0,8,-3),'body');r.bone('head',(0,8,-4),'neck')
    r.cube('head',(-4,6,-5),(8,4,1),2)
    r.cube('head',(-3,8,-6),(2,1,1),0);r.cube('head',(1,8,-6),(2,1,1),0)
    r.cube('head',(-3,7,-6),(2,1,1),3);r.cube('head',(1,7,-6),(2,1,1),3)
    r.bone('tail',(0,6,4),'body');r.cube('tail',(-2,4,4),(4,3,2),1)
    for i,(x,z) in enumerate([(-3,-2),(3,-2),(-3,2),(3,2)]):
        b=r.bone('leg_'+str(i),(x,4,z),'body');r.cube(b,(x-1,2,z-1),(2,2,2),0)
        foot=r.bone('foot_'+str(i),(x,2,z),b);r.cube(foot,(x-2,0,z-2),(4,2,4),2)
    return r.save()


def animations(r):
    clips={}
    for name,length,amp in [('idle',1.6,3),('wander',1.0,12),('hunt',.7,18),
                            ('flee',.5,25),('attack',.7,10),('special',1.0,14),('evade',.6,10)]:
        ch={}
        def wave(b,axis,amount):
            a=[0,0,0];a[axis]=amount;c=[0,0,0];c[axis]=-amount
            ch[b]={'rotation':keys(length,[a,c,a])}
        if r.id=='carp_spirit':
            wave('tail',1,amp);wave('tail_tip',1,-amp*.65)
            wave('left_fin',2,amp);wave('right_fin',2,-amp)
            if name in ['attack','special']:wave('jaw',0,12);wave('neck',1,15)
        elif r.id=='snail_maiden':
            wave('left_fin',0,amp/3);wave('right_fin',0,-amp/3);wave('tail',1,amp/4)
            if name in ['attack','special','evade']:
                ch['waist']={'rotation':keys(length,[[0,0,0],[30,0,0],[0,0,0]])}
                ch['head']={'rotation':keys(length,[[0,0,0],[15,0,0],[0,0,0]])}
                ch['shell']={'rotation':keys(length,[[0,0,0],[-10,0,0],[0,0,0]])}
        elif r.id=='lantern_ghost':
            wave('body',2,amp/3);wave('tail',2,-amp/2)
            for i in range(4):wave('cord_'+str(i),0,amp*(1 if i%2 else -1))
            if name in ['attack','special']:
                for side in ['front','back']:wave('paper_'+side,0,35 if side=='front' else -35)
                for side in ['left','right']:wave('paper_'+side,2,35 if side=='left' else -35)
        else:
            for i in range(4):wave('leg_'+str(i),0,amp*(1 if i in [0,3] else -1)/2)
            wave('boulder',2,amp/5)
            if name in ['attack','special']:wave('body',0,12);wave('head',0,-8)
        clips[name]={'loop':True,'animation_length':length,'bones':ch}
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch','sting','possession','return_water','side_charge']:
        clips[name]=json.loads(json.dumps(clips['evade' if name in ['return_water','burrow','side_charge'] else 'special']))
    (ASSET/f'animations/secondary/{r.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')


def main():
    rigs=[carp(),snail(),lantern(),stone()]
    path=OUT/'model-manifest.json';manifest=json.loads(path.read_text()) if path.exists() else {}
    for r in rigs:
        animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),
                                     'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    path.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({r.id:manifest[r.id] for r in rigs},indent=2))


if __name__=='__main__':main()
