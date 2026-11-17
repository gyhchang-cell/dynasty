"""Offline complete fixed-source spatial reading; grants no reference credit."""
import hashlib
import itertools
import json
from pathlib import Path
import sys
import zipfile
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso,color

def sha(b): return hashlib.sha256(b).hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

assert not (OUT/'RECEIPT.json').exists()
member='data/kaisyn/structures/village/sparse_jungle_polynesian/houses/sparse_jungle_fisher_and_fletcher_1.nbt'
metadata=ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json'
source=next(r for r in json.loads(metadata.read_text())['entries'] if r['member']==member)
comparisons=[]
for batch in [324,325]:
    p=ROOT/f'docs/architecture/research-20261104-smithy-{batch}/manual-review.json'
    b=p.read_bytes();d=json.loads(b)
    comparisons.append({'path':str(p),'sha256':sha(b),'seven_dimensions':d['seven_dimensions'],
                        'limits':d.get('limits'), 'reused_actual_prior_reading':True})
save('pre-original-family-comparison.json',{
    'target':'NPC15黄老汉岸侧值守/储物/临水作业辅助空间；不以渔户自动代替渡口',
    'full_seven_dimension_records':comparisons,
    'other_actual_prior_read_records':['061F03 elevated cold room and veranda','094F01 beach elevated work/bed room','097F01 L-shaped ranch, roof storage, watercourt'],
    'bounded_observations':['137F02 west/south two-door workroom with pool and farmland; incomplete original study','119F02 west water-work corridor and east little room; incomplete original study'],
    'exclusions_before_original':['303 Japanese fisher had full source state reading but square-house family exclusion before images; do not reopen that passed screen merely to find sources.', 'Temple W003/W016/W018 and094 beach main house already complete; 300 cloud-lake dock limited relevance exclusion retained.'],
    'current_choice':'Sparse jungle Polynesian fisher/fletcher exact member only found in prior machine candidate/functional screens, not a manual whole spatial review. No semantic novelty is assumed; now read complete body.',
    'formal_credit_added':0})
archive=Path(source['source_archive'])
assert sha(archive.read_bytes())=='9c8115af7109579da990249fdd67b38323a45be70f8a3a962b61da69c7021984'
with zipfile.ZipFile(archive) as z:
    raw=z.read(member);assert sha(raw)==source['nbt_sha256'];n=read(raw)
    loc='kaisyn:'+member.split('/structures/',1)[1][:-4]
    contexts=[]
    for name in z.namelist():
        if '/worldgen/template_pool/' in name and name.endswith('.json'):
            b=z.read(name)
            if loc.encode() in b:
                o=json.loads(b);contexts.append({'path':name,'sha256':sha(b),'bytes':len(b),
                    'header':{k:v for k,v in o.items() if k!='elements'},
                    'selected_elements':[e for e in o.get('elements',[]) if loc in json.dumps(e)],
                    'full_parent_read':False})
    roots=[]
    for name in z.namelist():
        if '/worldgen/structure/' in name and 'village_' in name and 'sparse_jungle' in name:
            b=z.read(name);roots.append({'path':name,'sha256':sha(b),'object':json.loads(b)})
save('selected-context.json',{'selected_parent_records':contexts,'direct_roots':roots})
palette=n['palette'];stored={tuple(b['pos']):b for b in n['blocks']}
rows=[]
sx,sy,sz=n['size']
for y in range(sy):
    for z in range(sz):
        vals=[stored[(x,y,z)]['state'] if (x,y,z) in stored else None for x in range(sx)]
        rows.append({'y':y,'z':z,'runs_x':[[k,len(list(g))] for k,g in itertools.groupby(vals)]})
be=[b for b in n['blocks'] if 'nbt' in b]
save('original-fullspace.json',{'size':n['size'],'DataVersion':n['DataVersion'],'palette':palette,
    'block_entities':be,'entities':n.get('entities',[]),'rows':rows,'stored':len(stored),
    'missing':sx*sy*sz-len(stored)})
save('source-binding.json',{'archive':str(archive),'archive_sha256':sha(archive.read_bytes()),
    'member':member,'nbt_sha256':sha(raw),'metadata_sha256':sha(metadata.read_bytes()),
    'historical_publisher_url':'https://www.curseforge.com/minecraft/mc-mods/towns-and-towers',
    'new_network_access':False})
cells={p:palette[b['state']]['Name'] for p,b in stored.items() if palette[b['state']]['Name'] not in AIR}
whole=Image.new('RGB',(1520,680),'#edf0f2')
for r in range(2):whole.paste(iso(cells,n['size'],r,'Polynesian work hut whole original; cubes not collision'),(760*r,0))
whole.save(OUT/'whole.png')
cuts=Image.new('RGB',(1520,1360),'#edf0f2')
for i,y in enumerate([2,5]):
    for r in range(2):cuts.paste(iso(cells,n['size'],r,f'Original cut y<={y}; one source',y),(760*r,680*i))
cuts.save(OUT/'cutaways.png')
step=17;pw=sx*step+60;ph=sz*step+55
im=Image.new('RGB',(pw*3,ph*((sy+2)//3)),'#edf0f2');draw=ImageDraw.Draw(im)
for y in range(sy):
    left=(y%3)*pw+35;top=(y//3)*ph+30
    draw.text((left,top-22),f'y={y}; +X right +Z down',fill='black')
    for x in range(sx):
        for z in range(sz):
            name=palette[stored[x,y,z]['state']]['Name'] if (x,y,z) in stored else None
            c='#ff00ff' if name is None else '#e3e6e9' if name in AIR else color(name)
            draw.rectangle((left+x*step,top+z*step,left+(x+1)*step,top+(z+1)*step),fill=c,outline='#bfc6ca')
    for x in range(0,sx,2):draw.text((left+x*step,top-12),str(x),fill='black')
    for z in range(0,sz,2):draw.text((left-20,top+z*step),str(z),fill='black')
im.save(OUT/'all-layers.png')
sec=Image.new('RGB',(1200,650),'#edf0f2');draw=ImageDraw.Draw(sec)
for i,(axis,fixed) in enumerate([('x',5),('z',6)]):
    width=sz if axis=='x' else sx;left=40+600*i;top=70;unit=38
    draw.text((left,20),f'{axis}={fixed}; y up; source categories, not collision',fill='black')
    for y in range(sy):
        draw.text((left-22,top+(sy-1-y)*unit),str(y),fill='black')
        for h in range(width):
            pos=(fixed,y,h) if axis=='x' else (h,y,fixed)
            name=palette[stored[pos]['state']]['Name'] if pos in stored else None
            c='#ff00ff' if name is None else '#e3e6e9' if name in AIR else color(name)
            draw.rectangle((left+h*unit,top+(sy-1-y)*unit,left+(h+1)*unit,top+(sy-y)*unit),fill=c,outline='#bfc6ca')
    for h in range(width):draw.text((left+h*unit,top+sy*unit+8),str(h),fill='black')
sec.save(OUT/'sections.png')
print('SOURCE',source['member'],n['size'],n['DataVersion'],'stored',len(stored),'missing',sx*sy*sz-len(stored))
print('PALETTE')
for i,st in enumerate(palette):print(i,json.dumps(st,separators=(',',':')))
print('BE',json.dumps(be,separators=(',',':')))
print('ENTITIES',json.dumps(n.get('entities',[]),separators=(',',':')))
print('ALL_ROWS y,z then index/run across x')
for r in rows:print(r['y'],r['z'],r['runs_x'])
print('CONTEXT',json.dumps({'parents':contexts,'roots':roots},separators=(',',':')))
