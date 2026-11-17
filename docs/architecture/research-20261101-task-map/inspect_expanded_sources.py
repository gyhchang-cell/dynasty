#!/usr/bin/env python3
"""Targeted re-study of three previously excluded buildings after scope expansion.

Existing review decisions and formal registry remain unchanged. New sections are
research evidence only; rendering does not instantiate a dungeon or award credit.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from PIL import Image,ImageDraw

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,color,plans

OLD=ROOT/'docs/architecture/continuation-20261022/references/whole-candidates-004'
LEVELS={'D001':[1,16],'D011':[],'D012':[9,24]}


def vertical(cells,size,ident):
    sx,sy,sz=size
    image=Image.new('RGB',(1520,1100),'#edf0f2'); draw=ImageDraw.Draw(image)
    for col,(axis,fixed,width) in enumerate((('z',sz//2,sx),('x',sx//2,sz))):
        step=min(650/width,930/sy)
        left=col*760+45; top=65
        draw.text((left,18),f'{ident}: vertical section {axis}={fixed}; height up',fill='#17252c')
        for y in range(sy):
            for horizontal in range(width):
                pos=(horizontal,y,fixed) if axis=='z' else (fixed,y,horizontal)
                n=cells.get(pos)
                x0=left+horizontal*step; y0=top+(sy-1-y)*step
                draw.rectangle((x0,y0,x0+step,y0+step),fill=color(n) if n else '#e3e6e9',outline='#bfc6ca')
        for y in range(0,sy,5):draw.text((left-23,top+(sy-1-y)*step),str(y),fill='#17252c')
    draw.text((20,1045),'RESEARCH: stored states only / generic color / full-cell approximation / not generated terrain or collision',fill='#17252c')
    return image


def main():
    old=json.loads((OLD/'candidates.json').read_text())
    review=json.loads((OLD/'review-batch-004.json').read_text())
    rows=[]; archives={}
    for c in old['candidates']:
        ident=c['id']
        if ident not in LEVELS:continue
        archive=Path(c['source_jar'])
        if str(archive) not in archives:
            archives[str(archive)]=hashlib.sha256(archive.read_bytes()).hexdigest()
        with ZipFile(archive) as z:
            raw=z.read(c['member'])
            assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
            d=read(raw);pal=d.get('palette') or d['palettes'][0]
            cells={tuple(b['pos']):pal[b['state']]['Name'] for b in d['blocks'] if pal[b['state']]['Name'] not in AIR}
            pool_data=[dict(member=n,data=json.loads(z.read(n))) for n in c['pool_references']]
        images=[]
        for level in LEVELS[ident]:
            name=f'{ident}-expanded-y{level}.png';plans(cells,d['size'],level,ident).save(OUT/name);images.append(name)
        name=f'{ident}-expanded-vertical.png';vertical(cells,d['size'],ident).save(OUT/name);images.append(name)
        # Positions of vertical connectors and physical entrance shapes support
        # the visual review without treating doors' most common floor as entry.
        connector=[dict(position=b['pos'],state=pal[b['state']]) for b in d['blocks']
            if any(k in pal[b['state']]['Name'] for k in ('ladder','stairs','door','gate','chain','carpet'))]
        entities=[dict(pos=e.get('pos'),block_pos=e.get('blockPos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]
        rows.append(dict(id=ident,source_archive=str(archive),source_archive_sha256=archives[str(archive)],
            source_member=c['member'],nbt_sha256=c['nbt_sha256'],publisher_url=c.get('source_url'),size=d['size'],
            previous_review_reason=review['not_credited'][ident],previous_formal_credit=0,
            previous_whole_image=str(OLD/c['image']),previous_plan_image=str(OLD/c['plan_image']),
            new_research_images=images,sockets=c['sockets'],pool_data=pool_data,
            vertical_and_opening_states=connector,entities=entities,
            layer_counts=dict(sorted(Counter(p[1] for p in cells).items())),formal_new_credit=0))
        print(ident,'new sections',len(images),'entities',len(entities),'connectors',len(connector))
    (OUT/'scope-expansion-sources.json').write_text(json.dumps(dict(reason='用户新增cod2十座地牢范围，针对原先仅因规模/用途排除的3例重新审相关性；不是新发现或重复计数',candidates=rows,formal_new_credit=0),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
