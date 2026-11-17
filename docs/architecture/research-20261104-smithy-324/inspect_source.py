"""One fixed local whole-body reference, source-only, with no admission credit."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import zipfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR, iso, plans, color


def digest(b):
    return hashlib.sha256(b).hexdigest()


def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')


assert not (OUT/'RECEIPT.json').exists()
member = 'data/kaisyn/structures/village/exclusives/tudor/houses/tudor_fisher_1.nbt'
metadata = ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json'
meta = [r for r in json.loads(metadata.read_text())['entries'] if r['member']==member]
assert len(meta)==1
source = meta[0]
archive = Path(source['source_archive'])
assert digest(archive.read_bytes()) == '9c8115af7109579da990249fdd67b38323a45be70f8a3a962b61da69c7021984'

# All these complete written observations were read before this original NBT/image.
comparators = []
for batch, ident in [(61,'F03'), (97,'F01'), (119,'F02'), (127,'F01'), (127,'F02'), (137,'F02')]:
    f = ROOT/f'docs/architecture/research-20261104-smithy-{batch:03}/manual-review.json'
    raw = f.read_bytes()
    cases = json.loads(raw)['cases']
    case = next(c for c in cases if c['id']==ident)
    comparators.append({'path':str(f),'sha256':digest(raw),'case':ident,
                        'observations':case.get('observations',case.get('screening_observations')),
                        'complete_seven_dimension_record': 'observations' in case})
save('pre-original-comparison.json', {
    'target':'NPC15黄老汉·大江古渡口，岸边值守/储物和水作空间有限相关性，不是完整码头',
    'comparators_read_before_originals':comparators,
    'history_search':'Exact member found in198 machine candidates,229 bounded interface screen,046 functional prefilter and components metadata. No matching manual-review or full-building record in this bounded local text search. String absence is not semantic novelty.',
    'excluded_prior_complete_temples':['COD4-R001-W003 cherry_temple','COD4-R001-W016 Swedish library/temple','COD4-R001-W018 flower_forest_temple'],
    'decision':'Original whole-body study allowed; no novelty/credit admission. Compare enclosed room plus work-edge, not profession names.',
    'formal_credit_added':0})

with zipfile.ZipFile(archive) as z:
    raw=z.read(member)
    assert digest(raw)==source['nbt_sha256']
    n=read(raw)
    loc='kaisyn:'+member.split('/structures/',1)[1][:-4]
    contexts=[]
    for name in z.namelist():
        if '/worldgen/' in name and name.endswith('.json'):
            b=z.read(name)
            if loc.encode() in b:
                obj=json.loads(b)
                matching=[e for e in obj.get('elements',[]) if loc in json.dumps(e)]
                contexts.append({'path':name,'sha256':digest(b),'bytes':len(b),
                                 'selected_elements':matching,
                                 'pool_header':{k:v for k,v in obj.items() if k!='elements'},
                                 'full_parent_read':False})
    save('selected-parent-context.json',contexts)
    roots=[name for name in z.namelist() if '/worldgen/structure/' in name and 'tudor' in name and name.endswith('.json')]
    root_objects=[]
    for name in roots:
        b=z.read(name);obj=json.loads(b)
        root_objects.append({'path':name,'sha256':digest(b),'object':obj})
    save('direct-root-context.json',root_objects)

palette=n['palette'];stored={tuple(b['pos']):b for b in n['blocks']}
assert len(stored)==len(n['blocks'])
rows=[]
for y in range(n['size'][1]):
    for z in range(n['size'][2]):
        vals=[stored[(x,y,z)]['state'] if (x,y,z) in stored else None for x in range(n['size'][0])]
        rows.append({'y':y,'z':z,'runs_x':[[k,len(list(g))] for k,g in itertools.groupby(vals)]})
be=[b for b in n['blocks'] if 'nbt' in b]
save('original-fullspace.json',{'size':n['size'],'DataVersion':n['DataVersion'],
      'palette':palette,'block_entities':be,'entities':n.get('entities',[]),'rows':rows,
      'stored_count':len(stored),'missing_count':n['size'][0]*n['size'][1]*n['size'][2]-len(stored)})
save('source-binding.json',{'source_archive':str(archive),'archive_sha256':digest(archive.read_bytes()),
      'member':member,'nbt_sha256':digest(raw),'metadata_sha256':digest(metadata.read_bytes()),
      'reference_url':'https://www.curseforge.com/minecraft/mc-mods/towns-and-towers',
      'url_use':'Historical provenance only; no network access this batch'})

cells={p:palette[b['state']]['Name'] for p,b in stored.items() if palette[b['state']]['Name'] not in AIR}
whole=Image.new('RGB',(1520,1360),'#edf0f2')
for i in range(4):
    # Repeated rotations are views of one source, never separate designs.
    rotated=cells; size=n['size']
    for _ in range(i//2*2):
        rotated={(size[2]-1-z,y,x):v for (x,y,z),v in rotated.items()};size=[size[2],size[1],size[0]]
    whole.paste(iso(rotated,size,i%2,f'Tudor fisher original whole view {i}; cubes not collision'),((i%2)*760,(i//2)*680))
whole.save(OUT/'F01-whole.png')
cuts=Image.new('RGB',(1520,680),'#edf0f2')
for rot in range(2):cuts.paste(iso(cells,n['size'],rot,'Original cutaway y<=3; no native collision',3),(rot*760,0))
cuts.save(OUT/'F01-cutaway.png')
for y in [0,2,4,6]:plans(cells,n['size'],y,'F01').save(OUT/f'F01-y{y}.png')
print('SOURCE',member,n['size'],n['DataVersion'],'stored',len(stored),'missing',n['size'][0]*n['size'][1]*n['size'][2]-len(stored))
print('PALETTE')
for i,p in enumerate(palette):print(i,json.dumps(p,separators=(',',':')))
print('BLOCK_ENTITIES',json.dumps(be,separators=(',',':')))
print('ENTITIES',json.dumps(n.get('entities',[]),separators=(',',':')))
print('FULL_ROWS y,z then palette/run-length across x')
for r in rows:print(r['y'],r['z'],r['runs_x'])
print('SELECTED_CONTEXT',json.dumps(contexts,separators=(',',':')))
print('ROOTS',json.dumps(root_objects,separators=(',',':')))
