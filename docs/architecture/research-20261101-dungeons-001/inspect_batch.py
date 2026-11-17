#!/usr/bin/env python3
"""Offline original-template inspection; writes research evidence only."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from PIL import Image,ImageDraw

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
sys.path.insert(0,str(OUT.parent/'research-20261101-task-map'))
from nbt_read import read
from whole_building_candidates import AIR,iso,plans
from inspect_expanded_sources import vertical

MODS=Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods')
SELECTION=[
 ('ati_structures','*ATi*jar','https://www.curseforge.com/minecraft/mc-mods/ati-structures',[
  'catalonian_castle','ruined_castle','dark_tower','underwater_dungeon','illager_tower','stray_ruins']),
 ('trek','*远足*jar','https://modrinth.com/datapack/trek',[
  'overworld/rare/castle','overworld/rare/villager_castle','overworld/rare/tower_island',
  'overworld/rare/abandoned_castle_pillager','overworld/medium/tower_of_ice','overworld/medium/witch_tower']),
]


def main():
    previous=set()
    for p in (ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'):
        previous.update(r['member'] for r in json.loads(p.read_text()).get('candidates',[]))
    candidates=[]; archives=[]
    for namespace,pattern,url,names in SELECTION:
        matches=list(MODS.glob(pattern));assert len(matches)==1
        jar=matches[0];sha=hashlib.sha256(jar.read_bytes()).hexdigest()
        archives.append(dict(path=str(jar),sha256=sha,publisher_url=url,url_access='provenance only, not requested online'))
        with ZipFile(jar) as z:
            pools={n:json.loads(z.read(n)) for n in z.namelist() if '/worldgen/template_pool/' in n and n.endswith('.json')}
            for name in names:
                member=f'data/{namespace}/structures/{name}.nbt'
                assert member not in previous,'Previously studied member; choose or explicitly rescope rather than call new'
                raw=z.read(member);d=read(raw);pal=d.get('palette') or d['palettes'][0];blocks=d['blocks']
                cells={tuple(b['pos']):pal[b['state']]['Name'] for b in blocks if pal[b['state']]['Name'] not in AIR}
                assert len({tuple(b['pos']) for b in blocks})==len(blocks)
                assert all(0<=p<s for b in blocks for p,s in zip(b['pos'],d['size']))
                doors=[dict(position=b['pos'],state=pal[b['state']]) for b in blocks if pal[b['state']]['Name'].endswith('_door') and pal[b['state']].get('Properties',{}).get('half')=='lower']
                level=min((b['position'][1] for b in doors),default=min(p[1] for p in cells)+1)
                sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in blocks if pal[b['state']]['Name']=='minecraft:jigsaw']
                ident=f'F{len(candidates)+1:02d}';cutoff=max(level+1,round(d['size'][1]*.4))
                image=Image.new('RGB',(1520,1400),'#edf0f2')
                for rotation,x in ((0,0),(1,760)):
                    image.paste(iso(cells,d['size'],rotation,ident+' '+name.rsplit('/',1)[-1]),(x,0))
                    image.paste(iso(cells,d['size'],rotation,f'{ident} cutaway y <= {cutoff}',cutoff),(x,680))
                ImageDraw.Draw(image).text((18,1372),'RESEARCH ONLY / full-cell approximation / classification colors / not native terrain, texture or collision / no automatic credit',fill='#17252c')
                names_out=[ident+'-whole.png',ident+'-plan.png',ident+'-vertical.png']
                image.save(OUT/names_out[0]);plans(cells,d['size'],level,ident).save(OUT/names_out[1])
                vertical(cells,d['size'],ident).save(OUT/names_out[2])
                loc=namespace+':'+member.split('/structures/',1)[1][:-4]
                pool_refs=[dict(member=n,data=data) for n,data in pools.items() if loc in json.dumps(data)]
                states=[dict(position=b['pos'],state=pal[b['state']]) for b in blocks
                        if any(k in pal[b['state']]['Name'] for k in ('stairs','ladder','door','gate','jigsaw'))]
                candidates.append(dict(id=ident,member=member,source_archive=str(jar),source_archive_sha256=sha,
                    publisher_url=url,nbt_sha256=hashlib.sha256(raw).hexdigest(),size=d['size'],nonair=len(cells),
                    materials=dict(Counter(cells.values())),layers=dict(sorted(Counter(p[1] for p in cells).items())),
                    doors=doors,sockets=sockets,selected_plan_level=level,
                    selected_plan_level_limit='Lowest stored lower door, otherwise generic minimum nonair + 1; NOT proof of real world entrance',
                    opening_and_vertical_states=states,pool_references=pool_refs,images=names_out,
                    entities=[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])],
                    status='UNREVIEWED; NO AUTOMATIC CREDIT'))
                print(ident,name,d['size'],'plan',level,'sockets',len(sockets))
    (OUT/'sources.json').write_text(json.dumps(dict(source_archives=archives,candidates=candidates,automatic_credit=0),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
