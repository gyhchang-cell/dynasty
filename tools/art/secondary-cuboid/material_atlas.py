"""Original per-face material atlases for three already nonhuman secondary rigs.

The user's 2026-10-11 modeling requirements (19.3, 20, 26.13) supersede the
historical four-color portrait policy for these three targets. Geometry and
animations are preserved. Called by pixel16.export so regeneration stays valid.
"""
import copy
import hashlib
import io
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

IDS = {'clockwork_rat', 'wooden_magpie', 'stone_sprite'}
PALETTE = {
    'wood': ('#93653e', '#5a402b', '#c29258'),
    'brass': ('#aa8950', '#705e3e', '#d0b77a'),
    'iron': ('#667479', '#3d4b50', '#9ca9a8'),
    'stone': ('#7e8584', '#525d60', '#b1b6ac'),
    'moss': ('#66734f', '#46553d', '#8b9a65'),
    'eye': ('#bddbce', '#4c786b', '#e0eed5'),
    'dark': ('#29343a', '#29343a', '#29343a'),
}


def material(id, bone, index):
    if id == 'stone_sprite':
        if bone == 'head' and index in (1, 2): return 'dark'
        if bone == 'head' and index in (3, 4): return 'eye'
        if bone == 'boulder' and index == 1: return 'moss'
        if bone.startswith('leg_'): return 'dark'
        return 'stone'
    if id == 'clockwork_rat':
        if bone == 'head': return ('wood', 'brass', 'dark', 'eye', 'eye')[index]
        if bone == 'body': return ('wood', 'brass', 'iron', 'iron')[index]
        if bone == 'key': return 'brass'
        if bone == 'ears': return 'brass'
        if bone.startswith(('tail', 'leg_', 'foot_')): return 'iron'
        return 'brass' if bone == 'neck' else 'wood'
    if bone == 'head' and index: return 'dark'
    if bone == 'beak' or bone.endswith('_foot'): return 'iron'
    if bone == 'gears': return 'brass' if index == 0 else 'iron'
    if bone.endswith('_wing') and index == 1: return 'iron'
    if bone in ('breast', 'neck') or bone == 'body' and index == 1: return 'brass'
    if bone.endswith('_wingtip') and index == 0: return 'brass'
    if bone == 'tail' and index == 1: return 'iron'
    return 'wood'


