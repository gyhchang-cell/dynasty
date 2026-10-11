#!/usr/bin/env python3
"""Validate native block UVs, half splitting, registered variants and embedded authoring bytes."""
from pathlib import Path
import base64, hashlib, json, math
from itertools import combinations, product
from PIL import Image
from remains_resources import ASSETS, DOC, STATUE, COFFER

def exposed_coplanar_conflicts(parts):
    errors=[]
    for a,b in combinations(parts,2):
        for axis in range(3):
            others=[j for j in range(3) if j!=axis]
            lo=[max(a['a'][j],b['a'][j]) for j in others];hi=[min(a['b'][j],b['b'][j]) for j in others]
            if any(lo[k]>=hi[k] for k in range(2)):continue
            for bound,sign in [('a',-1),('b',1)]:
                plane=a[bound][axis]
                if plane!=b[bound][axis]:continue
                face=[('west','east'),('down','up'),('north','south')][axis][sign==1]
                def material(p):
                    return {'up':'L','down':'D','south':'D'}.get(face,'B') if p['material']=='B' else p['material']
                if material(a)==material(b):continue
                for fractions in product((.25,.75),repeat=2):
                    sample=[0,0,0];sample[axis]=plane+sign*.001
                    for k,j in enumerate(others):sample[j]=lo[k]+fractions[k]*(hi[k]-lo[k])
                    if not any(all(p['a'][j]<sample[j]<p['b'][j] for j in range(3)) for p in parts if p is not a and p is not b):
                        errors.append((a['name'],b['name'],face));break
    return errors

def main():
    files=[];checks=[]
    for name in ('lootable_remains','rebel_general_statue'):
        png=ASSETS/f'textures/block/{name}.png';im=Image.open(png).convert('RGB')
        assert im.size==(16,16) and len(set(im.get_flattened_data()))<=4
        for x in range(16):
            for y in range(16):
                color=im.getpixel((x,y))
                if x<2 or x>13 or y<2 or y>13:assert color==(255,255,255)
                assert any(all(im.getpixel((a+dx,b+dy))==color for dx in (0,1) for dy in (0,1)) for a in (x-1,x) for b in (y-1,y) if 0<=a<15 and 0<=b<15)
        paths=[ASSETS/f'models/block/{name}.json']
        if name.endswith('statue'):paths.extend(sorted((ASSETS/'models/block').glob(name+'_*.json')))
        for p in paths:
            obj=json.loads(p.read_text());assert obj['texture_size']==[16,16]
            for e in obj['elements']:
                a,b=e['from'],e['to'];assert all(math.isfinite(v) for v in a+b)
                assert all(a[i]<b[i] for i in range(3)) and len(e['faces'])==6
                if '_lower_' in p.name:assert 0<=a[1]<b[1]<=16
                if '_upper_' in p.name:assert 0<=a[1]<b[1]<=8
                assert all(0<=a[i]<b[i]<=16 for i in (0,2))
                for f in e['faces'].values():
                    u,v,U,V=f['uv'];assert all(isinstance(z,int) for z in f['uv']) and 2<=u<U<=14 and 2<=v<V<=14 and U-u>=2 and V-v>=2
                    island={im.getpixel((x,y)) for x in range(u,U) for y in range(v,V)}
                    assert len(island)==1 and (255,255,255) not in island
            files.append(p)
        source=DOC/f'blockbench/{name}.bbmodel';bb=json.loads(source.read_text());assert base64.b64decode(bb['textures'][0]['source'].split(',',1)[1])==png.read_bytes()
        authored=STATUE if name.endswith('statue') else COFFER
        conflicts=exposed_coplanar_conflicts(authored)
        assert not conflicts, conflicts
        assert len(bb['elements'])==len(authored)
        for part,e in zip(authored,bb['elements']):assert e['from']==part['a'] and e['to']==part['b'] and all(v==0 for v in e['rotation'])
        files.extend([png,source]);checks.append(name+' exact 16px / 4-color / 2px white border / 2x2 regions / solid-island UV / embedded source parity')
    variants=json.loads((ASSETS/'blockstates/rebel_general_statue.json').read_text())['variants'];assert len(variants)==16
    for row in variants.values():assert (ASSETS/('models/'+row['model'].split(':')[1]+'.json')).exists()
    for armed in ('armed','empty'):
        pieces={}
        for half,offset in [('lower',0),('upper',16)]:
            for e in json.loads((ASSETS/f'models/block/rebel_general_statue_{half}_{armed}.json').read_text())['elements']:
                a,b=list(e['from']),list(e['to']);a[1]+=offset;b[1]+=offset;pieces.setdefault(e['name'],[]).append((a,b))
        expected=[p for p in STATUE if armed=='armed' or p['group']!='weapon']
        assert set(pieces)=={p['name'] for p in expected}
        for p in expected:
            ps=sorted(pieces[p['name']],key=lambda x:x[0][1]);assert ps[0][0]==p['a'] and ps[-1][1]==p['b']
            assert all(ps[i][1][1]==ps[i+1][0][1] for i in range(len(ps)-1))
            assert all(a[j]==p['a'][j] and b[j]==p['b'][j] for a,b in ps for j in (0,2))
    checks.append('16 facing/half/weapon states; halves exactly recombine authored cuboids; weapon disappears without moving hand or armor')
    checks.append('No sampled exposed coplanar overlaps with differing face colors (armor/hand/leg flicker audit)')
    report=dict(checks=checks,files={str(p.relative_to(ASSETS.parents[4])):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (DOC/'resource-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('PASS '+str(len(files))+' native art/source files; strict UV/texture/half/variant checks')
if __name__=='__main__':main()
