from pathlib import Path
from PIL import Image
import json,re,math,hashlib,os
B=Path(__file__).resolve().parent;R=B.parent
S=R/'batch-06/sources/dercodeKoenig__marvins-minecraft-mods/aw_vehicles/src/main/java/Vehicles'
A=B/'reference-assets/aw_vehicles/src/main/resources/assets/aw_vehicles/textures/entity'
results=[]
number=r'(-?\d+(?:\.\d+)?)[fF]?'
pattern=re.compile(r'\.texOffs\(\s*'+number+r'\s*,\s*'+number+r'\s*\)\s*\.addBox\(\s*'+r'\s*,\s*'.join([number]*6)+r'\s*\)')
for java,png in [('BallistaRenderer.java','ballista_stand_3.png'),('BallistaBoltRenderer.java','arrow_wood.png')]:
 p=S/java;text=p.read_text();im=Image.open(A/png).convert('RGBA');W,H=im.size;records=[]
 declared=re.search(r'LayerDefinition.create\(mesh,\s*(\d+),\s*(\d+)\)',text)
 for i,m in enumerate(pattern.finditer(text),1):
  u,v,x,y,z,w,h,d=map(float,m.groups());line=text.count('\n',0,m.start())+1
  faces={'down':[u+d,v,u+d+w,v+d],'up':[u+d+w,v,u+d+2*w,v+d],'west':[u,v+d,u+d,v+d+h],'north':[u+d,v+d,u+d+w,v+d+h],'east':[u+d+w,v+d,u+2*d+w,v+d+h],'south':[u+2*d+w,v+d,u+2*d+2*w,v+d+h]}
  checked=[]
  for name,box in faces.items():
   x0,y0,x1,y1=box;points=[(ix,iy) for iy in range(math.floor(y0),math.ceil(y1)) for ix in range(math.floor(x0),math.ceil(x1)) if x0<=ix+.5<x1 and y0<=iy+.5<y1]
   valid=[pt for pt in points if 0<=pt[0]<W and 0<=pt[1]<H]
   values=[im.getpixel(pt) for pt in valid]
   checked.append(dict(face=name,uv_bounds=box,in_atlas=0<=x0<=x1<=W and 0<=y0<=y1<=H,pixel_centres=len(points),transparent=sum(c[3]==0 for c in values),opaque=sum(c[3]==255 for c in values),visible_colours=len({c for c in values if c[3]>0})))
  records.append(dict(cuboid=i,source_line=line,tex_offs=[u,v],dimensions=[w,h,d],faces=checked))
 pixels=list(im.get_flattened_data());transparent=sum(c[3]==0 for c in pixels)
 results.append(dict(source=os.path.relpath(p,B),texture=str((A/png).relative_to(B)),texture_sha256=hashlib.sha256((A/png).read_bytes()).hexdigest(),actual_dimensions=[W,H],declared_dimensions=[int(declared[1]),int(declared[2])],dimensions_match=[W,H]==[int(declared[1]),int(declared[2])],transparent_pixels=transparent,magenta_rgb_alpha_zero=sum(c==(255,0,255,0) for c in pixels),partial_alpha=sum(0<c[3]<255 for c in pixels),parsed_cuboids=len(records),addBox_occurrences=text.count('.addBox('),all_cuboids_parsed=len(records)==text.count('.addBox('),all_face_bounds_in_atlas=all(f['in_atlas'] for c in records for f in c['faces']),fully_transparent_face_samples=[dict(cuboid=c['cuboid'],line=c['source_line'],face=f['face'],samples=f['pixel_centres']) for c in records for f in c['faces'] if f['pixel_centres']>0 and f['opaque']==0],cuboids=records))
report=dict(method='Read-only literal texOffs/addBox unfolding following exact Forge47.3.0 ModelPart.Cube/Polygon. Pixel-centre alpha diagnostics, no raster rewrite or production asset copy. This is not actual GPU filtering/animation or shader alpha validation.',results=results,new_reference_credit=0)
(B/'atlas-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k not in ['cuboids','fully_transparent_face_samples']}|{'fully_transparent_face_samples':len(r['fully_transparent_face_samples'])} for r in results],ensure_ascii=False))
