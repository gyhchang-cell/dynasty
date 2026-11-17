"""Original, editable Cuboid art. Only the three named resource contracts are changed.

The tiny atlas is also a front-facing 16-pixel portrait: seven 2x2 cells with
one white pixel around the edge. Cuboid faces reuse its solid colour islands.
No combat source, gameplay timings, entity dimensions or third-party art.
"""
import base64
import json
import uuid
from pathlib import Path
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
ASSETS = REPO / 'src/main/resources/assets/dynasty'
OUT = REPO / 'docs/art/cod2-voxel-v1'
IDS = ['jubi_shigandang', 'juli_bixi_kuilei', 'tongbi_feitian_yecha']
PALETTES = [
    ['#ffffff', '#747e70', '#283b35', '#b99954'],
    ['#ffffff', '#899080', '#30433a', '#b39954'],
    ['#ffffff', '#292d36', '#6b9980', '#bd8a45'],
]
PORTRAITS = [
    ['..111..', '..121..', '.111133', '..12133', '..11133', '..1..33', '.11..33'],
    ['..333..', '..323..', '.11111.', '1121211', '1111111', '.2...2.', '.11.11.'],
    ['..323..', '1.333.1', '1113111', '.1.323.', '..1333.', '..1.33.', '..1.33.'],
]


class Rig:
    def __init__(self, name, palette, portrait):
        self.name, self.bones, self.animations = name, [], {}
        self.image = Image.new('RGB', (16, 16), palette[0])
        draw = ImageDraw.Draw(self.image)
        self.islands = {}
        for y, row in enumerate(portrait):
            for x, value in enumerate(row):
                if value == '.': continue
                color = int(value)
                draw.rectangle((1+x*2, 1+y*2, 2+x*2, 2+y*2), fill=palette[color])
                self.islands.setdefault(color, [1+x*2, 1+y*2])

    def bone(self, name, parent, pivot, cubes=(), rotation=None):
        b = dict(name=name, pivot=pivot)
        if parent: b['parent'] = parent
        if cubes: b['cubes'] = list(cubes)
        if rotation: b['rotation'] = rotation
        self.bones.append(b)
        return b

    def cube(self, origin, size, material=1, faces=None):
        uv = {f: {'uv': self.islands[(faces or {}).get(f, material)], 'uv_size': [2, 2]}
              for f in ['north', 'south', 'east', 'west', 'up', 'down']}
        result=dict(origin=origin, size=size, uv=uv)
        # Tiny separation prevents coplanar armour/scute surfaces flickering.
        if material > 1: result['inflate'] = .02*(material-1)
        return result

    def clip(self, name, ticks, channels, loop=False):
        self.animations['animation.'+self.name+'.'+name] = dict(
            loop=loop, animation_length=ticks/20, bones=channels)

    def save(self):
        geo = {'format_version': '1.12.0', 'minecraft:geometry': [{
            'description': dict(identifier='geometry.'+self.name, texture_width=16,
                texture_height=16, visible_bounds_width=8, visible_bounds_height=6,
                visible_bounds_offset=[0, 1.4, 0]), 'bones': self.bones}]}
        from species_materials import finish
        self.image = finish(self.name, geo, self.image)
        anim = {'format_version': '1.8.0', 'animations': self.animations}
        baseline = OUT/'source'/self.name
        original = json.loads((baseline/'original.animation.json').read_text())
        assert set(original['animations']) == set(self.animations), 'Preserve controller clip IDs'
        for key in self.animations:
            assert self.animations[key]['animation_length'] == original['animations'][key]['animation_length'], key
        from resource_paths import resource_paths
        gp,ap,tex=resource_paths(self.name)
        for path, data in [(gp, geo), (ap, anim)]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2)+'\n')
        tex.parent.mkdir(parents=True, exist_ok=True); self.image.save(tex)
        self.image.resize((512, 512), Image.Resampling.NEAREST).save(OUT/(self.name+'-texture.png'))
        self.bbmodel(tex)

    def bbmodel(self, texture):
        """Blockbench's project coordinates mirror exported Bedrock X and X/Y angles."""
        groups, elements = {}, []
        namespace = uuid.UUID('2f058c40-6922-4ac9-a87f-186a1e609588')
        uid = lambda label: str(uuid.uuid5(namespace, self.name+'/'+label))
        for bone in self.bones:
            pivot=bone['pivot']; rotation=bone.get('rotation',[0,0,0])
            group=dict(name=bone['name'], type='group', origin=[-pivot[0],pivot[1],pivot[2]],
                rotation=[-rotation[0],-rotation[1],rotation[2]], uuid=uid(bone['name']),
                export=True, isOpen=True, children=[])
            groups[bone['name']]=group
            for i,cube in enumerate(bone.get('cubes',[])):
                x,y,z=cube['origin']; w,h,d=cube['size']; key=uid(bone['name']+'/'+str(i))
                faces={}
                for face, uv in cube['uv'].items():
                    u,v=uv['uv'];du,dv=uv['uv_size']
                    faces[face]=dict(uv=[u+du,v+dv,u,v] if face in ['up','down'] else [u,v,u+du,v+dv],texture=0)
                elements.append(dict(name=bone['name']+'_'+str(i),type='cube',uuid=key,
                    **{'from':[-x-w,y,z], 'to':[-x,y+h,z+d]},
                    origin=group['origin'],rotation=[0,0,0],inflate=cube.get('inflate',0),box_uv=False,faces=faces))
                group['children'].append(key)
        roots=[]
        for bone in self.bones:
            if bone.get('parent'): groups[bone['parent']]['children'].append(groups[bone['name']])
            else: roots.append(groups[bone['name']])
        data=dict(meta=dict(format_version='4.10',model_format='geckolib_model',box_uv=False),
            name=self.name,model_identifier=self.name,geckolib_modid='dynasty',
            resolution=dict(width=self.image.width,height=self.image.height),elements=elements,outliner=roots,
            textures=[dict(path=str(texture),name=texture.name,id='0',uuid=uid('texture'),
                width=16,height=16,uv_width=16,uv_height=16,
                source='data:image/png;base64,'+base64.b64encode(texture.read_bytes()).decode())])
        # Authoring animation JSON is preserved alongside the project, importable in Animation mode.
        dest=OUT/'blockbench';dest.mkdir(exist_ok=True)
        (dest/(self.name+'.bbmodel')).write_text(json.dumps(data,indent=2)+'\n')


