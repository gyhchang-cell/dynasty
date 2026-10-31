"""Same-camera actual PNG/UV comparisons; offline images are NOT game captures."""
from pathlib import Path
import ast, hashlib, importlib.util, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'src/main/resources/assets/dynasty'
OUT=ROOT/'docs/art/bestiary-v43/wood-kite'
spec=importlib.util.spec_from_file_location('wood_geometry',ROOT/'tools/art/secondary-cuboid/review_models.py')
geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry);geometry.CATEGORY='blueprint/boss'
source=(ROOT/'tools/art/boss-forms/texture_review.py').read_text()
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef) and node.name in ('cuboid','references','raster'):
  function_source=ast.get_source_segment(source,node)
  if node.name=='raster':
   # Coplanar pre-existing faces differ only by floating-point roundoff. Give
   # equal-depth fragments a deterministic first-wins order in this offline
   # renderer; this is NOT a geometry fix or evidence of native GL behaviour.
   function_source=function_source.replace('(zz>old)','(zz>old+1e-7)')
  exec(function_source,globals())
r=geometry
font=lambda n:ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',n)

def label(im,text):
 output=Image.new('RGB',(im.width,im.height+50),'#e8e9e4');output.paste(im,(0,50))
 ImageDraw.Draw(output).text((14,12),text,font=font(19),fill='#2a3435')
 return output

def q(ident,clip='idle',tick=0,before=False):
 return geometry.geometry(ident,clip='animation.luban_yisha.'+clip,tick=tick,
  geo_path=OUT/'before'/(ident+'.geo.json') if before else None,
  animation_path=OUT/'before'/(ident+'.animation.json') if before else None)

def image(ident,angle=45,mode='unlit',before=False,clip='idle',tick=0,size=(1400,720),bones=None,checker=None,frame_points=None):
 quads=q(ident,clip,tick,before)
 atlas=np.array(Image.open((OUT/'before' if before else ASSET/'textures/entity/blueprint/boss')/(ident+'.png')).convert('RGB'))
 if checker is not None:atlas=checker
 if bones:
  quads=[item for item in quads if any(key in item[2] for key in bones)]
  return raster(quads,atlas,yaw=angle,elevation=8,size=size,mode=mode)
 return raster(quads+references(np.array([-100,0,-12])),atlas,yaw=angle,elevation=8,size=size,mode=mode,frame_points=frame_points)

def uv_checks(ident):
 out=OUT/ident;tex=Image.open(out/'texture.png').convert('RGB');overlay=tex.resize((1024,1024),Image.Resampling.NEAREST)
 check=Image.new('RGB',tex.size,'#252d30');d=ImageDraw.Draw(check);od=ImageDraw.Draw(overlay)
 islands=json.loads((out/'uv-islands.json').read_text())
 for i,p in enumerate(islands):
  x,y,w,h=p['rect'];tile=Image.new('RGB',(w,h));td=ImageDraw.Draw(tile)
  for yy in range(h):
   for xx in range(w):
    color=[(185,67,63),(88,162,93),(71,117,183),(198,165,68)][2*(yy>=h/2)+(xx>=w/2)]
    if (xx//4+yy//4)%2:color=tuple(max(0,c-20)for c in color)
    tile.putpixel((xx,yy),color)
  if w>=10 and h>=10:
   td.text((1,1),str(i),font=ImageFont.load_default(size=8),fill='white')
   td.line((1,h-3,w-3,h-3),fill='white');td.line((w-5,h-5,w-3,h-3,w-5,h-1),fill='white')
  check.paste(tile,(x,y));od.rectangle((2*x,2*y,2*(x+w)-1,2*(y+h)-1),outline='#df6a9e')
 check.save(out/'uv-checker.png');overlay.save(out/'uv-overlay-2x.png')
 return np.array(check)

def main():
 verification={}
 for ident in ('luban_yisha','luban_yisha_metal'):
  out=OUT/ident
  for angle,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
   for mode in ('unlit','lit'):
    image(ident,angle,mode).save(out/f'{name}-{mode}.png')
   for before,word in [(True,'before'),(False,'after')]:
    image(ident,angle,'unlit',before=before).save(out/f'{name}-{word}.png')
   comparison=Image.new('RGB',(2800,770),'#e8e9e4')
   comparison.paste(label(Image.open(out/f'{name}-before.png'),'修改前 · 原PNG逐面采样'),(0,0))
   comparison.paste(label(Image.open(out/f'{name}-after.png'),'修改后 · 同形体 / 同机位 / 同尺度 · 原色'),(1400,0))
   comparison.save(out/f'comparison-{name}.png')
  for label_,names,angle in [('head',['eagle_tool_head','focusing_lens','shear_beak','forehead'],45),('wing',['left_redwood_vanes','left_folding_rail','left_wing_bearing'],45),('motor',['oil_jet_','engine_','gear_'],45)]:
   label(image(ident,angle,'lit',bones=names,size=(1000,700)),label_+' / 实际PNG和现有部件 · 软件近景').save(out/(label_+'-detail.png'))
  for mode in ('gray','dim'):
   image(ident,45,mode).save(out/(mode+'.png'))
  checker=uv_checks(ident)
  image(ident,45,'unlit',checker=checker).save(out/'uv-direction.png')
  image(ident,90,'unlit',checker=checker).save(out/'uv-direction-side.png')
  # Full clip coverage, including pre-contact and recovery; no damage timing edit.
  data=json.loads((ASSET/f'animations/blueprint/boss/{ident}.animation.json').read_text())['animations']
  motions=[]
  for clip in ('fly','wing_cut','claws','bombs'):
   duration=data['animation.luban_yisha.'+clip]['animation_length'];frames=[]
   times=np.linspace(0,duration*20,24)
   # One camera scale for the WHOLE clip; autosizing every frame would conceal
   # translation and exaggerate the size of folded / unfolded wings.
   fixed_points=np.concatenate([points for t in times for points,_,_ in q(ident,clip,float(t))+references(np.array([-100,0,-12]))])
   for tick in times:
    frames.append(label(image(ident,45,'lit',clip=clip,tick=float(tick),size=(900,520),frame_points=fixed_points),f'{clip} / {tick:.1f} tick · 完整原动作软件回放'))
   frames[0].save(out/(clip+'.webp'),save_all=True,append_images=frames[1:],duration=max(20,round(duration*1000/23)),loop=0,lossless=True)
   strip=Image.new('RGB',(1440,6*228),'#e8e9e4')
   for i,frame in enumerate(frames):strip.paste(frame.resize((360,228),Image.Resampling.NEAREST),((i%4)*360,(i//4)*228))
   strip.save(out/(clip+'-frames.png'))
   motions.append(dict(clip=clip,length_seconds=duration,samples=24,file=clip+'.webp'))
   print(ident,clip,'full offline clip',flush=True)
  verification[ident]=dict(render='Actual runtime PNG and per-face UV, nearest sampling, no particles/emission. Software only.',
   views=['front','45','side','back'],modes=['unlit','basic diffuse','gray','dim'],motions=motions,
   animation_camera='fixed across all24 samples of each full clip',
   source_geometry_and_action_unchanged=True,game_test='pending',
   coplanar_preview='Equal-depth floating-point raster speckles fixed locally; no runtime geometry edit and no claim about native GL coplanar rendering.')
 (OUT/'preview-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
 print('Both existing forms previewed; no Java, game, focus, sound or brightness changes.')

if __name__=='__main__':main()
