#!/usr/bin/env python3
"""Read local reference templates and draw candidates for manual whole-building review.

This never awards reference credit. Cubes approximate block states: stairs, slabs,
fences and foliage are not native meshes or collision shapes. No game assets are
written, no Java is launched, and no source template is extracted.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

from nbt_read import read
from reference_components import geometry_hash, role

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ('trek', '*远足]*.jar', 'https://modrinth.com/datapack/trek'),
    ('kaisyn', '*城镇与塔楼]*.jar', 'https://www.curseforge.com/minecraft/mc-mods/towns-and-towers'),
    ('terralith', '*地形生成]Terralith*.jar', 'https://github.com/Stardust-Labs-MC/Terralith'),
    ('goetyawaken', '*诡厄巫法觉醒]*.jar', 'https://github.com/k1sak1/goetyawaken'),
]
AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air', 'minecraft:structure_void'}


def color(name):
    if 'jigsaw' in name: return (194, 85, 218)
    if 'spawner' in name: return (211, 60, 60)
    if any(k in name for k in ('chest', 'barrel')): return (222, 145, 39)
    if any(k in name for k in ('leaf', 'leaves', 'moss', 'grass', 'vine')): return (103, 134, 78)
    if any(k in name for k in ('water', 'ice')): return (91, 159, 192)
    if 'lava' in name: return (232, 111, 38)
    if any(k in name for k in ('torch', 'lantern', 'glowstone')): return (241, 203, 92)
    if 'sandstone' in name or 'sand' in name: return (207, 188, 137)
    if 'brick' in name and not any(k in name for k in ('stone', 'deepslate', 'blackstone', 'nether')): return (164, 103, 84)
    if any(k in name for k in ('log', 'wood', 'planks', 'fence', 'trapdoor', 'door')): return (148, 114, 77)
    if any(k in name for k in ('quartz', 'snow', 'calcite', 'white', 'bone')): return (217, 217, 204)
    if 'glass' in name: return (145, 196, 198)
    if any(k in name for k in ('blackstone', 'deepslate', 'obsidian')): return (82, 83, 99)
    if 'dirt' in name or 'podzol' in name: return (135, 113, 87)
    return (150, 153, 154)


def iso(cells, size, rotation, title, cutoff=None):
    sx, sy, sz = size
    if rotation:
        cells = {(sz-1-z, y, x): n for (x,y,z),n in cells.items()}
        sx, sz = sz, sx
    cells = {p:n for p,n in cells.items() if cutoff is None or p[1] <= cutoff}
    panel = Image.new('RGB', (760, 680), '#edf0f2')
    d = ImageDraw.Draw(panel)
    d.text((18, 12), title, fill='#17252c')
    scale = min(660 / max(1,sx+sz), 570 / max(1,(sx+sz)*.5+sy))
    origin=(380 + (sz-sx)*scale*.5, 70+sy*scale)
    def project(p):
        x,y,z=p
        return (origin[0]+(x-z)*scale, origin[1]+(x+z)*scale*.5-y*scale)
    for (x,y,z),name in sorted(cells.items(), key=lambda it:(sum(it[0]),it[0][1])):
        c=color(name)
        faces=[((0,1,0),[(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)],1.12),
               ((1,0,0),[(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)],.82),
               ((0,0,1),[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)],.66)]
        for (dx,dy,dz),face,shade in faces:
            if (x+dx,y+dy,z+dz) in cells: continue
            d.polygon([project(p) for p in face], fill=tuple(min(255,round(v*shade)) for v in c))
    return panel


def plans(cells, size, level, ident):
    """Two coordinate-preserving horizontal sections; omissions remain grey."""
    sx,sy,sz=size
    img=Image.new('RGB',(1520,800),'#edf0f2'); d=ImageDraw.Draw(img)
    step=min(660/max(sx,1),650/max(sz,1))
    for col,y in enumerate((level,level+1)):
        left=col*760+45; top=60
        d.text((left,15),f'{ident}: horizontal section y={y}; +X right, +Z down',fill='#17252c')
        for x in range(sx):
            for z in range(sz):
                n=cells.get((x,y,z)); c=color(n) if n else (227,230,233)
                d.rectangle((left+x*step,top+z*step,left+(x+1)*step,top+(z+1)*step),fill=c,outline='#bfc6ca')
        for x in range(0,sx,5): d.text((left+x*step,top-18),str(x),fill='#17252c')
        for z in range(0,sz,5): d.text((left-22,top+z*step),str(z),fill='#17252c')
    d.text((24,755),'MAGENTA jigsaw / ORANGE storage / RED spawner / GREY empty or omitted / cube states, not collision',fill='#17252c')
    return img


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mods', required=True, type=Path)
    ap.add_argument('--batch', type=int, choices=(1,2,3), default=1)
    ap.add_argument('--output', type=Path, default=ROOT/'docs/architecture/continuation-20261022/references/whole-candidates')
    args=ap.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    rows=[]
    sources = SOURCES if args.batch == 1 else [
        ('ati_structures', '*ATi*jar', 'https://www.curseforge.com/minecraft/mc-mods/ati-structures'),
        ('simply_houses', '*简易房屋*jar', 'https://www.curseforge.com/minecraft/mc-mods/simply-houses'),
        ('terralith', '*地形生成]Terralith*.jar', 'https://github.com/Stardust-Labs-MC/Terralith'),
    ]
    if args.batch == 3:
        sources=[('repurposed_structures','*结构变体*jar','https://github.com/TelepathicGrunt/RepurposedStructures')]
    if args.batch != 1 and args.output.name == 'whole-candidates':
        raise ValueError('Additional batches require a separate --output directory')
    for namespace,pattern,url in sources:
        matches=list(args.mods.glob(pattern))
        if len(matches)!=1: raise ValueError((pattern,matches))
        jar=matches[0]
        jar_hash=hashlib.sha256(jar.read_bytes()).hexdigest()
        with ZipFile(jar) as z:
            pools={n:json.loads(z.read(n)) for n in z.namelist() if '/worldgen/template_pool/' in n and n.endswith('.json')}
            for member in sorted(z.namelist()):
                if '/structures/' not in member or not member.endswith('.nbt'): continue
                if args.batch == 1:
                    if not any(k in member for k in ('church', 'temple', 'mausoleum', 'graveyard')): continue
                elif args.batch == 3:
                    if '/structures/villages/' not in member or 'temple' not in member: continue
                elif not ((namespace=='ati_structures' and 'temple' in member) or
                          (namespace in ('simply_houses','terralith') and 'chapel' in member)):
                    continue
                if namespace=='kaisyn' and '/houses/' not in member: continue
                if namespace=='goetyawaken' and member.rsplit('/',1)[-1] not in ('the_mausoleum.nbt','tidal_tomb.nbt','temple_of_apollyon.nbt'): continue
                raw=z.read(member); nbt=read(raw)
                palette=nbt.get('palette') or nbt.get('palettes',[[]])[0]
                cells={tuple(b['pos']):palette[b['state']]['Name'] for b in nbt.get('blocks',[]) if palette[b['state']]['Name'] not in AIR}
                if not cells: continue
                sockets=[{'position':b['pos'], 'state':palette[b['state']], 'data':b.get('nbt',{})} for b in nbt.get('blocks',[]) if palette[b['state']]['Name']=='minecraft:jigsaw']
                loc=namespace+':'+member.split('/structures/',1)[1][:-4]
                refs=[n for n,v in pools.items() if loc in json.dumps(v)]
                ident=f'{ {1:"W",2:"B",3:"C"}[args.batch]}{len(rows)+1:03d}'
                doors=[{'position':b['pos'],'state':palette[b['state']]} for b in nbt.get('blocks',[]) if palette[b['state']]['Name'].endswith('_door') and palette[b['state']].get('Properties',{}).get('half')=='lower']
                door_levels=Counter(b['position'][1] for b in doors)
                level=max(door_levels,key=lambda y:(door_levels[y],-y)) if door_levels else min(y for x,y,z in cells)+1
                size=nbt['size']; cutoff=max(1,round(size[1]*.4))
                sheet=Image.new('RGB',(1520,1400),'#edf0f2')
                sheet.paste(iso(cells,size,0,ident+' '+member.rsplit('/',1)[-1]),(0,0))
                sheet.paste(iso(cells,size,1,'Quarter turn; complete stored volume'),(760,0))
                sheet.paste(iso(cells,size,0,f'Cutaway y <= {cutoff}',cutoff),(0,680))
                sheet.paste(iso(cells,size,1,f'Quarter turn cutaway y <= {cutoff}',cutoff),(760,680))
                ImageDraw.Draw(sheet).text((18,1372),'OFFLINE REFERENCE / cube approximation / not native placement or collision / no automatic full-building credit',fill='#17252c')
                image_name=ident+'.png'; sheet.save(args.output/image_name)
                low=Image.new('RGB',(1520,680),'#edf0f2')
                low.paste(iso(cells,size,0,f'{ident}: entrance-level cutaway y <= {level+1}',level+1),(0,0))
                low.paste(iso(cells,size,1,f'{ident}: entrance-level quarter turn',level+1),(760,0))
                low.save(args.output/(ident+'-low.png'))
                plans(cells,size,level,ident).save(args.output/(ident+'-plan.png'))
                rows.append(dict(id=ident,source_url=url,source_jar=str(jar),source_jar_sha256=jar_hash,member=member,nbt_sha256=hashlib.sha256(raw).hexdigest(),size=size,
                                 material_independent_geometry_sha256=geometry_hash({p:role(n) for p,n in cells.items()},size),
                                 material_counts=dict(Counter(cells.values())),sockets=sockets,pool_references=refs,image=image_name,doors=doors,entrance_level=level,plan_image=ident+'-plan.png',low_cutaway_image=ident+'-low.png',
                                 status='UNREVIEWED_CANDIDATE_NOT_CREDITED'))
    (args.output/'candidates.json').write_text(json.dumps({'schema':1,'automatic_credit':0,'candidates':rows},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'candidates':len(rows),'output':str(args.output),'automatic_credit':0}))


if __name__=='__main__': main()
