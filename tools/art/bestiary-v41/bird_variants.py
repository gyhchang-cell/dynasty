"""Named author-published bird texture studies; shared rigs are explicitly grouped.
No gender views or extra poses count as a new creature identity.
"""
from pathlib import Path
import json,re,urllib.request,hashlib,concurrent.futures
from PIL import Image,ImageDraw
from bird_references import D, get

OUT=D/'species';OUT.mkdir(exist_ok=True)
def collect():
    rows=[]
    for page in sorted(D.glob('*.md')):
        for line in page.read_text().splitlines():
            cells=line.split('|')
            if len(cells)<5 or not re.fullmatch(r'\s*\d+\s*',cells[1]):continue
            species=re.sub(r'\s*\([^)]*\)','',cells[2]).strip()
            urls=re.findall(r'<img[^>]*src=["\']([^"\']+)["\']',line)
            url=next((u for u in urls if 'imgur.com' in u or 'postimg.cc' in u),None)
            if not url:continue
            if species.lower() in {r['identity'].lower() for r in rows}:continue
            rows.append(dict(identity=species,model_family=page.stem,source='https://github.com/frikinzi/frikinzis_fauna/wiki/'+page.stem,url=url))
    def load(r):
        try:
            file='image-'+hashlib.sha256(r['url'].encode()).hexdigest()[:18]+'.img';p=OUT/file
            if not p.exists():p.write_bytes(get(r['url']))
            im=Image.open(p)
            if min(im.size)<40:return None
            r.update(file=file,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),viewed=False);return r
        except Exception:return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:rows=[r for r in ex.map(load,rows) if r]
    for i,r in enumerate(rows):r['index']=i+1
    (OUT/'candidates.json').write_text(json.dumps(rows,indent=2)+'\n')
    for start in range(0,len(rows),16):
        sheet=Image.new('RGB',(1600,1320),'#e9e9df');dr=ImageDraw.Draw(sheet)
        for j,r in enumerate(rows[start:start+16]):
            im=Image.open(OUT/r['file']).convert('RGBA');im.thumbnail((390,278));x=j%4*400;y=j//4*330;sheet.paste(im,(x+(390-im.width)//2,y),im)
            dr.text((x+8,y+280),str(r['index'])+' '+r['identity'],fill='black');dr.text((x+8,y+300),'shared rig: '+r['model_family'],fill='black')
        sheet.save(OUT/f'sheet-{start//16+1:02}.jpg',quality=92)
    print('Named species',len(rows),'rig families',len({r['model_family'] for r in rows}),flush=True)

if __name__=='__main__':collect()
