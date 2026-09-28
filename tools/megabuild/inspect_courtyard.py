"""Read-only snapshot and measured plan of the player's new courtyard."""
import sys,json,gzip,hashlib,shutil
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'art'))
from read_build_world import WORLD,stable,chunks,blocks
from audit_patrol_population import nbt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/courtyard-reference'
FULL='--full' in sys.argv
if FULL:OUT=ROOT/'build/courtyard-full-reference'
def main():
    OUT.mkdir(exist_ok=True)
    snapshot=OUT/'snapshot'
    if not snapshot.exists():
        snapshot.mkdir()
        hashes={}
        for p in WORLD.rglob('*'):
            if not p.is_file() or p.name=='session.lock':continue
            raw=stable(p);q=snapshot/p.relative_to(WORLD);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
            hashes[str(p.relative_to(WORLD))]=hashlib.sha256(raw).hexdigest()
        (OUT/'source-hashes.json').write_text(json.dumps(hashes,indent=2))
    selected={}
    for f in (snapshot/'region').glob('r.*.mca'):
        rx,rz=map(int,f.stem.split('.')[1:])
        if rx!=0 or rz not in (-1,0):continue
        for c in chunks(f.read_bytes()):
            if not ((15<=c['xPos']<=27 and -14<=c['zPos']<=-3) if FULL else (20<=c['xPos']<=30 and -12<=c['zPos']<=1)):continue
            for p,s in blocks(c):
                inside=(240<=p[0]<=439 and -210<=p[2]<=-50 and -63<=p[1]<=64) if FULL else (330<=p[0]<=475 and -180<=p[2]<=10 and -60<=p[1]<=0)
                if inside and s['Name'] not in ('minecraft:air','minecraft:light','minecraft:grass_block'):
                    selected[','.join(map(str,p))]=s
    (OUT/'blocks.json').write_text(json.dumps(selected))
    from PIL import Image,ImageDraw
    colors={'smooth_quartz':'#eeeae1','diorite':'#cccac2','calcite':'#e9dcc1','white_concrete_powder':'#e3dcd0','dirt':'#9c6d45','water':'#529ab3'}
    im=Image.new('RGB',(1200,1000) if FULL else (900,1200),'#344e39');d=ImageDraw.Draw(im)
    top={}
    for key,s in selected.items():
        x,y,z=map(int,key.split(','))
        if y<(-60 if FULL else -59):continue
        if (x,z) not in top or y>top[x,z][0]:top[x,z]=(y,s)
    for (x,z),(y,s) in top.items():
        n=s['Name'].split(':')[1];color=colors.get(n,'#715238')
        if 'deepslate' in n:color='#30353e'
        elif 'leaves' in n:color='#ce9ba9' if 'cherry' in n else '#638755'
        elif 'bamboo' in n:color='#8eaa58'
        px=(x-(240 if FULL else 330))*6;py=(z+(210 if FULL else 180))*6
        d.rectangle((px,py,px+5,py+5),fill=color)
    for x in range(240 if FULL else 330,440 if FULL else 476,10):d.text(((x-(240 if FULL else 330))*6,2),str(x),fill='white')
    for z in range(-210 if FULL else -180,-49 if FULL else 11,10):d.text((2,(z+(210 if FULL else 180))*6),str(z),fill='white')
    im.save(OUT/'plan.png')
    print('Snapshot',snapshot,'blocks',len(selected))
if __name__=='__main__':main()