def track(channel, frames):
    return {channel: {str(t/20): value for t,value in frames}}


def stone(r):
    c,b=r.cube,r.bone
    b('root',None,[0,0,0])
    b('foot','root',[0,5,0],[c([-4,0,-5],[8,3,10],2),c([-3,3,-3],[6,9,7]),c([-4,9,-4],[8,2,9],3)])
    b('body','root',[0,14,0],[c([-6,11,-5],[12,7,10]),c([-7,11,-6],[14,2,12],2)])
    b('waist','body',[0,18,0],[c([-4,18,-4],[8,5,8],2),c([-5,20,-5],[10,2,10],3)])
    b('chest','waist',[0,23,0],[c([-7,22,-5],[14,9,10]),c([-8,27,-6],[16,4,12]),c([-5,23,-7],[10,5,2],2),c([-5,23,5],[10,5,2],2)])
    b('neck','chest',[0,31,0],[c([-3,30,-3],[6,3,6],2)])
    b('head','neck',[0,32,0],[c([-5,32,-4],[10,5,9]),c([-6,36,-5],[12,2,10]),c([-6,32,-4],[2,3,8],3),c([4,32,-4],[2,3,8],3)])
    b('face','head',[0,34,-4],[c([-4,34,-5],[3,2,1],2),c([1,34,-5],[3,2,1],2),c([-2,32,-5],[4,2,1],3)])
    b('left_stump','chest',[7,28,0],[c([7,24,-3],[4,6,6]),c([7,28,-4],[5,2,8],3)])
    b('right_shoulder','chest',[-7,28,0],[c([-15,23,-5],[9,9,10]),c([-16,28,-6],[10,3,12],3)])
    b('right_upper','right_shoulder',[-12,24,0],[c([-15,16,-4],[7,9,8]),c([-16,19,-5],[9,3,10],2)])
    b('right_elbow','right_upper',[-12,16,0],[c([-17,10,-5],[10,7,10]),c([-18,13,-6],[12,2,12],3)])
    b('right_fist','right_elbow',[-12,9,0],[c([-19,1,-7],[14,9,14]),c([-20,7,-8],[16,3,16],2),c([-18,3,-9],[4,4,2]),c([-12,3,-9],[4,4,2]),c([-20,3,-3],[2,4,5],3)])
    for i in range(4):
        x=-5-i*2;y=29-i*2
        b('chain_'+str(i),'chest' if i==0 else 'chain_'+str(i-1),[x,y,6],
          [c([x-2,y-3,6],[4,1,2],3),c([x-2,y,6],[4,1,2],3),c([x-2,y-2,6],[1,2,2],3),c([x+1,y-2,6],[1,2,2],3)])
    b('inscription','chest',[0,26,-7],[c([-3,26,-8],[6,2,1],3),c([-1,23,-8],[2,3,1],3)])
    r.clip('idle',60,{'chest':track('position',[(0,[0,0,0]),(30,[0,.3,0]),(60,[0,0,0])])},True)
    for name,ticks in [('walk',40),('run',28)]:
        r.clip(name,ticks,{'body':track('rotation',[(0,[0,0,-3]),(ticks/2,[0,0,4]),(ticks,[0,0,-3])]),
            'root':track('position',[(0,[0,0,0]),(ticks/4,[0,.8,0]),(ticks/2,[0,0,0]),(ticks*3/4,[0,.8,0]),(ticks,[0,0,0])]),
            'foot':track('rotation',[(0,[-8,0,0]),(ticks/2,[8,0,0]),(ticks,[-8,0,0])]),
            'right_shoulder':track('rotation',[(0,[0,0,0]),(ticks/2,[0,0,4]),(ticks,[0,0,0])])},True)
    r.clip('attack',40,{'body':track('rotation',[(0,[0,0,0]),(12,[0,-22,-8]),(16,[0,28,5]),(24,[0,22,3]),(40,[0,0,0])]),
        'right_shoulder':track('rotation',[(0,[0,0,0]),(12,[28,0,-12]),(16,[-68,0,8]),(23,[-55,0,6]),(40,[0,0,0])]),
        'right_elbow':track('rotation',[(0,[0,0,0]),(12,[35,0,0]),(16,[-15,0,0]),(40,[0,0,0])])})
    r.clip('slam',60,{'body':track('rotation',[(0,[0,0,0]),(25,[-12,0,-7]),(30,[28,0,6]),(34,[23,0,5]),(60,[0,0,0])]),
        'right_shoulder':track('rotation',[(0,[0,0,0]),(22,[-140,0,-15]),(29,[-140,0,-15]),(30,[12,0,0]),(34,[6,0,0]),(60,[0,0,0])]),
        'right_elbow':track('rotation',[(0,[0,0,0]),(22,[-25,0,0]),(29,[-25,0,0]),(30,[0,0,0]),(60,[0,0,0])])})
    r.clip('hurt',10,{'chest':track('rotation',[(0,[0,0,0]),(2,[-6,0,0]),(10,[0,0,0])])})
    r.clip('death',44,{'body':{**track('rotation',[(0,[0,0,0]),(12,[12,0,0]),(30,[84,0,0]),(44,[84,0,0])]),**track('position',[(0,[0,0,0]),(30,[0,-5,0]),(44,[0,-5,0])])},
        'right_shoulder':track('rotation',[(0,[0,0,0]),(30,[6,0,0]),(44,[6,0,0])]),
        'inscription':track('scale',[(0,[1,1,1]),(18,[1,1,1]),(44,[.05,.05,.05])])})


