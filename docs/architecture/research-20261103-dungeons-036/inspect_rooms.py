"""Inspect hall layers, tower ladder and real upper-tip states, without assembly."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image,ImageDraw

OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
spec=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
details=importlib.util.module_from_spec(spec);spec.loader.exec_module(details)

def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    c=json.loads((OUT/'sources.json').read_text())['candidates'][0]
    with ZipFile(c['source_archive']) as z:
        raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256'];d=read(raw)
        pal=d.get('palette') or d['palettes'][0]
        states={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
        cs={p:s for p,s in states.items() if s['Name'] not in AIR}
        author=[]
        for member in z.namelist():
            if '/worldgen/structure/' not in member or not member.endswith('.json'):continue
            content=z.read(member);value=json.loads(content)
            if value.get('start_pool')=='terralith:village/fortified/starts':
                author.append(dict(member=member,sha256=sha(content),data=value))
        manifest=z.read('META-INF/mods.toml')
    sx,sy,sz=d['size'];cuts=[('y',5,sx,sz),('y',9,sx,sz),('x',22,sz,sy),('z',4,sx,sy)]
    im=Image.new('RGB',(1440,1480),'#edf0f2');draw=ImageDraw.Draw(im)
    for i,(axis,fixed,width,height) in enumerate(cuts):
        left=(i%2)*720+45;top=(i//2)*710+60;step=min(640/width,620/height)
        draw.text((left,top-40),f'F01 hall/tower {axis}={fixed}',fill='#17252c')
        for v in range(height):
            for h in range(width):
                p=(h,fixed,v) if axis=='y' else (fixed,v,h) if axis=='x' else (h,v,fixed)
                row=v if axis=='y' else height-1-v
                xx,yy=left+h*step,top+row*step
                draw.rectangle((xx,yy,xx+step,yy+step),fill=details.shade(cs.get(p)),outline='#bfc6ca')
        for h in range(0,width,5):draw.text((left+h*step,top-17),str(h),fill='#17252c')
        for v in range(0,height,5):
            row=v if axis=='y' else height-1-v
            draw.text((left-23,top+row*step),str(v),fill='#17252c')
    draw.text((20,1433),'Original occupied cells / class colours / cyan ladder / purple door / explicit air and omitted merged',fill='#17252c')
    draw.text((20,1453),'No collision or native route solver; upper tip is not extra rooms; roads and residents not assembled',fill='#17252c')
    im.save(OUT/'F01-hall-tower.png')
    planes=[dict(y=y,original_states=[dict(position=list(p),state=s) for p,s in states.items() if p[1]==y]) for y in (5,9,23,24,25,26,27,28,29,30)]
    upper=[dict(y=y,nonair=sum(p[1]==y for p in cs),
                materials=dict(Counter(s['Name'] for p,s in cs.items() if p[1]==y)),
                horizontal_bounds=[[min(p[a] for p in cs if p[1]==y),max(p[a] for p in cs if p[1]==y)] for a in (0,2)]) for y in range(23,31)]
    evidence=dict(id='F01',nbt_sha256=c['nbt_sha256'],cuts=[dict(axis=a,coordinate=f,width=w,height=h) for a,f,w,h in cuts],
        original_horizontal_planes=planes,upper_occupied_profile=upper,author_structure_resources=author,
        manifest_sha256=sha(manifest),manifest_text=manifest.decode(),
        geometry_not_rebuilt=True,building_credit=0,native_routes_verified=False,actor_or_road_assembly=False)
    (OUT/'room-height-placement-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print('Author configs',[r['member'] for r in author]);print('Upper profile',upper)

if __name__=='__main__':main()
