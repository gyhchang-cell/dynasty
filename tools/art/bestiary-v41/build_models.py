"""Original native ModelPart assets. No external pixels or geometry are imported.

This is the authoritative source for the two layers, their UVs and runtime PNGs.
Coordinates use Minecraft's native model frame: ground y=24, nose towards -Z.
Run with the bundled Python/Pillow. Old gen_beast scripts cannot overwrite these
independent bestiary textures.
"""
from pathlib import Path
import json, math, shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'docs/art/bestiary-v41'
ASSETS = ROOT/'src/main/resources/assets/dynasty'
JAVA = ROOT/'src/main/java/com/dynasty/client/BestiarySpiritLayers.java'


class Model:
    def __init__(self, name):
        self.name=name; self.bones=[]; self.cubes=[]

    def bone(self,name,parent=None,pivot=(0,0,0),rotation=(0,0,0)):
        self.bones.append(dict(name=name,parent=parent,pivot=list(pivot),rotation=list(rotation),cubes=[]))
        return name

    def cube(self,bone,origin,size,material,role='plain'):
        c=dict(origin=list(origin),size=list(size),material=material,role=role)
        next(b for b in self.bones if b['name']==bone)['cubes'].append(c)
        self.cubes.append(c)


def fox():
    m=Model('nine_tailed_fox');m.bone('root',pivot=(0,0,0))
    m.bone('body','root',(0,15,0));m.cube('body',(-4,-3,-6),(8,7,13),'fox','body')
    m.bone('neck','body',(0,-1,-5));m.cube('neck',(-3,-3,-4),(6,6,5),'cream','throat')
    m.bone('head','neck',(0,-2,-3));m.cube('head',(-3.5,-3,-5),(7,6,6),'fox','face')
    m.bone('snout','head',(0,1,-4));m.cube('snout',(-2,-1,-4),(4,3,4),'cream','muzzle')
    for side,s in [('left',1),('right',-1)]:
        m.bone('ear_'+side,'head',(s*2.4,-2.4,-1.5),(0,0,s*.12))
        m.cube('ear_'+side,(-1,-4,-.8),(2,4,2),'fox','ear')
    for i,(name,x,z) in enumerate([('front_left',3,-4),('front_right',-3,-4),('back_left',3,5),('back_right',-3,5)]):
        hind=i>=2
        m.bone('leg_'+name,'body',(x,2,z),(.12 if hind else 0,0,0))
        m.cube('leg_'+name,(-1.5,0,-1.5),(3,4,3),'fox','leg')
        m.bone('ankle_'+name,'leg_'+name,(0,3.5,0),(-.12 if hind else 0,0,0))
        m.cube('ankle_'+name,(-1,0,-1),(2,3,2),'fox','shin')
        m.cube('ankle_'+name,(-1,2.5,-2),(2,1,3),'paw','paw')
    # All nine tails begin inside the rump; each has a genuinely inherited tip.
    for i in range(9):
        n=f'tail{i}';spread=(i-4)*.19
        m.bone(n,'body',((i-4)*.34,-.6+(i%3)*.35,5),(.32+(i%3)*.14,spread,0))
        m.cube(n,(-1.5,-1.5,0),(3,3,8),'fox','tail_root')
        m.bone(n+'_tip',n,(0,0,7),(.23+(i%2)*.06,0,0))
        m.cube(n+'_tip',(-1.5,-1.5,0),(3,3,8),'fox','tail')
        m.cube(n+'_tip',(-1,-1,7),(2,2,3),'cream','tail_end')
    return m


