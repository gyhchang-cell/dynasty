#!/usr/bin/env python3
"""Offline Minecraft cuboid resource QA; reads assets, creates preview PNGs only.

Exact element coordinates, nearest-neighbor texture sampling, orthographic
projection and z-buffer. No texture artwork is created or modified here.
Supports model inheritance, texture aliases, implicit/explicit face UVs and
quarter-turn face rotations. Element rotations are rejected, not approximated.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT_ASSETS = HERE.parents[3] / 'src/main/resources/assets'
CANDIDATE_ASSETS = HERE.parent / 'candidate/assets'
NORMALS = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0),
           'east': (1, 0, 0), 'up': (0, 1, 0), 'down': (0, -1, 0)}
SHADE = {'north': .8, 'south': .8, 'west': .6, 'east': .6, 'up': 1., 'down': .5}


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def normalize(a):
    length = math.sqrt(dot(a, a))
    return tuple(x/length for x in a)


class Assets:
    def __init__(self, roots):
        self.roots = [Path(p) for p in roots]
        self.textures = {}
        self.used = set()

    def path(self, name, kind, suffix):
        namespace, relative = name.split(':', 1) if ':' in name else ('minecraft', name)
        for root in self.roots:
            path = root / namespace / kind / (relative + suffix)
            if path.exists():
                self.used.add(str(path))
                return path
        raise FileNotFoundError(f'{kind}/{name}{suffix} missing in {self.roots}')

    def model(self, name, seen=()):
        if name in seen:
            raise ValueError(f'Cyclic model parent: {seen} -> {name}')
        if name in ('minecraft:block/block', 'block/block'):
            return {'textures': {}}
        own = json.loads(self.path(name, 'models', '.json').read_text())
        inherited = self.model(own['parent'], (*seen, name)) if own.get('parent') else {'textures': {}}
        out = {**inherited, **own}
        out['textures'] = {**inherited.get('textures', {}), **own.get('textures', {})}
        return out

    def texture(self, name, aliases):
        seen = set()
        while name.startswith('#'):
            if name in seen:
                raise ValueError(f'Cyclic texture alias {name}')
            seen.add(name)
            name = aliases[name[1:]]
        if name not in self.textures:
            tex = Image.open(self.path(name, 'textures', '.png')).convert('RGBA')
            if tex.height != tex.width:
                raise ValueError(f'Animated/non-square atlas {name}: choose frame explicitly before QA')
            self.textures[name] = tex
        return self.textures[name]


def corners_and_default_uv(element, direction):
    """Corners follow UV order TL, TR, BR, BL in each face's own plane.

    These rects are Minecraft BlockElement.uvsByFace defaults. World projection:
      N=(16-x,16-y), S=(x,16-y), W=(z,16-y), E=(16-z,16-y),
      U=(x,z), D=(x,16-z).
    """
    x0, y0, z0 = element['from']
    x1, y1, z1 = element['to']
    face = {
        'north': ([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)], [16-x1,16-y1,16-x0,16-y0]),
        'south': ([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)], [x0,16-y1,x1,16-y0]),
        'west': ([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)], [z0,16-y1,z1,16-y0]),
        'east': ([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)], [16-z1,16-y1,16-z0,16-y0]),
        'up': ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)], [x0,z0,x1,z1]),
        'down': ([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)], [x0,16-z1,x1,16-z0]),
    }
    return face[direction]


def render(assets, model_name, eye, size=(176,168), scale=6.0):
    model = assets.model(model_name)
    facing = normalize(eye)
    reference_up = (0,0,-1) if abs(facing[1]) > .99 else (0,1,0)
    right = normalize(cross(reference_up, facing))
    camera_up = cross(facing, right)
    img = Image.new('RGBA', size, (0,0,0,0))
    pix = img.load()
    depths = [-float('inf')] * (size[0] * size[1])

    def project(v):
        centered = (v[0]-8, v[1]-7, v[2]-8)
        return (size[0]/2 + dot(centered,right)*scale,
                size[1]/2 - dot(centered,camera_up)*scale,
                dot(centered,facing))

    for element in model.get('elements', []):
        if element.get('rotation'):
            raise ValueError('Element rotation unsupported; do not approximate geometry')
        for direction, face in element['faces'].items():
            if dot(NORMALS[direction], facing) <= 1e-9:
                continue
            corners, default_uv = corners_and_default_uv(element, direction)
            u0,v0,u1,v1 = face.get('uv', default_uv)
            coords = [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
            rotation = face.get('rotation',0)
            if rotation not in (0,90,180,270):
                raise ValueError(f'Invalid face rotation {rotation}')
            # Minecraft face rotation advances texture corners by quarter turns.
            coords = coords[rotation//90:] + coords[:rotation//90]
            vertices = [(*project(v), *uv) for v,uv in zip(corners,coords)]
            texture = assets.texture(face['texture'], model['textures'])
            tx = texture.load()
            shade = SHADE[direction] if element.get('shade',True) else 1.0
            for indices in [(0,1,2),(0,2,3)]:
                a,b,c = [vertices[i] for i in indices]
                denom = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
                if abs(denom) < 1e-8:
                    continue
                xmin = max(0, math.floor(min(a[0],b[0],c[0])))
                xmax = min(size[0]-1, math.ceil(max(a[0],b[0],c[0])))
                ymin = max(0, math.floor(min(a[1],b[1],c[1])))
                ymax = min(size[1]-1, math.ceil(max(a[1],b[1],c[1])))
                for py in range(ymin,ymax+1):
                    for px in range(xmin,xmax+1):
                        sx,sy = px+.5,py+.5
                        wa = ((b[1]-c[1])*(sx-c[0]) + (c[0]-b[0])*(sy-c[1]))/denom
                        wb = ((c[1]-a[1])*(sx-c[0]) + (a[0]-c[0])*(sy-c[1]))/denom
                        wc = 1-wa-wb
                        if min(wa,wb,wc) < -1e-7:
                            continue
                        depth = wa*a[2]+wb*b[2]+wc*c[2]
                        index = py*size[0]+px
                        if depth <= depths[index]+1e-8:
                            continue
                        u = (wa*a[3]+wb*b[3]+wc*c[3])/16*texture.width
                        v = (wa*a[4]+wb*b[4]+wc*c[4])/16*texture.height
                        rgba = tx[max(0,min(texture.width-1,math.floor(u))),
                                  max(0,min(texture.height-1,math.floor(v)))]
                        if rgba[3] == 0:
                            continue
                        pix[px,py] = tuple(round(c*shade) for c in rgba[:3]) + (rgba[3],)
                        depths[index] = depth
    return img


def font(size):
    for path in ['/System/Library/Fonts/Menlo.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():
            return ImageFont.truetype(path,size)
    return ImageFont.load_default(size=size)


def background(size):
    im = Image.new('RGB',size,(230,229,221))
    d = ImageDraw.Draw(im)
    for y in range(0,size[1],16):
        for x in range(0,size[0],16):
            if ((x//16)+(y//16))%2:
                d.rectangle((x,y,x+15,y+15), fill=(220,220,211))
    return im


def compose(configurations, views, output, tile_size, scale, enlarge):
    render_width,render_height = tile_size
    cell_width = render_width*enlarge+24
    cell_height = render_height*enlarge+48
    canvas = Image.new('RGB',(len(configurations)*cell_width+24,len(views)*cell_height+142),(247,246,240))
    draw = ImageDraw.Draw(canvas)
    draw.text((18,12),'JADE MENDING FORGE | offline model preview / not game',font=font(18),fill=(38,47,46))
    draw.text((18,39),'Exact existing cuboids. Nearest texel sampling; no antialiasing.',font=font(13),fill=(60,67,64))
    for col,(title,asset,model) in enumerate(configurations):
        for row,(view_title,eye) in enumerate(views):
            x,y = 12+col*cell_width, 74+row*cell_height
            draw.text((x+9,y),title,font=font(16),fill=(38,47,46))
            draw.text((x+9,y+22),view_title,font=font(12),fill=(68,76,73))
            rgba = render(asset,model,eye,tile_size,scale)
            name = f'{col}_{row}_{model.split("/")[-1]}'
            rgba.save(output.parent/(output.stem+'_'+name+'.png'))
            preview = background((render_width*enlarge,render_height*enlarge))
            large = rgba.resize(preview.size,Image.Resampling.NEAREST)
            preview.paste(large,(0,0),large)
            canvas.paste(preview,(x+9,y+43))
    draw.text((18,canvas.height-40),'Offline orthographic QA: geometry + UV only; no game, collision, lighting or interaction test.',font=font(12),fill=(63,72,66))
    draw.text((18,canvas.height-21),'Original idle = lit. Candidate lit uses colored pixels; actual emission is unverified.',font=font(12),fill=(63,72,66))
    canvas.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-assets',type=Path,default=CANDIDATE_ASSETS)
    parser.add_argument('--before-assets',type=Path,default=HERE.parent/'before/assets')
    parser.add_argument('--project-assets',type=Path,default=PROJECT_ASSETS)
    parser.add_argument('--output',type=Path,default=HERE/'forge-model-comparison.png')
    parser.add_argument('--only-original',action='store_true')
    args = parser.parse_args()
    # Outputs are restricted to this delegated preview directory.
    if not args.output.resolve().is_relative_to(HERE):
        parser.error('--output must remain inside this renderer directory')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    before = Assets([args.before_assets,args.project_assets])
    after = Assets([args.candidate_assets,args.before_assets,args.project_assets])
    configurations = [('Original / idle = lit',before,'dynasty:block/jade_mending_forge')]
    if not args.only_original:
        # Require candidate files so fallback cannot silently label originals as candidates.
        for model in ['jade_mending_forge','jade_mending_forge_active']:
            if not (args.candidate_assets/'dynasty/models/block'/f'{model}.json').exists():
                parser.error(f'Candidate {model}.json is not ready in {args.candidate_assets}')
        configurations.extend([
            ('Candidate / idle',after,'dynasty:block/jade_mending_forge'),
            ('Candidate / lit',after,'dynasty:block/jade_mending_forge_active'),
        ])
    views = [('Front NORTH + WEST + TOP',(-1,1.05,-1.4)),
             ('Rear SOUTH + EAST + TOP',(1,1.05,1.4))]
    compose(configurations,views,args.output,(176,168),6.0,2)
    # Six orthographic views make each real UV projection directly inspectable.
    ortho = [('NORTH / front',(0,0,-1)),('SOUTH / rear',(0,0,1)),
             ('WEST / left',(-1,0,0)),('EAST / right',(1,0,0)),
             ('UP / top',(0,1,0)),('DOWN / underside',(0,-1,0))]
    compose(configurations,ortho,args.output.with_name('forge-six-face-comparison.png'),(128,118),6.0,2)
    manifest = {
        'purpose':'offline model preview / not game; no texture edits',
        'implicit_uv':{'north':['16-x','16-y'],'south':['x','16-y'],
                       'west':['z','16-y'],'east':['16-z','16-y'],
                       'up':['x','z'],'down':['x','16-z']},
        'geometry':[{'from':e['from'],'to':e['to']} for e in before.model('dynasty:block/jade_mending_forge')['elements']],
        'direction_shade':SHADE,
        'before_sources':sorted(before.used),
        'candidate_sources':sorted(after.used),
        'limitations':['not a Minecraft runtime render','no collision or behavior validation',
                       'no actual emissive/render layer verification','orthographic projection']}
    args.output.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(args.output)
    print(args.output.with_name('forge-six-face-comparison.png'))


if __name__ == '__main__':
    main()
