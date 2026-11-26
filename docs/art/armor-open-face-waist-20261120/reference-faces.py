from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ART=ROOT/'docs/art'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CONTRACT=ART/'armor-worn-uv-20261102/face-and-seam-inventory.json'
template=read(CONTRACT)['entries'][0]
parts={p['part']:{f['direction']:f['crop'] for f in p['faces']} for p in template['parts']}
controls=ART/'armor-worn-uv-20261102'
source_specs={
 'vanilla iron': (controls/'vanilla-controls/iron_layer_1.png',controls/'vanilla-controls/iron_layer_2.png',controls/'vanilla-control-provenance.json'),
 'vanilla leather': (controls/'vanilla-controls/leather_layer_1.png',controls/'vanilla-controls/leather_layer_2.png',controls/'vanilla-control-provenance.json'),
}
for name,folder,pattern,binding in [
 ('Twilight Forest Ironwood','armor-ironwood-whole-20261114','ironwood_{}.png','bindings-review.json'),
 ('Caverns & Chasms Silver','armor-silver-whole-20261114','silver_layer_{}.png','four-slot-source-binding.json'),
 ('Ender IO Dark Steel','armor-dark-steel-whole-20261114','dark_steel_layer_{}.png','four-slot-source-binding.json'),
]:
    base=ART/folder
    source_specs[name]=(*[next((base/'source').rglob(pattern.format(n))) for n in (1,2)],base/binding)

sheet=Image.new('RGB',(1180,842),'#52585c')
draw=ImageDraw.Draw(sheet)
columns=[(8,'source'),(206,'atlas L1'),(405,'atlas L2'),(610,'head front'),(711,'hat front'),(815,'L2 front'),(917,'L2 back'),(1020,'L2 side'),(1090,'L2 side')]
for x,label in columns:draw.text((x,9),label,fill='white')
def paste(img,x,y,scale):
    bigger=img.resize((img.width*scale,img.height*scale),Image.Resampling.NEAREST)
    sheet.paste(bigger,(x,y),bigger)

def binding(p):
    return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}

report=[]
for index,(label,(first,second,decl)) in enumerate(source_specs.items()):
    y=40+index*155
    draw.text((8,y+20),label,fill='white')
    l1,l2=[Image.open(p).convert('RGBA') for p in (first,second)]
    assert l1.size==l2.size==(64,32)
    paste(l1,206,y,3)
    paste(l2,405,y,3)
    row={'label':label,'atlas':[binding(first),binding(second)],'registration_binding':binding(decl),'faces':{}}
    for x,layer,part,direction in [(610,1,'head','NORTH'),(711,1,'hat','NORTH'),(815,2,'body','NORTH'),(917,2,'body','SOUTH'),
                            (1020,2,'body','WEST'),(1090,2,'body','EAST')]:
        crop=(l1 if layer==1 else l2).crop(parts[part][direction])
        paste(crop,x,y,9)
        alpha=crop.getchannel('A')
        pixels=[''.join('#' if alpha.getpixel((i,j)) else '.' for i in range(crop.width)) for j in range(crop.height)]
        row['faces'][f'L{layer}/{part}/{direction}']={'crop':parts[part][direction],'nontransparent_rows':[p.count('#') for p in pixels],
                                                   'alpha_mask':pixels}
    report.append(row)
sheet.save(OUT/'wear-reference-faces.png')
(OUT/'reference-face-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for item in report:
    print(item['label'], {k:v['nontransparent_rows'] for k,v in item['faces'].items()})