def phoenix():
    m=Model('phoenix');m.bone('root')
    m.bone('body','root',(0,15,0),(.10,0,0));m.cube('body',(-4,-4,-6),(8,9,13),'red','body')
    m.bone('rump','body',(0,0,5));m.cube('rump',(-3,-2,-1),(6,6,7),'red','rump')
    m.bone('neck','body',(0,-2,-5),(.18,0,0));m.cube('neck',(-2,-6,-2),(4,8,4),'orange','neck')
    m.bone('head','neck',(0,-5,-1));m.cube('head',(-2.5,-3,-4),(5,5,5),'red','face')
    m.bone('beak','head',(0,0,-3));m.cube('beak',(-1,-1,-3),(2,2,3),'gold','beak')
    m.cube('beak',(-1,0,-4),(2,1,1),'gold','beak_tip')
    m.bone('crest','head',(0,-2.5,0),(-.35,0,0));m.cube('crest',(-.5,-5,0),(1,5,3),'gold','crest')
    # Offset the shorter plume surface so its sides do not fight the main crest.
    m.cube('crest',(-.48,-2.98,2),(1,3,3),'orange','crest')
    for side,s in [('left',1),('right',-1)]:
        n='wing_'+side
        m.bone(n,'body',(s*3.5,-1,-3),(0,s*.10,s*.10))
        m.cube(n,(0 if s>0 else -8,-1,-1),(8,2,9),'red','wing_root')
        m.bone(n+'_fore',n,(s*7,0,0),(0,-s*.17,0))
        m.cube(n+'_fore',(0 if s>0 else -8,-.5,0),(8,1,10),'orange','wing_coverts')
        # Sparse, broad remiges form a stepped trailing edge, not a voxel sculpture.
        for j in range(4):
            x=(j*2 if s>0 else -j*2-3)
            m.cube(n+'_fore',(x,.12+j*.04,5+j*.6),(3,1,9-j),'gold' if j==3 else 'orange','remige')
        m.bone(n+'_tip',n+'_fore',(s*7,0,2),(0,-s*.15,0))
        m.cube(n+'_tip',(0 if s>0 else -5,0,1),(5,1,9),'gold','remige')
        m.cube(n+'_tip',(s*2 if s>0 else -7,.04,3),(5,1,6),'gold','remige')
        m.bone('leg_'+side,'body',(s*2,4,3),(-.1,0,0))
        m.cube('leg_'+side,(-1,0,-1),(2,5,2),'ochre','leg')
        m.bone('foot_'+side,'leg_'+side,(0,4,0),(.1,0,0))
        m.cube('foot_'+side,(-1.5,0,-3),(3,1,4),'ochre','claw')
    for i in range(3):
        n=f'tail{i}';m.bone(n,'rump',((i-1)*1.5,0,5),(-.05,(i-1)*.17,0))
        m.cube(n,(-1,-.5,0),(2,1,12+(i==1)*2),'red','tail_feather')
        m.bone(n+'_tip',n,(0,.02,11+(i==1)*2),(-.12,0,0))
        m.cube(n+'_tip',(-1.5,-.5,0),(3,1,8),'gold','tail_eye')
    return m


PALETTES={
 'fox':['71351f','a85329','c67639','d98b49','e8a45c'],
 'cream':['a9a995','c8c7ae','dedcc1','f1e8cc','fff0d5'],
 'paw':['281f20','3a2b29','513b31','6b4c36','856140'],
 'red':['501b25','772831','a13532','c24931','dc6336'],
 'orange':['7b2b27','a54127','c7602c','de8234','eba745'],
 'gold':['785037','a97837','c79b45','dfbb62','efcf80'],
 'ochre':['49352d','6f4c2f','926b35','b18a44','cbaa63'],
}


def face_rects(c):
    u,v=c['uv'];w,h,d=c['size']
    return {'west':(u,v+d,d,h),'north':(u+d,v+d,w,h),
            'east':(u+d+w,v+d,d,h),'south':(u+2*d+w,v+d,w,h),
            'up':(u+d,v,w,d),'down':(u+d+w,v,w,d)}


