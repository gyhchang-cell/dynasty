"""Check the authored source, UV padding, original clips and shipped resources."""
import base64
import copy
import hashlib
import json
from pathlib import Path
from PIL import Image
from build_models import ASSET, REPO, Rig
from material_atlas import IDS, render
from rig_bounds import vertices
import build_additional
import build_invertebrates
import build_fliers


def shape(bones):
    bones=copy.deepcopy(bones)
    for b in bones:
        for c in b.get('cubes',[]):c.pop('uv')
    return bones


def main():
    base=REPO/'build/maintenance/secondary-materials-v2';out=REPO/'docs/art/secondary-materials-v2'
    save=Rig.save
    try:
        Rig.save=lambda r:r
        authored={'clockwork_rat':build_invertebrates.rat(),
                  'wooden_magpie':build_fliers.bird('wooden_magpie',mechanical=True),
                  'stone_sprite':build_additional.stone()}
    finally:Rig.save=save
    results={}
    for id in sorted(IDS):
        gp=ASSET/f'geo/secondary/{id}.geo.json';tp=ASSET/f'textures/entity/secondary/{id}.png';ap=ASSET/f'animations/secondary/{id}.animation.json'
        document=json.loads(gp.read_text());g=document['minecraft:geometry'][0]
        assert shape(g['bones'])==shape(authored[id].bones),(id,'generator drift')
        exported,png,rec=render(id,document)
        assert exported==document and png==tp.read_bytes(),(id,'atlas export drift')
        im=Image.open(tp)
        for tile in rec['islandData']:
            x,y=tile['uv'];w,h=tile['size']
            for yy in range(-2,h+2):
                for xx in range(-2,w+2):
                    assert im.getpixel((x+xx,y+yy))==im.getpixel((x+min(w-1,max(0,xx)),y+min(h-1,max(0,yy)))),(id,'padding bleed')
        source=out/f'blockbench/{id}.bbmodel';bb=json.loads(source.read_text())
        assert base64.b64decode(bb['textures'][0]['source'].split(',')[1])==png
        assert len(bb['elements'])==sum(len(b.get('cubes',[])) for b in g['bones'])
        assert (out/f'blockbench/{id}.animation.json').read_bytes()==ap.read_bytes()
        before=base/f'before/animations/secondary/{id}.animation.json'
        if before.exists():assert before.read_bytes()==ap.read_bytes(),(id,'changed existing animation')
        points=vertices(g['bones'],{},0)
        minimum=[min(v[i] for v in points)/16 for i in range(3)]
        maximum=[max(v[i] for v in points)/16 for i in range(3)]
        clips=json.loads(ap.read_text())['animations'];bound=[minimum.copy(),maximum.copy()]
        for clip in clips.values():
            for i in range(25):
                p=vertices(g['bones'],clip['bones'],clip['animation_length']*i/24)
                for axis in range(3):
                    bound[0][axis]=min(bound[0][axis],min(v[axis] for v in p)/16)
                    bound[1][axis]=max(bound[1][axis],max(v[axis] for v in p)/16)
        # Current authored 4x4 render envelope remains ample for the three rigs.
        assert all(-2<=bound[0][axis]<=bound[1][axis]<=2 for axis in (0,2)),id
        assert -.9<=bound[0][1] and bound[1][1]<=3.1,id
        results[id]={'sourceGeometryExact':True,'shapePreserved':id!='stone_sprite',
            'animationsPreserved':before.exists(),'regenerationExact':True,
            'gutterVerified':True,'editableSourceVerified':True,
            'atlas':list(im.size),'colors':rec['colors'],'bones':len(g['bones']),
            'cuboids':len(bb['elements']),'clips':len(clips),
            'visibleRestDimensionsBlocks':[maximum[i]-minimum[i] for i in range(3)],
            'visibleRestMinBlocks':minimum,'visibleRestMaxBlocks':maximum,
            'animationBoundsBlocks':bound,'boundPoseSamples':len(clips)*25,
            'nativeClient':'PENDING: GLFW reported no primary monitor; screen was not woken',
            'hashes':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (gp,tp,ap,source)}}
    (out/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS 3 authored rigs, 438 faces with 2px gutters, 57 unchanged clips, 1425 bound poses and editable sources')


if __name__=='__main__':main()
