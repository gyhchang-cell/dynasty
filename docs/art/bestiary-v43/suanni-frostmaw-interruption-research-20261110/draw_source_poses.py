"""Same-scale source geometry diagrams; not textures or game rendering."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
B=Path(__file__).resolve().parent
scenes=json.loads((B/'diagram-geometry.json').read_text())
keys=['SLEEP@0','ACTIVATE_ANIMATION@36','ACTIVATE_ANIMATION@51']
vertices=[v for k in keys for boxes in scenes[k].values() for box in boxes for v in box]
zmin,zmax=min(v[2] for v in vertices),max(v[2] for v in vertices)
ymin,ymax=min(v[1] for v in vertices),max(24,max(v[1] for v in vertices))
scale=min(420/(zmax-zmin),400/(ymax-ymin))
im=Image.new('RGB',(1440,620),'#eeeae2');d=ImageDraw.Draw(im)
f=ImageFont.load_default(size=15);t=ImageFont.load_default(size=22)
d.text((20,15),'Frostmaw: source rigid body / same scale / NOT game',fill='#24323b',font=t)
d.text((20,48),'Nominal model plane only; terrain=0; assumed carried chest scale=1.1 for waking.',fill='#973d33',font=f)
faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
for column,key in enumerate(keys):
    left=480*column
    def point(v):return (left+30+(v[2]-zmin)*scale,100+(v[1]-ymin)*scale)
    floor=point([0,24,0])[1]
    d.line([(left+20,floor),(left+460,floor)],fill='#a6483d',width=2)
    polygons=[]
    for n,boxes in scenes[key].items():
        if n.startswith('eyeLid'):continue
        for box in boxes:
            for face in faces:
                vs=[box[i] for i in face];polygons.append((sum(v[0] for v in vs),n,vs))
    for _,n,vs in sorted(polygons):
        fill='#c4bd9f' if n in ('head','jaw') else '#7d919d' if n in ('leftFoot','rightFoot','leftHand','rightHand','leftFingers','rightFingers') else '#a5a7a4'
        d.polygon([point(v) for v in vs],fill=fill,outline='#454f55')
    d.text((left+20,525),key,fill='#24323b',font=f)
    d.text((left+20,550),'Opaque cuboids; no atlas/alpha.',fill='#6d6760',font=f)
d.text((20,590),'Signed floor gaps and conditional interruption landmarks: see JSON. Not a ground-contact acceptance.',fill='#973d33',font=f)
im.save(B/'frostmaw-source-poses.png')
