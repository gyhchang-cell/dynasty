"""Original mob-only dependency boundary and settlement levels, no assembly."""
import hashlib,json,sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,plans,iso
def dump(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    c=json.loads((OUT/'sources.json').read_text())['candidates'][0]
    with ZipFile(c['source_archive']) as z:
        n=read(z.read(c['member']));pal=n['palette']
        cells={tuple(b['pos']):pal[b['state']]['Name'] for b in n['blocks'] if pal[b['state']]['Name'] not in AIR}
        member='data/trek/worldgen/template_pool/mobs/villagers/plains/unemployed.json'
        raw=z.read(member);pool=json.loads(raw);parts=[]
        for e in pool['elements']:
            loc=e['element']['location'];ns,name=loc.split(':',1);mem=f'data/{ns}/structures/{name}.nbt'
            b=z.read(mem);d=read(b);p=d['palette']
            parts.append(dict(archive_member=mem,sha256=hashlib.sha256(b).hexdigest(),weight=e['weight'],
              size=d['size'],blocks=d['blocks'],palette=p,entities=d.get('entities',[]),
              materials=dict(Counter(p[x['state']]['Name'] for x in d['blocks'])),
              interpretation='Mob-support template, not another building or credit unit.'))
    dump('mob-support-boundary.json',dict(pool_member=member,pool_sha256=hashlib.sha256(raw).hexdigest(),pool_data=pool,
        support_templates=parts,original_parent_jigsaws=c['sockets'],
        transformed_or_assembled=False,native_spawn_verified=False,building_credit=0))
    for y in (19,24,34):plans(cells,n['size'],y,'F01 original settlement').save(OUT/f'F01-y{y}.png')
    image=Image.new('RGB',(1520,1400),'#edf0f2')
    for y,off in [(24,0),(34,680)]:
        for rot in (0,1):image.paste(iso(cells,n['size'],rot,f'F01 original y <= {y}',y),(rot*760,off))
    ImageDraw.Draw(image).text((16,1372),'RESEARCH ONLY: original blocks / full-cell classification / not native furniture, texture, terrain or collision / no assembly',fill='#17252c')
    image.save(OUT/'F01-life-level-cutaway.png')
if __name__=='__main__':main()
