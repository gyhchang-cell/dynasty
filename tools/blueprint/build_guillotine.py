#!/usr/bin/env python3
"""Original cuboid guillotine using existing vanilla pixel materials.

The designated art chat's three atlas drafts failed its flat-color check and stay
unpublished. Runtime JSON references vanilla resources, without copying/replacing them.
"""
import base64
import json
import uuid
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'src/main/resources/assets/dynasty'
OUT=ROOT/'docs/art/cod2-guillotine-v1'
TEXTURES=['minecraft:block/anvil','minecraft:block/iron_block','minecraft:block/dark_oak_planks','minecraft:block/exposed_copper']
MODELS={
    'anchor': [('mount',[0,1,1],[16,15,15],2),('band_a',[1,0,0],[4,16,16],3),('band_b',[12,0,0],[15,16,16],3)],
    'frame': [('timber',[.25,1,1],[15.75,15,15],2),('left_binding',[0,0,0],[2,16,16],3),
              ('middle_binding',[7,0,0],[9,16,16],3),('right_binding',[14,0,0],[16,16,16],3)],
    'rod': [('iron_guide',[0,0,0],[16,16,16],0)],
    'blade': [('plate',[0,2,2],[16,14,14],0),('cutting_edge',[0,0,3],[16,2,13],1),
              ('top_carriage',[0,14,1],[16,16,15],3),
              ('front_muzzle',[6.5,4,0],[9.5,8,2],3),('front_brow',[6,10,0],[10,12,2],3),
              ('front_ear_l',[6,12,0],[7,15,2],0),('front_ear_r',[9,12,0],[10,15,2],0),
              ('front_eye_l',[6.5,8,0],[7.25,10,2],1),('front_eye_r',[8.75,8,0],[9.5,10,2],1),
              ('back_muzzle',[6.5,4,14],[9.5,8,16],3),('back_brow',[6,10,14],[10,12,16],3),
              ('back_ear_l',[6,12,14],[7,15,16],0),('back_ear_r',[9,12,14],[10,15,16],0),
              ('back_eye_l',[6.5,8,14],[7.25,10,16],1),('back_eye_r',[8.75,8,14],[9.5,10,16],1)]
}


def model(cubes):
    return {'ambientocclusion':False,'textures':{**{str(i):t for i,t in enumerate(TEXTURES)},'particle':TEXTURES[0]},'elements':[
        {'name':name,'from':lo,'to':hi,'faces':{face:{'uv':[0,0,16,16],'texture':'#'+str(material)}
         for face in ('north','south','east','west','up','down')}} for name,lo,hi,material in cubes]}


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def vanilla_images():
    # Read-only asset extraction for the local editable file / software preview.
    # Never launches Java, builds, installs or changes runtime vanilla textures.
    for line in (ROOT/'build/classpath/runClient_minecraftClasspath.txt').read_text().replace(':','\n').splitlines():
        path=Path(line)
        if path.suffix!='.jar' or not path.is_file():continue
        with zipfile.ZipFile(path) as archive:
            names=['assets/'+t.replace(':','/textures/')+'.png' for t in TEXTURES]
            if all(n in archive.namelist() for n in names):return [archive.read(n) for n in names]
    raise FileNotFoundError('Existing Minecraft client texture resources unavailable')


def build():
    images=vanilla_images()
    namespace=uuid.UUID('c0bcbf94-0175-436d-9c85-3941886849e9')
    for name,cubes in MODELS.items():
        data=model(cubes);write(ASSETS/f'models/block/cod2_guillotine/{name}.json',data)
        uid=lambda text:str(uuid.uuid5(namespace,name+'/'+text))
        elements=[dict(e,type='cube',uuid=uid(e['name']),origin=[8,8,8],rotation=[0,0,0],
            faces={f:{'uv':v['uv'],'texture':int(v['texture'][1:])} for f,v in e['faces'].items()}) for e in data['elements']]
        write(OUT/f'blockbench/{name}.bbmodel',{'meta':{'format_version':'4.10','model_format':'java_block','box_uv':False},
            'name':'guillotine_'+name,'resolution':{'width':16,'height':16},'elements':elements,
            'outliner':[{'name':name,'origin':[8,0,8],'uuid':uid('group'),'children':[e['uuid'] for e in elements]}],
            'textures':[{'name':texture.rsplit('/',1)[-1]+'.png','id':str(i),'uuid':uid('texture'+str(i)),'width':16,'height':16,
                'uv_width':16,'uv_height':16,'source':'data:image/png;base64,'+base64.b64encode(images[i]).decode()} for i,texture in enumerate(TEXTURES)]})
    write(ASSETS/'blockstates/guillotine_trap.json',{'variants':{f'facing={direction}':{
        'model':'dynasty:block/cod2_guillotine/anchor','y':angle} for direction,angle in
        [('north',0),('east',90),('south',180),('west',270)]}})
    print('Exported four actual block models, four editable sources and four facing variants; vanilla textures referenced unchanged')