def bixi(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    b('shell','root',[0,12,0],[c([-14,9,-14],[28,8,28]),c([-16,9,-15],[32,3,30],2),c([-12,17,-12],[24,3,24]),c([-9,20,-10],[18,2,20],3)])
    b('plastron','shell',[0,9,0],[c([-11,7,-11],[22,3,22],2)])
    for s in [-1,1]:
        for z in [-9,-1,7]:
            b(f'scutes_{s}_{z}','shell',[s*11,17,z],[c([s*11-3,16,z-3],[6,3,6],3),c([s*11-2,19,z-2],[4,1,4])])
    b('stele','shell',[0,22,2],[c([-7,22,-1],[14,10,5]),c([-9,22,-2],[18,2,7],3),c([-8,31,-2],[16,3,7],3),c([-3,25,-2],[6,2,1],2),c([-1,24,-2],[2,6,1],2),c([-3,25,4],[6,2,1],2)])
    b('neck_base','shell',[0,12,-13],[c([-4,10,-19],[8,6,7],2),c([-5,13,-18],[10,3,4],3)])
    b('neck_tip','neck_base',[0,12,-18],[c([-3,10,-23],[6,5,6])])
    b('head','neck_tip',[0,13,-22],[c([-5,11,-27],[10,6,8]),c([-4,11,-30],[8,4,4]),c([-6,15,-26],[3,2,6],3),c([3,15,-26],[3,2,6],3),c([-5,17,-23],[2,4,2],2),c([3,17,-23],[2,4,2],2),c([-5,13,-28],[2,2,1],2),c([3,13,-28],[2,2,1],2)])
    b('jaw','head',[0,11,-23],[c([-4,8,-30],[8,3,9],2),c([-3,9,-31],[6,2,1],3)])
    for fore,z in [('front',-10),('rear',10)]:
        for side,s in [('left',1),('right',-1)]:
            x=s*13;name=fore+'_'+side
            b(name+'_hip','shell',[x,12,z],[c([x-3,6,z-3],[6,7,6]),c([x-4,9,z-4],[8,3,8],3)])
            b(name+'_piston',name+'_hip',[x,7,z],[c([x-2,3,z-2],[4,5,4],2)])
            b(name+'_foot',name+'_piston',[x,3,z],[c([x-4,0,z-5],[8,3,10]),c([x-3,0,z-6],[2,2,2],3),c([x+1,0,z-6],[2,2,2],3)])
    b('tail_base','shell',[0,11,14],[c([-3,9,13],[6,4,6],2)])
    b('tail_tip','tail_base',[0,11,18],[c([-2,9,18],[4,3,5]),c([-1,9,23],[2,2,3],3)])
    r.clip('idle',80,{'neck_base':track('rotation',[(0,[0,0,0]),(40,[-3,0,0]),(80,[0,0,0])]),'tail_tip':track('rotation',[(0,[0,-6,0]),(40,[0,6,0]),(80,[0,-6,0])])},True)
    for clip,ticks in [('walk',56),('run',40)]:
        channels={}
        for i,name in enumerate(['front_left','front_right','rear_left','rear_right']):
            sign=1 if i in [0,3] else -1
            channels[name+'_hip']=track('rotation',[(0,[sign*14,0,0]),(ticks/2,[-sign*14,0,0]),(ticks,[sign*14,0,0])])
            channels[name+'_piston']=track('position',[(0,[0,0,0]),(ticks/4,[0,1 if sign==1 else 0,0]),(ticks/2,[0,0,0]),(ticks*3/4,[0,1 if sign==-1 else 0,0]),(ticks,[0,0,0])])
            channels[name+'_foot']=track('rotation',[(0,[-sign*14,0,0]),(ticks/2,[sign*14,0,0]),(ticks,[-sign*14,0,0])])
        r.clip(clip,ticks,channels,True)
    r.clip('attack',46,{'neck_base':track('rotation',[(0,[0,0,0]),(14,[-15,0,0]),(18,[8,0,0]),(46,[0,0,0])]),'neck_tip':track('position',[(0,[0,0,0]),(14,[0,0,2]),(18,[0,0,-3]),(30,[0,0,-2]),(46,[0,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(14,[30,0,0]),(18,[0,0,0]),(46,[0,0,0])])})
    r.clip('stomp',68,{'shell':{**track('rotation',[(0,[0,0,0]),(25,[-14,0,0]),(31,[-14,0,0]),(32,[2,0,0]),(38,[0,0,0]),(68,[0,0,0])]),**track('position',[(0,[0,0,0]),(25,[0,4,0]),(31,[0,4,0]),(32,[0,0,0]),(68,[0,0,0])])},'stele':track('rotation',[(0,[0,0,0]),(32,[0,0,0]),(34,[4,0,0]),(38,[-3,0,0]),(45,[0,0,0]),(68,[0,0,0])])})
    r.clip('hurt',10,{'neck_base':track('rotation',[(0,[0,0,0]),(3,[-8,0,0]),(10,[0,0,0])])})
    r.clip('death',44,{'shell':track('position',[(0,[0,0,0]),(26,[0,-4,0]),(44,[0,-4,0])]),'head':track('rotation',[(0,[0,0,0]),(30,[18,0,0]),(44,[18,0,0])]),**{name+'_hip':track('rotation',[(0,[0,0,0]),(26,[0,0,s*30]),(44,[0,0,s*30])]) for name,s in [('front_left',1),('rear_left',1),('front_right',-1),('rear_right',-1)]},**{name+'_foot':track('rotation',[(0,[0,0,0]),(26,[0,0,-s*30]),(44,[0,0,-s*30])]) for name,s in [('front_left',1),('rear_left',1),('front_right',-1),('rear_right',-1)]}})


def yecha(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    b('torso','root',[0,19,0],[c([-4,14,-3],[8,5,6]),c([-5,16,-4],[10,2,8],3)])
    b('waist','torso',[0,19,0],[c([-3,18,-2],[6,5,4]),c([-4,20,-3],[8,2,6],3)])
    b('chest','waist',[0,23,0],[c([-6,22,-4],[12,8,8]),c([-7,27,-5],[14,3,10],3),c([-4,23,-5],[8,5,1],3),c([-3,24,-6],[6,2,1],2)])
    b('neck','chest',[0,30,0],[c([-2,29,-2],[4,3,4],2)])
    b('head','neck',[0,32,0],[c([-4,31,-4],[8,6,8]),c([-5,35,-5],[10,2,6],3),c([-4,33,-5],[3,2,1],2),c([1,33,-5],[3,2,1],2),c([-3,31,-6],[6,2,2],3),c([-5,36,-1],[2,4,2],3),c([3,36,-1],[2,4,2],3)])
    for side,s in [('left',1),('right',-1)]:
        x=s*3
        b(side+'_thigh','torso',[x,16,0],[c([x-2,8,-3],[4,8,5]),c([x-2,9,-4],[4,3,2],3)])
        b(side+'_shin',side+'_thigh',[x,9,0],[c([x-1,3,0],[2,7,4]),c([x-2,1,-2],[4,3,6],3),c([x-2,0,-4],[2,2,3],2),c([x,0,-4],[2,2,3],2)])
        for i in range(3):
            x=s*(5+i*6); y=28-i*2;lo=min(x,x+s*6)
            b(side+'_wing_'+str(i),'chest' if i==0 else side+'_wing_'+str(i-1),[x,y,4],
                [c([lo,y-1,4],[6,2,2],3),c([lo,y-7,5],[4,6,1]),c([lo+2,y-9,5],[4,6,1])],rotation=[0,0,s*-8])
    b('left_arm','chest',[6,28,0],[c([6,19,-2],[3,9,4],2),c([5,25,-3],[5,4,6],3),c([6,16,-3],[3,4,5],3)])
    for i in range(5):
        y=28-i*4;w=8 if i<2 else 7 if i<4 else 6
        b('giant_arm_'+str(i),'chest' if i==0 else 'giant_arm_'+str(i-1),[-8,y,0],
            [c([-12,y-5,-4],[w,5,8],3),c([-13,y-1,-5],[w+2,2,10]),c([-10,y-4,-5],[3,2,1],2)])
    b('palm','giant_arm_4',[-8,8,0],[c([-12,4,-5],[8,4,10],3),c([-13,5,-6],[2,3,4],2)])
    for i in range(3): b('finger_'+str(i),'palm',[-11+i*3,5,-3],[c([-12+i*3,1,-4],[2,4,3],3),c([-12+i*3,0,-5],[2,2,2],2)])
    # Preserve the established semantic grip/hold locators as identity aliases.
    b('giant_palm','palm',[-8,6,0])
    for i in range(3):b('hook_'+str(i),'finger_'+str(i),[-11+i*3,1,-5])
    def wings(ticks,amp):
        return {side+'_wing_'+str(i):track('rotation',[(0,[0,0,s*-amp]),(ticks/2,[0,0,s*amp]),(ticks,[0,0,s*-amp])]) for side,s in [('left',1),('right',-1)] for i in range(3)}
    lengths=json.loads((OUT/'source'/r.name/'original.animation.json').read_text())['animations']
    for clip in ['idle','walk','run']:
        ticks=lengths['animation.'+r.name+'.'+clip]['animation_length']*20
        r.clip(clip,ticks,{**wings(ticks,5 if clip=='idle' else 18),'torso':track('position',[(0,[0,0,0]),(ticks/2,[0,.8,0]),(ticks,[0,0,0])])},True)
    r.clip('attack',40,{'chest':track('rotation',[(0,[0,0,0]),(12,[0,-20,-8]),(16,[0,30,8]),(40,[0,0,0])]),**{'giant_arm_'+str(i):track('rotation',[(0,[0,0,0]),(12,[i*2+8,0,-4]),(16,[-i*5-8,0,3]),(40,[0,0,0])]) for i in range(5)}})
    grab={}
    for i in range(5):grab['giant_arm_'+str(i)]={**track('rotation',[(0,[0,0,0]),(16,[-18,0,0]),(20,[-18,0,0]),(80,[-18,0,0]),(104,[0,0,0])]),**track('position',[(0,[0,0,0]),(16,[0,0,0]),(20,[0,-1.8,-1]),(80,[0,-1.8,-1]),(104,[0,0,0])])}
    for i in range(3):grab['finger_'+str(i)]=track('rotation',[(0,[0,0,0]),(19,[0,0,0]),(23,[-65,0,0]),(78,[-65,0,0]),(84,[0,0,0]),(104,[0,0,0])])
    r.clip('grab',104,grab)
    r.clip('hurt',10,{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(10,[0,0,0])])})
    r.clip('death',44,{'torso':{**track('rotation',[(0,[0,0,0]),(26,[75,0,0]),(44,[75,0,0])]),**track('position',[(0,[0,0,0]),(26,[0,-11,0]),(44,[0,-11,0])])},**{side+'_wing_'+str(i):track('rotation',[(0,[0,0,0]),(26,[0,0,s*22]),(44,[0,0,s*22])]) for side,s in [('left',1),('right',-1)] for i in range(3)}})


def main():
    rigs=[]
    for name,palette,portrait,builder in zip(IDS,PALETTES,PORTRAITS,[stone,bixi,yecha]):
        rig=Rig(name,palette,portrait);builder(rig);rig.save()
        rigs.append(rig)
        print(name,len(rig.bones),'bones',sum(len(b.get('cubes',[])) for b in rig.bones),'cuboids')
    from contacts import settle
    settle()
    for rig in rigs:
        # Keep the exact animation export next to the editable project.
        animation=ASSETS/f'animations/blueprint/{rig.name}.animation.json'
        (OUT/'blockbench'/(rig.name+'.animation.json')).write_bytes(animation.read_bytes())


if __name__=='__main__':main()
