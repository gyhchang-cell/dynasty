"""Original low-spec cuboid rigs, dedicated pixel atlases and GeckoLib 4 clips.

Run from any directory. No copied mod art, smooth primitives or image resampling.
Editable geo/animation JSON is directly importable in Blockbench's GeckoLib format.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
ASSET = REPO / 'src/main/resources/assets/dynasty'
OUT = REPO / 'docs/art/secondary-cuboid-v1'
IDS = ['river_imp', 'tree_spirit', 'shrimp_soldier']
PALETTES = {
    'river_imp': ['#243b36', '#507b51', '#a5bc70', '#e8d4a1'],
    'tree_spirit': ['#302c25', '#75553b', '#a78452', '#77904c'],
    'shrimp_soldier': ['#352c37', '#944b48', '#ce865c', '#e8d6a1'],
}


def texture(id):
    im = Image.new('RGB', (128, 128), PALETTES[id][0])
    d = ImageDraw.Draw(im)
    # Eight reusable 32px tiles, with 1 texture pixel per geometry unit.
    for i in range(4):
        d.rectangle((i*32, 0, i*32+31, 31), fill=PALETTES[id][i])
    for tile, (base, accent) in enumerate([(1, 2), (0, 1), (2, 3), (1, 0)], 4):
        x=(tile%4)*32; y=(tile//4)*32
        d.rectangle((x,y,x+31,y+31),fill=PALETTES[id][base])
        if id == 'tree_spirit':
            for offset in [2,10,18,26]:
                d.rectangle((x+offset,y,x+offset+1,y+31),fill=PALETTES[id][accent])
        else:
            for offset in [0,8,16,24]:
                d.rectangle((x,y+offset,x+31,y+offset+1),fill=PALETTES[id][accent])
    path=ASSET/f'textures/entity/secondary/{id}.png'
    path.parent.mkdir(parents=True,exist_ok=True);im.save(path)


class Rig:
    def __init__(self,id): self.id=id;self.bones=[];self.by={}
    def bone(self,name,pivot,parent='root'):
        b={'name':name,'pivot':list(pivot)}
        if parent: b['parent']=parent
        self.bones.append(b);self.by[name]=b
        return name
    def cube(self,bone,origin,size,material=1,name=None):
        # Each cuboid face maps to an explicit hard-edge tile; UV never touches
        # unrelated parts of a borrowed large-creature texture.
        tile=material; u=(tile%4)*32;v=(tile//4)*32
        x,y,z=size
        dims={'north':(x,y),'south':(x,y),'east':(z,y),'west':(z,y),'up':(x,z),'down':(x,z)}
        uv={f:{'uv':[u,v],'uv_size':list(dim)} for f,dim in dims.items()}
        c={'origin':list(origin),'size':list(size),'uv':uv}
        self.by[bone].setdefault('cubes',[]).append(c)
    def save(self):
        texture(self.id)
        description={'identifier':'geometry.secondary.'+self.id,
                     'texture_width':128,'texture_height':128,
                     'visible_bounds_width':4,'visible_bounds_height':4,
                     'visible_bounds_offset':[0,1.1,0]}
        geo={'format_version':'1.12.0','minecraft:geometry':[
            {'description':description,'bones':self.bones}]}
        path=ASSET/f'geo/secondary/{self.id}.geo.json'
        path.write_text(json.dumps(geo,indent=2)+'\n')
        return self


def river():
    r=Rig('river_imp');r.bone('root',(0,0,0),None)
    r.bone('body',(0,7,0));r.cube('body',(-3,6,-2),(6,5,4),1)
    r.bone('pelvis',(0,5,0),'body');r.cube('pelvis',(-3,4,-1),(6,2,4),2)
    r.bone('shell',(0,8,2),'body')
    r.cube('shell',(-4,5,2),(8,8,2),0);r.cube('shell',(-3,6,4),(6,6,2),4)
    r.cube('shell',(-2,7,6),(4,4,1),1)
    r.bone('neck',(0,11,0),'body');r.cube('neck',(-2,11,-2),(4,1,4),2)
    r.bone('head',(0,12,0),'neck');r.cube('head',(-2,12,-3),(4,4,5),1)
    r.cube('head',(-4,13,-3),(2,3,3),2);r.cube('head',(2,13,-3),(2,3,3),2)
    r.cube('head',(-3,13,-4),(2,2,1),0);r.cube('head',(1,13,-4),(2,2,1),0)
    r.bone('jaw',(0,12,-2),'head');r.cube('jaw',(-2,11,-5),(4,2,2),3)
    r.cube('jaw',(-1,11,-6),(2,1,1),2)
    r.bone('dish',(0,16,0),'head')
    r.cube('dish',(-3,16,-3),(1,1,6),2);r.cube('dish',(2,16,-3),(1,1,6),2)
    r.cube('dish',(-2,16,-3),(4,1,1),2);r.cube('dish',(-2,16,2),(4,1,1),2)
    r.cube('dish',(-2,16,-2),(4,.5,4),0)
    for side,x in [('left',3),('right',-3)]:
        b=r.bone(side+'_fin',(x,10,0),'body')
        r.cube(b,((3 if x>0 else -5),7,-1),(2,3,2),1)
        fore=r.bone(side+'_forearm',(x+(1 if x>0 else -1),6,0),b)
        r.cube(fore,((3 if x>0 else -5),5,-2),(2,2,2),2)
        hand=r.bone(side+'_hand',(x,4,-1),fore)
        r.cube(hand,((3 if x>0 else -6),3,-3),(3,2,3),1)
        leg=r.bone(side+'_thigh',((2 if x>0 else -2),5,1),'pelvis')
        r.cube(leg,((1 if x>0 else -3),2,0),(2,2,3),1)
        foot=r.bone(side+'_foot',((2 if x>0 else -2),2,0),leg)
        r.cube(foot,((0 if x>0 else -4),0,-3),(4,2,5),2)
        r.cube(foot,((1 if x>0 else -3),0,-4),(2,1,1),1)
    r.bone('tail',(0,5,3),'pelvis');r.cube('tail',(-1,3,4),(2,2,3),1)
    return r.save()


def tree():
    r=Rig('tree_spirit');r.bone('root',(0,0,0),None)
    r.bone('body',(0,10,0));r.cube('body',(-5,5,-4),(10,18,8),4)
    r.cube('body',(-4,23,-3),(8,2,6),2)
    r.cube('body',(-3,8,-5),(6,10,1),1)
    # Hollow knot mask embedded in the trunk, without a quadruped muzzle.
    r.bone('neck',(0,19,-2),'body');r.bone('head',(0,21,-4),'neck')
    r.cube('head',(-4,19,-5),(8,6,2),2)
    r.cube('head',(-3,21,-6),(2,2,1),0);r.cube('head',(1,21,-6),(2,2,1),0)
    r.cube('head',(-2,19,-6),(4,2,1),0)
    r.cube('head',(-1,21,-7),(2,2,1),1)
    # Four root supports retain old animation anchors but form a stump skeleton.
    for i,(x,z) in enumerate([(-4,-2),(4,-2),(-4,2),(4,2)]):
        b=r.bone('leg_'+str(i),(x,7,z),'body')
        r.cube(b,(x-2,2,z-2),(4,3,4),1)
        foot=r.bone('foot_'+str(i),(x,2,z),b)
        ox=-9 if x<0 else 4;oz=-5 if z<0 else 1
        r.cube(foot,(ox,0,oz),(5,3,4),7)
    r.bone('tail',(0,6,4),'body');r.cube('tail',(-2,1,4),(4,4,3),1)
    for side,s in [('left',1),('right',-1)]:
        b=r.bone(side+'_branch',(s*5,20,0),'body')
        r.cube(b,((5 if s>0 else -8),16,-1),(3,6,3),4)
        hand=r.bone(side+'_twig',(s*7,16,0),b)
        r.cube(hand,((6 if s>0 else -9),10,-2),(3,6,3),1)
        r.cube(hand,((7 if s>0 else -10),8,-3),(3,3,4),2)
        r.cube(hand,((9 if s>0 else -11),7,-3),(2,3,2),1)
    for i,(x,z,height) in enumerate([(-4,-1,10),(-1,2,7),(2,-1,9),(3,3,5)]):
        b=r.bone('branch_'+str(i),(x,24,z),'body')
        r.cube(b,(x-1,24,z-1),(2,height,2),1)
        ox=x-3 if i%2==0 else x+1
        r.cube(b,(ox,26,z-1),(4,2,2),1)
        r.cube(b,(ox,28,z-1),(2,3,2),2)
        if i in [0,2]:r.cube(b,(x-2,30,z-2),(4,2,4),3)
    r.cube('body',(-5,12,4),(4,4,1),3)
    return r.save()


def shrimp():
    r=Rig('shrimp_soldier');r.bone('root',(0,0,0),None)
    r.bone('body',(0,8,0));r.cube('body',(-3,5,-2),(6,7,5),1)
    r.bone('carapace',(0,9,2),'body');r.cube('carapace',(-4,7,1),(8,6,3),4)
    r.cube('carapace',(-3,13,1),(6,1,3),2)
    r.bone('head',(0,13,0),'body');r.cube('head',(-3,12,-3),(6,5,5),1)
    r.cube('head',(-4,14,-4),(1,2,2),0);r.cube('head',(3,14,-4),(1,2,2),0)
    r.cube('head',(-1,14,-5),(2,2,3),2);r.cube('head',(-1,15,-7),(2,1,2),3)
    for side,s in [('left',1),('right',-1)]:
        ant=r.bone(side+'_antenna',(s*2,17,-2),'head')
        r.cube(ant,((2 if s>0 else -4),16,-4),(2,3,2),2)
        r.cube(ant,((3 if s>0 else -5),18,-6),(2,2,4),3)
        shoulder=r.bone(side+'_fin',(s*3,11,0),'body')
        r.cube(shoulder,((3 if s>0 else -6),8,-1),(3,4,3),4)
        fore=r.bone(side+'_forearm',(s*5,8,-1),shoulder)
        r.cube(fore,((4 if s>0 else -6),6,-2),(2,3,3),1)
        grip=r.bone(side+'_grip',(s*5,7,-3),fore)
        r.cube(grip,((3 if s>0 else -7),6,-5),(4,2,3),2)
        r.cube(grip,((4 if s>0 else -5),8,-5),(1,2,2),3)
        r.cube(grip,((6 if s>0 else -7),8,-5),(1,2,2),3)
    r.bone('spear',(5,7,-4),'left_grip')
    r.cube('spear',(4,1,-4.5),(2,15,2),0)
    r.cube('spear',(3,16,-4),(4,2,2),2)
    r.cube('spear',(4,18,-4),(2,2,2),3)
    r.bone('tail',(0,6,2),'body');r.cube('tail',(-3,3,2),(6,3,4),4)
    parent='tail'
    for i,(y,z,w) in enumerate([(2,5,6),(1,7,4),(0,9,4),(0,11,6)],1):
        b=r.bone('tail_'+str(i),(0,y+2,z),parent)
        r.cube(b,(-w/2,y,z),(w,2,3),4 if i<4 else 2);parent=b
    r.bone('tail_fan',(0,1,12),'tail_4')
    r.cube('tail_fan',(-4,0,12),(8,1,3),2)
    for side,s in [('left',1),('right',-1)]:
        for i in range(3):
            b=r.bone(side+'_swimmer_'+str(i),(s*2,5,1+i*2),'body' if i==0 else 'tail')
            r.cube(b,((2 if s>0 else -4),2,1+i*2),(2,3,2),1)
            r.cube(b,((3 if s>0 else -5),1,i*2),(2,1,3),3)
    return r.save()


def keys(length,values):
    # Explicit numeric linear keyframes: portable GeckoLib 4 / Blockbench export.
    return {str(round(i*length/(len(values)-1),4)):v for i,v in enumerate(values)}


def clips(r):
    all_clips={}
    for name,length,amp in [('idle',1.6,2),('wander',.9,12),('hunt',.65,20),
                            ('flee',.5,26),('attack',.6,0),('special',1.0,0),('evade',.6,0)]:
        ch={'body':{'rotation':keys(length,[[0,0,-1],[0,0,1],[0,0,-1]])}}
        if r.id=='river_imp':
            for side,s in [('left',1),('right',-1)]:
                ch[side+'_fin']={'rotation':keys(length,[[amp*s,0,0],[-amp*s,0,0],[amp*s,0,0]])}
                ch[side+'_thigh']={'rotation':keys(length,[[-amp*s,0,0],[amp*s,0,0],[-amp*s,0,0]])}
            ch['head']={'rotation':keys(length,[[0,-amp/3,0],[0,amp/3,0],[0,-amp/3,0]])}
            if name in ['attack','special']:
                for side in ['left','right']:
                    ch[side+'_fin']={'rotation':keys(length,[[0,0,0],[45,0,0],[-40,0,0],[0,0,0]])}
                    ch[side+'_forearm']={'rotation':keys(length,[[0,0,0],[-20,0,0],[35,0,0],[0,0,0]])}
                ch['jaw']={'rotation':keys(length,[[0,0,0],[12,0,0],[0,0,0]])}
            if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[15,0,18],[0,0,0]])}
        elif r.id=='tree_spirit':
            for i in range(4):
                s=1 if i in [0,3] else -1
                ch['leg_'+str(i)]={'rotation':keys(length,[[amp*s/2,0,0],[-amp*s/2,0,0],[amp*s/2,0,0]])}
            for side,s in [('left',1),('right',-1)]:
                ch[side+'_branch']={'rotation':keys(length,[[amp*s/3,0,0],[-amp*s/3,0,0],[amp*s/3,0,0]])}
            for i in range(4):ch['branch_'+str(i)]={'rotation':keys(length,[[0,0,-2],[0,0,2],[0,0,-2]])}
            if name in ['attack','special']:
                for side in ['left','right']:
                    ch[side+'_branch']={'rotation':keys(length,[[0,0,0],[65,0,0],[-30,0,0],[0,0,0]])}
                    ch[side+'_twig']={'rotation':keys(length,[[0,0,0],[20,0,0],[-20,0,0],[0,0,0]])}
                ch['body']={'rotation':keys(length,[[0,0,0],[-8,0,0],[12,0,0],[0,0,0]])}
            if name=='evade':ch['body']={'rotation':keys(length,[[0,0,0],[0,0,12],[0,0,0]])}
        else:
            for i in range(1,5):ch['tail_'+str(i)]={'rotation':keys(length,[[amp/4,0,0],[-amp/4,0,0],[amp/4,0,0]])}
            for side,s in [('left',1),('right',-1)]:
                ch[side+'_antenna']={'rotation':keys(length,[[0,0,-3*s],[0,0,3*s],[0,0,-3*s]])}
                for i in range(3):ch[side+'_swimmer_'+str(i)]={'rotation':keys(length,[[amp*s,0,0],[-amp*s,0,0],[amp*s,0,0]])}
            if name in ['attack','special']:
                ch['left_fin']={'rotation':keys(length,[[0,0,0],[-20,0,0],[80,0,0],[0,0,0]])}
                ch['left_forearm']={'rotation':keys(length,[[0,0,0],[15,0,0],[5,0,0],[0,0,0]])}
                ch['body']={'rotation':keys(length,[[0,0,0],[-8,0,0],[12,0,0],[0,0,0]])}
            if name=='evade':
                for i in range(1,5):ch['tail_'+str(i)]={'rotation':keys(length,[[0,0,0],[25,0,0],[0,0,0]])}
        all_clips[name]={'loop':True,'animation_length':length,'bones':ch}
    # Retain the existing controller's named skill contract without changing AI.
    for name in ['pounce','coil','stalk','dive','circle','burrow','eruption','pinch',
                 'sting','possession','return_water','side_charge']:
        source='evade' if name in ['return_water','side_charge','burrow','dive','circle'] else 'special'
        all_clips[name]=json.loads(json.dumps(all_clips[source]))
    path=ASSET/f'animations/secondary/{r.id}.animation.json'
    path.write_text(json.dumps({'format_version':'1.8.0','animations':all_clips},indent=2)+'\n')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rigs=[river(),tree(),shrimp()]
    manifest=json.loads((OUT/'model-manifest.json').read_text()) if (OUT/'model-manifest.json').exists() else {}
    for r in rigs:
        clips(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),
                                 'palette':PALETTES[r.id],'atlas':[128,128],'geometry':'1.12.0','animations':'1.8.0'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