def render():
    """Software view of the exported Cuboids and the renderer's assembled dimensions."""
    import io
    import sys
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(ROOT/'tools/art/cod2-voxel'))
    import review
    from review_chensha_architecture import JavaCoordinates
    java=JavaCoordinates();java.env.update(RAISED=-.875,LOWERED=-3)
    motion=java.load('GuillotineTrap',['bladeY'])
    # A local sampling atlas for the software renderer only; never a runtime texture.
    atlas=Image.new('RGB',(64,16))
    for i,data in enumerate(vanilla_images()):atlas.paste(Image.open(io.BytesIO(data)).convert('RGB'),(16*i,0))
    atlas.save(OUT/'preview-materials.png');review.TEX=OUT/'preview-materials.png';review.OUT=OUT
    renderer=(ROOT/'src/main/java/com/dynasty/dungeon/client/DungeonMechanismRenderer.java').read_text()
    assert 'GUILLOTINE_FRAME,-1,-.125,.125,3,.375,.75' in renderer
    assert 'new double[]{-.985,1.86}' in renderer and 'new double[]{-.5,1.375}' in renderer
    assert 'GUILLOTINE_BLADE,-.875,y,.3125,2.75,.75,.375' in renderer
    assert 'GUILLOTINE_ROD,x,y+.7,.4375,.125,-y,.125' in renderer
    def assembly(y):
        parts=[('anchor',(0,0,0),(1,1,1)),('frame',(-1,-.125,.125),(3,.375,.75)),
               ('blade',(-.875,y,.3125),(2.75,.75,.375))]
        parts += [('rod',(x,-3,.25),(.125,3,.5)) for x in (-.985,1.86)]
        parts += [('rod',(x,y+.7,.4375),(.125,-y,.125)) for x in (-.5,1.375)]
        quads=[]
        for name,offset,scale in parts:
            data=json.loads((ASSETS/f'models/block/cod2_guillotine/{name}.json').read_text())
            for e in data['elements']:
                for face,corners in review.FACES.items():
                    points=np.array(corners)*(np.array(e['to'])-e['from'])+e['from']
                    points=(points/16*np.array(scale)+np.array(offset)-np.array([.5,0,.5]))*16
                    material=int(e['faces'][face]['texture'][1:])
                    quads.append((points,{'uv':[material*16,0],'uv_size':[16,16]},e['name']))
        return quads
    frames=[(0,0,0,False,'RAISED / FRONT'),(0,0,45,False,'RAISED / 45'),(0,0,90,False,'RAISED / SIDE'),
            (0,0,180,False,'RAISED / BACK'),(0,0,0,True,'SILHOUETTE'),(2,.25,0,False,'FALL / TICK 1'),
            (2,.5,0,False,'CONTACT / TICK 2'),(3,.5,45,False,'RECOVERY / HALF')]
    images=[review.raster(assembly(motion.bladeY(phase,progress)),yaw,8,size=(380,400),silhouette=black)
            for phase,progress,yaw,black,label in frames]
    review.sheet(images,[f[-1] for f in frames],'model-review.png','Guillotine / actual exported models / SOFTWARE, NOT IN GAME',cols=4)
    print('Reviewed eight model/phase views from production Cuboids and motion function')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');args=parser.parse_args()
    build()
    if args.render:render()
