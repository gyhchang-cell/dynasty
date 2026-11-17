"""Reference-only byte-preserving extraction and integer-scaled inspection sheets."""
import hashlib, json, math, zipfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def extract(key,folder,selected):
    b=ROOT/'docs/art'/folder; b.mkdir(exist_ok=True)
    archive=HERE/(key+'-fixed.zip');z=zipfile.ZipFile(archive);prefix=z.namelist()[0]
    for n in z.namelist():
        rel=n[len(prefix):]
        if not n.endswith('/') and selected(rel):
            p=b/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
    entries={}
    for p in (b/'source').rglob('*'):
        if p.is_file():
            rel=p.relative_to(b/'source').as_posix();assert p.read_bytes()==z.read(prefix+rel)
            entries[rel]=sha(p)
    old=b/'provenance.json'
    prov=json.loads(old.read_text()) if old.exists() else {}
    prov.update(archive=str(archive),archive_sha256=sha(archive),entries=entries,external_code_executed=False)
    save(old,prov)
    return b
def sheets(b,paths,stem='native-pixels',cols=3,cell=(380,320)):
    pages=[]
    for page in range(math.ceil(len(paths)/9)):
        chunk=paths[page*9:page*9+9];out=Image.new('RGB',(cols*cell[0],math.ceil(len(chunk)/cols)*cell[1]),(81,87,91));d=ImageDraw.Draw(out)
        for i,p in enumerate(chunk):
            im=Image.open(p).convert('RGBA');x=i%cols*cell[0];y=i//cols*cell[1];d.text((x+8,y+8),p.name+' '+str(im.size),(255,255,255))
            k=max(1,min((cell[0]-20)//im.width,(cell[1]-40)//im.height));im=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);out.paste(im,(x+8,y+32),im)
        p=b/f'{stem}-{page+1:02}.png';out.save(p);pages.append(dict(path=p.name,sha256=sha(p)))
    save(b/(stem+'-index.json'),dict(pages=pages,source_pixels_unchanged=True,integer_nearest_neighbor=True,not_game_capture=True,source_png=[dict(path=str(p.relative_to(b)),sha256=sha(p),size=list(Image.open(p).size)) for p in paths]))
    return pages

if __name__=='__main__':
    b=extract('forbidden','armor-mortem-whole-20261112',lambda n: 'mortem' in n.lower() and n.endswith(('.png','.json')))
    sheets(b,sorted((b/'source').rglob('*.png')))
