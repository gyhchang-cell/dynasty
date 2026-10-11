"""Validate actual exported resource contracts; does not replace visual/native QA."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from build_models import REPO, ASSET, OUT

def main():
    manifest=json.loads((OUT/'model-manifest.json').read_text());result={}
    for id in manifest:
        gp=ASSET/f'geo/secondary/{id}.geo.json';ap=ASSET/f'animations/secondary/{id}.animation.json';tp=ASSET/f'textures/entity/secondary/{id}.png'
        g=json.loads(gp.read_text())['minecraft:geometry'][0];a=json.loads(ap.read_text())['animations'];im=Image.open(tp)
        from cull_internal_faces import IDS, cull
        if id in IDS:
            proof=OUT/f'face-cull-v1/before/{id}.geo.json'
            if proof.exists():
                original=json.loads(proof.read_text());cull(original)
                assert original['minecraft:geometry'][0]==g,(id,'unproved missing face or changed geometry')
        assert len(im.getcolors(1000))==4,(id,'palette')
        assert im.size==(16,16),(id,'actual 16x16 PNG required')
        pixels=im.convert('RGB');white=(255,255,255)
        assert all(pixels.getpixel((x,y))==white for x in range(16) for y in range(16) if x in (0,15) or y in (0,15)),(id,'white margin')
        for y in range(0,16,2):
            for x in range(0,16,2):
                assert len(set(pixels.crop((x,y,x+2,y+2)).getdata()))==1,(id,'color regions must be 2x2 or larger')
        assert im.size==(g['description']['texture_width'],g['description']['texture_height'])
        names={b['name'] for b in g['bones']};assert len(names)==len(g['bones'])
        original=json.loads((OUT/f'source/{id}.geo.json').read_text())['minecraft:geometry'][0]
        assert {b['name'] for b in original['bones']}<=names,(id,'removed bone')
        visited=set()
        for b in g['bones']:
            assert not b.get('parent') or b['parent'] in visited,(id,'parent ordering')
            visited.add(b['name'])
            for c in b.get('cubes',[]):
                assert all(v>0 for v in c['size'])
                assert c['uv'] and set(c['uv'])<={'north','south','east','west','up','down'}
                if id not in IDS:assert len(c['uv'])==6,(id,'unproved missing face')
                for uv in c['uv'].values():
                    assert all(0<=uv['uv'][i]<=uv['uv'][i]+uv['uv_size'][i]<=im.size[i] for i in range(2)),(id,'UV bounds')
                    assert all(float(v).is_integer() for v in uv['uv']+uv['uv_size']),(id,'pixel aligned UV')
                    x,y=uv['uv'];w,h=uv['uv_size']
                    assert white not in set(pixels.crop((x,y,x+w,y+h)).getdata()),(id,'background sampled by entity')
        for name,ch in a.items():
            assert set(ch['bones'])<=names,(id,name,'missing animated bone')
            for track in ch['bones'].values():
                for value in track.values():
                    assert max(map(float,value))<=ch['animation_length']
                    assert list(value.values())[0]==list(value.values())[-1],(id,name,'loop seam')
        assert {'idle','wander','hunt','flee','attack','special','evade'}<=set(a)
        result[id]={'bones':len(names),'cuboids':sum(len(b.get('cubes',[])) for b in g['bones']),
                    'renderedFaces':sum(len(c['uv']) for b in g['bones'] for c in b.get('cubes',[])),
                    'preservedOriginalBones':len(original['bones']),'clips':len(a),'pureColors':4,'atlas':im.size,
                    'resources':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [gp,ap,tp]}}
    (OUT/'static-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS exported resources:',len(result),'entities;',sum(v['clips'] for v in result.values()),'clips')

if __name__=='__main__':main()
