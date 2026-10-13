"""Rasterize actual production UV triangles against current PNG. Software, never game evidence."""
from pathlib import Path
import importlib.util, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/art/dragon-decal-v1'
spec = importlib.util.spec_from_file_location('dragon_texture', Path(__file__).with_name('make_texture.py'))
source = importlib.util.module_from_spec(spec); spec.loader.exec_module(source)
texture = Image.open(ROOT / 'src/main/resources/assets/dynasty/textures/effect/dragon_slayer_decal.png').convert('RGBA')
expected = Image.new('RGBA', (16, 16))
expected.putdata([source.PALETTE[c] for row in source.CELLS for c in row])
assert texture.tobytes() == expected.resize((32, 32), Image.Resampling.NEAREST).tobytes(), 'PNG drift'
pix = np.array(texture)
assert set(map(tuple, pix.reshape(-1, 4))) == set(source.PALETTE.values())
assert not pix[:2, :, 3].any() and not pix[-2:, :, 3].any() and not pix[:, :2, 3].any() and not pix[:, -2:, 3].any()
metadata = json.loads((ROOT / 'src/main/resources/assets/dynasty/textures/effect/dragon_slayer_decal.png.mcmeta').read_text())
assert metadata == {'texture': {'blur': False, 'clamp': True}}
data = json.loads((OUT / 'actual-triangles.json').read_text())
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)

def render(frame, yaw=0, mode='color', fade=False):
    bg = np.array([224, 222, 211], dtype=float)
    canvas = np.empty((280, 280, 3), dtype=float); canvas[:] = bg
    zbuffer = np.full((280, 280), -np.inf)
    theta = np.deg2rad(yaw); co, si = np.cos(theta), np.sin(theta)
    for t in frame['triangles']:
        vertices = [t[k] for k in ('a', 'b', 'c')]
        pts = np.array([v['xyz'] for v in vertices]); uv = np.array([v['uv'] for v in vertices])
        xy = np.stack([140 + (pts[:, 0]*co + pts[:, 2]*si)*200, 140 - pts[:, 1]*200], axis=1)
        depth = -pts[:, 0]*si + pts[:, 2]*co
        a,b,c = xy
        den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-6: continue
        lo = np.maximum(0, np.floor(xy.min(axis=0)).astype(int)); hi = np.minimum(279, np.ceil(xy.max(axis=0)).astype(int))
        for y in range(lo[1], hi[1]+1):
            for x in range(lo[0], hi[0]+1):
                xx, yy = x+.5, y+.5
                w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
                w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den; w2=1-w0-w1
                if min(w0,w1,w2)<-1e-9: continue
                w=np.array([w0,w1,w2]); z=w@depth
                if z<zbuffer[y,x]:continue
                u,v=w@uv; tx=min(31,max(0,int(u*32))); ty=min(31,max(0,int(v*32))); rgba=pix[ty,tx]
                if rgba[3]==0: continue
                color = np.array([0,0,0] if mode=='black' else [122,126,126] if mode=='gray' else rgba[:3], dtype=float)
                alpha=t['alpha'] if fade else 1
                canvas[y,x]=color*alpha+bg*(1-alpha); zbuffer[y,x]=z
    return Image.fromarray(np.rint(canvas).astype('uint8'))

views=[('front',0,'color'),('45',45,'color'),('right edge',90,'color'),('left edge',-90,'color'),('back',180,'color'),('black',45,'black'),('gray',45,'gray')]
sheet=Image.new('RGB',(280*7,370),(224,222,211));draw=ImageDraw.Draw(sheet)
draw.text((15,12),'DRAGON DECAL / ACTUAL JAVA TRIANGLES + NEAREST32 PNG / OPAQUE SOFTWARE DIAGNOSTICS',font=font,fill=(30,31,30))
draw.text((15,35),'Fixed world scale: 200px/block. Surface decal is intentionally edge-on invisible; back is mirrored. Not a creature model or game screenshot.',font=font,fill=(30,31,30))
for i,(name,yaw,mode) in enumerate(views):
    sheet.paste(render(data['frames'][0],yaw,mode),(280*i,70)); draw.text((280*i+10,350),name,font=font,fill=(30,31,30))
sheet.save(OUT/'software-views.png')
sheet=Image.new('RGB',(280*6,370),(224,222,211));draw=ImageDraw.Draw(sheet)
draw.text((15,15),'DRAGON DECAL / ACTUAL12T FADE / SOFTWARE ALPHA OVER FLAT BACKGROUND; NOT GL ACCEPTANCE',font=font,fill=(30,31,30))
for i,frame in enumerate(data['frames']):
    sheet.paste(render(frame,fade=True),(280*i,70));draw.text((280*i+10,350),'t='+str(frame['age']),font=font,fill=(30,31,30))
sheet.save(OUT/'software-timeline.png')
(OUT/'texture-validation.json').write_text(json.dumps({'dimensions':[32,32],'opaqueColors':3,'hardCells':2,'transparentBorderPixels':2,'exactRegeneration':True,'nearestMcmeta':True,'geometrySource':'actual DragonDecal.geometry + current PNG; software only'},indent=2)+'\n')
print('PASS original PNG regeneration, palette/margins/nearest; actual textured triangle views and fade; native PENDING')
