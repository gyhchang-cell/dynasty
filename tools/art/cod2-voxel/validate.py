"""Validate runtime contracts, every pixel/UV, editable coordinates and ground clearance."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
import review

OUT=review.OUT


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+',default=['jubi_shigandang','juli_bixi_kuilei','tongbi_feitian_yecha'])
    parser.add_argument('--output',default='validation.json');args=parser.parse_args()
    results=[]
    for name in args.ids:
        review.select(name)
        g=json.loads(review.GEO.read_text());a=json.loads(review.ANIM.read_text())
        assert g['format_version']=='1.12.0' and a['format_version']=='1.8.0'
        model=g['minecraft:geometry'][0];bones=model['bones'];names={b['name'] for b in bones}
        assert len(names)==len(bones)
        parents={b['name']:b.get('parent') for b in bones}
        for bone in names:
            seen=set();p=bone
            while p:
                assert p in names and p not in seen,(name,bone,'cycle or missing parent')
                seen.add(p);p=parents[p]
        original=json.loads((review.SOURCE/'original.geo.json').read_text())['minecraft:geometry'][0]
        assert {b['name'] for b in original['bones']}<=names,'Dropped established locator'
        old=json.loads((review.SOURCE/'original.animation.json').read_text())['animations']
        assert set(a['animations'])==set(old)
        image=Image.open(review.TEX).convert('RGB')
        desc=g['minecraft:geometry'][0]['description']
        assert image.size==(desc['texture_width'],desc['texture_height'])
        pixels=np.asarray(image);palette={tuple(c) for c in pixels.reshape(-1,3)}
        legacy=image.size==(16,16)
        if legacy:
            assert len(palette)==4 and (255,255,255) in palette
            assert np.all(pixels[0]==255) and np.all(pixels[-1]==255) and np.all(pixels[:,0]==255) and np.all(pixels[:,-1]==255)
        occupied=set()
        for b in bones:
            for c in b.get('cubes',[]):
                assert all(v>0 for v in c['size']) and 'texture_meshes' not in b
                for uv in c['uv'].values():
                    u,v=uv['uv'];du,dv=uv['uv_size']
                    assert all(float(x).is_integer() for x in [u,v,du,dv])
                    assert 0<=u<u+du<=image.width and 0<=v<v+dv<=image.height
                    if legacy:
                        block=pixels[v:v+dv,u:u+du]
                        assert np.all(block==block[0,0]) and not np.all(block[0,0]==255)
                    else:
                        for y in range(v,v+dv):
                            for x in range(u,u+du):
                                assert (x,y) not in occupied,'UV overlap'
                                occupied.add((x,y))
        bounds={}
        for key,clip in a['animations'].items():
            assert clip['animation_length']==old[key]['animation_length']
            assert set(clip['bones'])<=names
            for channels in clip['bones'].values():
                for track in channels.values():
                    if isinstance(track,dict):assert min(map(float,track))>=0 and max(map(float,track))<=clip['animation_length']
                    if clip.get('loop') is True:
                        assert np.allclose(review.sample(track,0),review.sample(track,clip['animation_length']),atol=1e-6),'Loop seam jumps: '+key
            minima=[]
            for tick in np.arange(0,clip['animation_length']*20+.01,.25):
                p=np.concatenate([p for p,_,_ in review.geometry(key.rsplit('.',1)[1],float(tick))])
                assert np.isfinite(p).all()
                minima.append(float(p[:,1].min()))
            bounds[key.rsplit('.',1)[1]]=round(min(minima),4)
            assert min(minima)>=-.09,(name,key,'floor penetration',min(minima))
        bb=json.loads((OUT/'blockbench'/(name+'.bbmodel')).read_text())
        assert bb['meta']['model_format']=='geckolib_model'
        cubes=[c for b in bones for c in b.get('cubes',[])]
        assert len(cubes)==len(bb['elements'])
        for c,element in zip(cubes,bb['elements']):
            low=element['from'];high=element['to'];size=[high[i]-low[i] for i in range(3)]
            origin=[-high[0],low[1],low[2]]
            assert np.allclose(size,c['size'],atol=1e-7) and np.allclose(origin,c['origin'],atol=1e-7) and element['inflate']==c.get('inflate',0),'Editing source lost coordinate/armour thickness'
        results.append(dict(id=name,bones=len(bones),cuboids=len(cubes),texture=list(image.size),palette=[[int(v) for v in c] for c in sorted(palette)],
            clips=len(a['animations']),ground_minimum_pixels=bounds,resource_sha256={str(p.relative_to(review.REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [review.GEO,review.ANIM,review.TEX]}))
    (OUT/args.output).write_text(json.dumps(dict(passed=True,models=results),indent=2)+'\n')
    print('PASS:',len(results),'resource contracts, declared pixel atlases, UVs, rigs, editable source, quarter-tick floor clearance')


if __name__=='__main__':main()
