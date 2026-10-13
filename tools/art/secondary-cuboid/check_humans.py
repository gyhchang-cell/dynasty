"""Real files, regeneration, per-face gutters, grip contacts and clip envelopes."""
import base64
import hashlib
import json
from PIL import Image
from build_models import REPO, ASSET
from human_atlas import generated, IDS
from rig_bounds import vertices

TOOLS={'bandit_thug':('blade','left_hand'),'night_watchman':('lantern','left_hand'),
       'herb_picker':('sickle','right_hand'),'famished_refugee':('staff','left_hand'),
       'swindler':('abacus','right_hand')}


def inside(p,c):
    return all(c['origin'][i]-1e-6<=p[i]<=c['origin'][i]+c['size'][i]+1e-6 for i in range(3))


def main():
    base=REPO/'build/maintenance/secondary-humans-v3';out=REPO/'docs/art/secondary-humans-v3'
    result={};authored=generated()
    for id in sorted(IDS):
        gp=ASSET/f'geo/secondary/{id}.geo.json';tp=ASSET/f'textures/entity/secondary/{id}.png';ap=ASSET/f'animations/secondary/{id}.animation.json'
        doc=json.loads(gp.read_text());g=doc['minecraft:geometry'][0];geo,png,rec=authored[id]
        assert geo==doc and png==tp.read_bytes(),(id,'source/export drift')
        old=json.loads((base/f'before/geo/secondary/{id}.geo.json').read_text())['minecraft:geometry'][0]
        assert {b['name']:b.get('parent') for b in old['bones']}=={b['name']:b.get('parent') for b in g['bones']},(id,'bone hierarchy changed')
        oldfaces=sum(len(c['uv']) for b in old['bones'] for c in b.get('cubes',[]))
        assert rec['faces']<=oldfaces,(id,'face count increased')
        assert ap.read_bytes()==(base/f'before/animations/secondary/{id}.animation.json').read_bytes(),(id,'clip changed')
        im=Image.open(tp)
        for island in rec['islandData']:
            x,y=island['uv'];w,h=island['size']
            for yy in range(-2,h+2):
                for xx in range(-2,w+2):
                    assert im.getpixel((x+xx,y+yy))==im.getpixel((x+min(w-1,max(0,xx)),y+min(h-1,max(0,yy)))),(id,'UV edge bleed')
        bb=json.loads((out/f'blockbench/{id}.bbmodel').read_text())
        assert base64.b64decode(bb['textures'][0]['source'].split(',')[1])==png
        assert len(bb['elements'])==sum(len(b.get('cubes',[])) for b in g['bones'])
        assert (out/f'blockbench/{id}.animation.json').read_bytes()==ap.read_bytes()
        by={b['name']:b for b in g['bones']};tool,hand=TOOLS[id]
        assert by[tool]['parent']==hand
        anchor=by[tool]['pivot'];assert any(inside(anchor,c) for c in by[hand]['cubes']),(id,'tool pivot outside palm')
        assert any(inside(anchor,c) for c in by[tool]['cubes']),(id,'palm misses actual shaft/contact')
        # All descendants share the hand transform, so the verified grip remains
        # invariant under every pre-existing shoulder/elbow/wrist animation.
        for part in (hand,tool):
            assert all(k not in by[part] for k in ('scale','position'))
        points=vertices(g['bones'],{},0);low=[min(v[i] for v in points)/16 for i in range(3)];high=[max(v[i] for v in points)/16 for i in range(3)]
        bound=[low.copy(),high.copy()];clips=json.loads(ap.read_text())['animations']
        for clip in clips.values():
            assert not any(b in clip['bones'] for b in (tool,hand)),(id,'grip independently animated')
            for i in range(25):
                p=vertices(g['bones'],clip['bones'],clip['animation_length']*i/24)
                for axis in range(3):
                    bound[0][axis]=min(bound[0][axis],min(v[axis] for v in p)/16)
                    bound[1][axis]=max(bound[1][axis],max(v[axis] for v in p)/16)
        assert all(-2<=bound[0][axis]<=bound[1][axis]<=2 for axis in (0,2)),id
        assert -.9<=bound[0][1] and bound[1][1]<=3.1,id
        result[id]={'sourceGeometryExact':True,'animationsPreserved':True,'bonesAndParentsPreserved':True,
            'gutterVerified':True,'editableSourceVerified':True,'heldToolPalmContactVerified':True,
            'heldTool':tool,'atlas':list(im.size),'colors':rec['colors'],'bones':len(g['bones']),
            'cuboids':len(bb['elements']),'renderedFaces':rec['faces'],'beforeFaces':oldfaces,
            'clips':len(clips),'boundsPoseSamples':len(clips)*25,
            'visibleRestDimensionsBlocks':[high[i]-low[i] for i in range(3)],
            'visibleRestMinBlocks':low,'visibleRestMaxBlocks':high,'animationBoundsBlocks':bound,
            'collisionUnchanged':[0.6,1.8],
            'nativeClient':'PENDING: earlier GLFW reported no primary monitor; no new client started',
            'vanillaFaceBudget':'PENDING: reduced against prior art, not claimed within vanilla base budget',
            'hashes':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (gp,tp,ap)}}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS five regenerated rigs, 95 unchanged clips, five actual palm/tool contacts and 2px UV gutters')
    print('Faces:',sum(v['renderedFaces'] for v in result.values()),'before:',sum(v['beforeFaces'] for v in result.values()),'; sampled poses:',sum(v['boundsPoseSamples'] for v in result.values()))


if __name__=='__main__':main()