def paint_face(c, face, width, height):
    """Directed clusters: anatomical region, surface normal and material, no RNG."""
    pal=['#'+s for s in PALETTES[c['material']]]
    role=c['role'];mat=c['material'];im=Image.new('RGBA',(width,height),pal[2]);d=ImageDraw.Draw(im)
    if mat=='fox':
        # Fur is grouped along the back-to-rump axis; the belly is an uninterrupted field.
        if role=='body':
            if face=='up':
                d.rectangle((2,0,width-3,height-1),fill=pal[1])
                for y in (3,8):d.line((2,y,width-3,y+1),fill=pal[2])
            elif face in ('east','west'):
                d.polygon([(0,height-3),(width//3,height-3),(width//2,height-2),(width-1,height-2),(width-1,height-1),(0,height-1)],fill='#dedcc1')
                d.line((0,1,width-1,1),fill=pal[3])
            elif face=='down':im.paste('#dedcc1',(0,0,width,height))
        elif role=='face':
            if face=='north':
                d.polygon([(0,3),(2,3),(3,4),(width-1,3),(width-1,height-1),(0,height-1)],fill='#f1e8cc')
                for x in (1,width-2):
                    d.rectangle((x,2,x,2),fill='#291e23')
                d.line((0,1,1,1),fill=pal[0]);d.line((width-2,1,width-1,1),fill=pal[0])
            elif face in ('east','west'):
                d.rectangle((0,3,width-1,height-1),fill='#dedcc1')
                x=1 if face=='west' else width-2;d.point((x,2),fill='#291e23')
        elif role=='ear' and face=='north':
            d.rectangle((0,1,width-1,height-2),fill='#563337');d.line((0,0,width-1,0),fill='#3a2b29')
        elif role in ('tail','tail_root'):
            if face in ('east','west','up','down'):
                along_z=face in ('up','down')
                for z in range(2,height if along_z else width,4):
                    if along_z:d.line((0,z,min(width-1,1),z+1),fill=pal[3])
                    else:d.line((z,0,z+1,min(height-1,1)),fill=pal[3])
                if role=='tail':
                    if along_z:d.rectangle((0,height-3,width-1,height-1),fill='#dedcc1')
                    else:d.rectangle((width-3,0,width-1,height-1),fill='#dedcc1')
            elif role=='tail' and face=='south':im.paste('#dedcc1',(0,0,width,height))
        elif role=='shin':
            d.rectangle((0,height-2,width-1,height-1),fill='#513b31')
    elif mat=='cream':
        if face=='down':im.paste(pal[1],(0,0,width,height))
        elif face in ('east','west'):d.line((0,height-1,width-1,height-1),fill=pal[1])
        if role=='muzzle' and face=='north':
            d.rectangle((1,0,width-2,0),fill='#291e23');d.point((width//2,1),fill='#513b31')
        if role=='throat' and face=='north':
            for y in (2,4):d.line((1,y,width-2,y),fill=pal[3])
    elif mat in ('red','orange','gold'):
        if face=='down':im.paste(pal[1],(0,0,width,height))
        if role=='body':
            if face=='north':
                d.polygon([(width//2-1,0),(width//2+1,0),(width-2,height-2),(width-3,height-1),(2,height-1),(1,height-2)],fill='#de8234')
                d.line((width//2,2,width//2,height-2),fill='#eba745')
            elif face in ('east','west'):
                for x in range(2,width-1,4):d.line((x,1,x+1,min(height-1,4)),fill=pal[3])
            elif face=='up':d.rectangle((width//2-1,1,width//2,height-2),fill=pal[1])
        elif role=='face':
            if face in ('east','west'):
                x=1 if face=='west' else width-2
                d.line((max(0,x-1),1,min(width-1,x+1),1),fill=pal[0]);d.point((x,2),fill='#efcf80')
                d.point((x,3),fill='#351d26')
            elif face=='north':
                d.line((0,1,width-1,1),fill=pal[0]);d.point((0,2),fill='#efcf80');d.point((width-1,2),fill='#efcf80')
        elif role=='neck' and face in ('north','east','west'):
            for y in range(1,height,3):d.line((1,y,width-2,y+1),fill=pal[3])
        elif role in ('wing_root','wing_coverts','remige','tail_feather','tail_eye'):
            if face in ('up','down'):
                for x in range(1,width,3):
                    d.line((x,1,x,height-2),fill=pal[1]);
                    if x+1<width:d.line((x+1,2,x+1,height-3),fill=pal[3])
                # Distal gold is a material region, never a border around every cuboid.
                if role in ('remige','tail_feather'):d.rectangle((0,height-2,width-1,height-1),fill='#dfbb62')
                if role=='tail_eye':
                    mid=width//2;d.rectangle((mid,2,mid,height-3),fill='#a13532')
                    d.point((mid,3),fill='#351d26');d.point((mid,4),fill='#efcf80')
        elif role.startswith('beak'):
            if face in ('east','west'):d.line((0,height-1,width-1,height-1),fill=pal[0])
            if role=='beak_tip' and face=='north':d.rectangle((0,height-1,width-1,height-1),fill='#49352d')
        elif role=='crest':
            if face in ('east','west'):d.line((0,0,0,height-1),fill=pal[3])
    elif mat=='ochre':
        if role=='leg' and face in ('north','south'):
            for y in range(1,height,2):d.line((0,y,width-1,y),fill=pal[1])
        if role=='claw' and face=='up':
            for x in (0,width-1):d.line((x,0,x,2),fill=pal[1])
            d.rectangle((0,0,width-1,0),fill='#281f20')
    return im


def atlas(m):
    # One texel per native model unit. Every cuboid owns a non-overlapping UV net.
    size=128
    im=Image.new('RGBA',(size,size));x=y=1;row=0
    for c in m.cubes:
        w,h,d=c['size'];bw=2*(w+d);bh=h+d
        if x+bw+1>size:x=1;y+=row+1;row=0
        if y+bh+1>size:raise ValueError('UV atlas overflow')
        c['uv']=[x,y];row=max(row,bh)
        for face,(u,v,fw,fh) in face_rects(c).items():
            tile=paint_face(c,face,int(fw),int(fh));im.paste(tile,(int(u),int(v)))
        x+=bw+1
    return im


def jf(x):return f'{float(x):.5f}F'


def export(m):
    folder=OUT/m.name;folder.mkdir(parents=True,exist_ok=True)
    im=atlas(m);path=ASSETS/'textures/entity/bestiary'/f'{m.name}.png';path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
    im.save(folder/'texture.png');im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(folder/'texture-4x.png')
    m.texture_size=list(im.size)
    data=dict(id=m.name,texture_size=m.texture_size,texture=str(path.relative_to(ROOT)),bones=m.bones)
    (folder/'model.json').write_text(json.dumps(data,indent=2)+'\n')
    uv=im.copy();d=ImageDraw.Draw(uv)
    for c in m.cubes:
        for name,(x,y,w,h) in face_rects(c).items():d.rectangle((x,y,x+w-1,y+h-1),outline='#ed58b1')
    uv.resize((uv.width*4,uv.height*4),Image.Resampling.NEAREST).save(folder/'uv-4x.png')
    lines=['        MeshDefinition mesh = new MeshDefinition();','        PartDefinition root = mesh.getRoot();']
    for b in m.bones:
        if b['name']=='root':continue
        cubes='CubeListBuilder.create()'
        for c in b['cubes']:
            cubes+=f'.texOffs({c["uv"][0]}, {c["uv"][1]}).addBox('+', '.join(map(jf,c['origin']+c['size']))+')'
        pose='PartPose.offsetAndRotation('+', '.join(map(jf,b['pivot']+b['rotation']))+')'
        lines.append(f'        PartDefinition {b["name"]} = {b["parent"]}.addOrReplaceChild("{b["name"]}", {cubes}, {pose});')
    lines.append(f'        return LayerDefinition.create(mesh, {im.width}, {im.height});')
    return '\n'.join(lines)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    methods=[]
    for m in (fox(),phoenix()):
        methods.append('    public static LayerDefinition '+('fox' if m.name=='nine_tailed_fox' else 'phoenix')+'() {\n'+export(m)+'\n    }')
    JAVA.write_text('''package com.dynasty.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;

/** Original anatomy and UVs. Generated by tools/art/bestiary-v41/build_models.py. */
public final class BestiarySpiritLayers {
    private BestiarySpiritLayers() {}
'''+ '\n\n'.join(methods)+'\n}\n')
    print('Exported native layers and original pixel atlases for fox + phoenix')


if __name__=='__main__':main()