def paint(key):
    mat, w, h, face, grain = key
    base, dark, light = PALETTE[mat]
    tile = Image.new('RGB', (w, h), base)
    d = ImageDraw.Draw(tile)
    if mat in ('eye', 'dark'): return tile
    # Sparse, authored hard edges; no random speckles or filtered gradients.
    if h >= 3: d.rectangle((0, h-1, w-1, h-1), fill=dark)
    if w >= 3 and face != 'down': d.rectangle((1, 0, w-2, 0), fill=light)
    if mat == 'wood':
        if grain == 'vertical' and w >= 5:
            d.rectangle((w//2, 1, w//2, max(1,h-2)), fill=dark)
        elif h >= 5:
            d.rectangle((1,h//2,max(1,w-2),h//2), fill=dark)
    elif mat in ('iron', 'brass'):
        if w >= 5 and h >= 5:
            d.rectangle((1,h-2,w-2,h-2), fill=dark)
            d.rectangle((1,1,1,1), fill=light)
            d.rectangle((w-2,1,w-2,1), fill=light)
    elif mat == 'stone' and w >= 6 and h >= 5:
        # A single stepped seam, leaving large calm rock surfaces.
        x=w//2
        d.rectangle((x,1,x,2), fill=dark)
        d.rectangle((x,3,min(w-2,x+1),3), fill=dark)
        d.rectangle((min(w-2,x+1),4,min(w-2,x+1),h-2), fill=dark)
    elif mat == 'moss' and w >= 4 and h >= 3:
        d.rectangle((0,0,w-1,1), fill=light)
        d.rectangle((0,2,max(1,w//3),h-1), fill=dark)
    return tile


def render(id, document):
    geo=copy.deepcopy(document)
    g=geo['minecraft:geometry'][0]
    tiles={}; faces=[]
    for b in g['bones']:
        for index,c in enumerate(b.get('cubes',[])):
            x,y,z=c['size']
            dims={'north':(x,y), 'south':(x,y), 'east':(z,y),
                  'west':(z,y), 'up':(x,z), 'down':(x,z)}
            for side in c['uv']:
                w,h=(max(1,math.ceil(v)) for v in dims[side])
                mat=material(id,b['name'],index)
                # Board fibers follow the long dimension on this physical face.
                key=(mat,w,h,side,'vertical' if h>w else 'horizontal')
                tiles.setdefault(key,paint(key));faces.append((c,side,key))
    # Two edge-extruded pixels around every unique UV island.
    placements=None
    for size in (64,128):
        placement={};x=y=2;row=0
        for key,tile in sorted(tiles.items(),key=lambda item:(-item[0][2],-item[0][1],item[0])):
            w,h=tile.size
            if x+w+2>size: x=2;y+=row;row=0
            if y+h+2>size: break
            placement[key]=(x,y);x+=w+4;row=max(row,h+4)
        else: placements=placement;break
    if placements is None: raise ValueError('Unexpected atlas overflow '+id)
    atlas=Image.new('RGB',(size,size),PALETTE['dark'][0])
    for key,tile in tiles.items():
        x,y=placements[key];w,h=tile.size
        # Extend exact edge colors, including all four corners. No resampling.
        for yy in range(-2,h+2):
            for xx in range(-2,w+2):
                atlas.putpixel((x+xx,y+yy),tile.getpixel((min(w-1,max(0,xx)),min(h-1,max(0,yy)))))
    for c,side,key in faces:
        c['uv'][side]={'uv':list(placements[key]),'uv_size':list(tiles[key].size)}
    g['description'].update(texture_width=size,texture_height=size)
    png=io.BytesIO();atlas.save(png,format='PNG')
    record={'atlas':[size,size], 'colors':len(atlas.getcolors(512)),
            'palette':['#%02x%02x%02x'%rgb for _,rgb in sorted(atlas.getcolors(512),key=lambda v:v[1])],
            'gutter':2, 'islands':len(tiles), 'faces':len(faces),
            'geometryChanged':id=='stone_sprite', 'animationsChanged':False,
            'policy':'2026-10-11 modeling requirements 19.3/20/26.13',
            'islandData':[{'material':k[0],'face':k[3],'uv':list(placements[k]),'size':list(tiles[k].size)} for k in placements]}
    return geo,png.getvalue(),record


def export_one(id, geo, asset):
    exported,png,record=render(id,geo)
    gp=asset/f'geo/secondary/{id}.geo.json';tp=asset/f'textures/entity/secondary/{id}.png'
    gp.write_text(json.dumps(exported,indent=2)+'\n');tp.write_bytes(png)
    return record


def main():
    from build_models import ASSET, REPO
    out=REPO/'docs/art/secondary-materials-v2';out.mkdir(parents=True,exist_ok=True)
    backup=REPO/'build/maintenance/secondary-materials-v2/before';backup.mkdir(parents=True,exist_ok=True)
    originals={};generated={};report={}
    for id in sorted(IDS):
        gp=ASSET/f'geo/secondary/{id}.geo.json';tp=ASSET/f'textures/entity/secondary/{id}.png'
        originals[gp]=gp.read_bytes();originals[tp]=tp.read_bytes()
        for p in (gp,tp,ASSET/f'animations/secondary/{id}.animation.json'):
            dest=backup/p.relative_to(ASSET);dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():dest.write_bytes(p.read_bytes())
        geo,png,record=render(id,json.loads(originals[gp]))
        generated[gp]=(json.dumps(geo,indent=2)+'\n').encode();generated[tp]=png
        report[id]=record
    # Preflight the full batch and check again per output to preserve parallel edits.
    for p,data in originals.items():
        if p.read_bytes()!=data:raise RuntimeError('Concurrent edit: '+str(p))
    for p,data in generated.items():
        if p.read_bytes()!=originals[p]:raise RuntimeError('Concurrent edit: '+str(p))
        temp=p.with_suffix(p.suffix+'.material-tmp');temp.write_bytes(data);temp.replace(p)
    for id in report:
        report[id]['sha256']={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in generated if p.stem.startswith(id)}
    (out/'atlases.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported original material atlases:', ', '.join(sorted(IDS)))


if __name__=='__main__':main()
