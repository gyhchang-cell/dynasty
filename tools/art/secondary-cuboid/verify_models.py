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
        assert len(im.getcolors(1000))==4,(id,'palette')
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
                assert set(c['uv'])=={'north','south','east','west','up','down'}
                for uv in c['uv'].values():
                    assert all(0<=uv['uv'][i]<=uv['uv'][i]+uv['uv_size'][i]<=im.size[i] for i in range(2)),(id,'UV bounds')
        for name,ch in a.items():
            assert set(ch['bones'])<=names,(id,name,'missing animated bone')
            for track in ch['bones'].values():
                for value in track.values():
                    assert max(map(float,value))<=ch['animation_length']
                    assert list(value.values())[0]==list(value.values())[-1],(id,name,'loop seam')
        assert {'idle','wander','hunt','flee','attack','special','evade'}<=set(a)
        result[id]={'bones':len(names),'cuboids':sum(len(b.get('cubes',[])) for b in g['bones']),
                    'preservedOriginalBones':len(original['bones']),'clips':len(a),'pureColors':4,'atlas':im.size,
                    'resources':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [gp,ap,tp]}}
    (OUT/'static-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS exported resources:',len(result),'entities;',sum(v['clips'] for v in result.values()),'clips')

if __name__=='__main__':main()
