"""Read original stair landings and foundation sockets; source evidence only."""
import json, hashlib, sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image, ImageDraw
P = Path(__file__).resolve().parent
R = P.parents[2]
assert not (P / 'RECEIPT.json').exists()
sys.path.insert(0, str(R / 'tools/architecture'))
from nbt_read import read
from whole_building_candidates import color
from reference_components import role, geometry_hash
def ld(p): return json.loads(Path(p).read_text())
def put(n, v): (P/n).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')
def bind(p):
    p=Path(p).resolve(); b=p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))
d=ld(P/'F02-original.json'); pal=d['palette']; bs={tuple(b['pos']): b for b in d['blocks']}
def cell(p):
    b=bs.get(tuple(p))
    return dict(pos=p, state_index=b['state'], state=pal[b['state']]) if b else dict(pos=p, omitted=True)
# Every straight flight endpoint plus adjacent source landing and two source cells
# above are retained. No collision model or traversability inference is applied.
chain_rows=[]
directions=dict(east=(1,0), west=(-1,0), north=(0,-1), south=(0,1))
for c in ld(P/'source-stair-chains-not-navigation.json'):
    dx,dz=directions[c['facing']]; start=c['positions'][0]; end=c['positions'][-1]
    probes=[]
    for label, q in [('before', [start[0]-dx,start[1]-1,start[2]-dz]), ('first',start), ('last',end), ('after',[end[0]+dx,end[1],end[2]+dz])]:
        probes.append(dict(label=label, source_cells=[cell([q[0],q[1]+h,q[2]]) for h in range(4)]))
    chain_rows.append(dict(flight=c, probes=probes))
put('stair-endpoint-probes.json', dict(meaning='Original state cells, not movement/clearance acceptance', flights=chain_rows))
# Bounded landing matrices across the southwest stair tower.
legend={}; matrices=[]
for y in [6,7,11,12,16,17,21,22,23,24,28,29]:
    matrix=[]
    for z in range(22,33):
        row=[]
        for x in range(4,15):
            b=bs.get((x,y,z)); key=str(b['state']) if b else '?'
            if b: legend[key]=pal[b['state']]
            row.append(key)
        matrix.append(row)
    matrices.append(dict(y=y, x_range=[4,14], z_range=[22,32], rows_z_increasing=matrix))
put('southwest-landing-matrices.json', dict(legend=legend, matrices=matrices, boundary='Full original property lookup; no collision verdict'))
sections=[('x',6),('x',12),('z',24),('z',34)]
for j in range(2):
    im=Image.new('RGB',(1500,900),'#edf0f2'); dr=ImageDraw.Draw(im); step=15
    for k,(axis,fixed) in enumerate(sections[j*2:j*2+2]):
        ox=40+k*750; oy=75
        dr.text((ox,20),f'F02 {axis}={fixed}; WHITE saved air / BLACK omitted; y up',fill='black')
        for u in range(48):
            for y in range(48):
                pos=(fixed,y,u) if axis=='x' else (u,y,fixed)
                b=bs.get(pos); n=pal[b['state']]['Name'] if b else None
                c='#151a24' if n is None else '#ffffff' if n in ['minecraft:air','minecraft:cave_air','minecraft:void_air'] else color(n)
                dr.rectangle((ox+u*step,oy+(47-y)*step,ox+(u+1)*step,oy+(48-y)*step),fill=c,outline='#bdc3c8')
        for t in range(0,48,5):
            dr.text((ox+t*step,oy+48*step+5),str(t),fill='black')
            dr.text((ox-22,oy+(47-t)*step),str(t),fill='black')
    im.save(P/f'F02-sections-{j+1}.png')
a=ld(P/'F02-source.json'); foundations=[]
with ZipFile(a['source_archive']) as z:
    for tail in ['terrain1','terrain2']:
        n='data/ati_structures/structures/terrain_large/'+tail+'.nbt'; raw=z.read(n); t=read(raw)
        sockets=[dict(pos=b['pos'],state=t['palette'][b['state']],nbt=b.get('nbt')) for b in t['blocks'] if t['palette'][b['state']]['Name']=='minecraft:jigsaw']
        foundations.append(dict(member=n,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),size=t['size'],stored=len(t['blocks']),sockets=sockets,read_boundary='Header and every socket only; foundation terrain not full spatially reviewed; 0 buildings'))
put('foundation-sockets.json', dict(archive=bind(a['source_archive']),host=[cell([23,0,23])],foundations=foundations))
cells={p: role(pal[b['state']]['Name']) for p,b in bs.items() if role(pal[b['state']]['Name']) not in (None,0)}
fp=dict(nbt_sha256=a['nbt_sha256'],role_sha256=geometry_hash(cells,d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']))
history=ld(R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json')
matches=[e for e in history['entries'] if any(e['fingerprints'].get(k)==v for k,v in fp.items())]
put('historical-fingerprint-check.json',dict(source=bind(R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json'),current=fp,matches=matches,method='NONAIR only, exactly the historical check_dedup.load convention; explicit air/omission remain separately preserved in F02-original.json',correction='Initial current calculation included explicit air and was not comparable. Corrected before sealing; its no-match result is invalid and supplies no novelty claim.',meaning='Rotation/material-invariant prefilter only, not semantic credit or actual viewing'))
prior=[]
for sub, ident in [('research-20261101-dungeons-002','F09'),('research-20261101-dungeons-003','F06')]:
    f=R/'docs/architecture'/sub/'manual-review.json'; entry=next(e for e in ld(f)['entries'] if e['id']==ident)
    prior.append(dict(binding=bind(f),entry=entry,current_reading='Full own seven observations and limits read; historical PNG not reopened and never counted again'))
put('prior-whole-comparison.json',dict(prior=prior,current_comparison='Fortified temple has asymmetric joined tall halls and a separate narrow turning-stair tower within ONE complex; dojo is lower hall plus centred upper pavilion; steam_house is wide water court beside multi-storey halls. Different spatial organizations, but the current flatland source still does not prove the target cliff/cave/upper monastery route.',credit_added=0))
print(json.dumps(dict(foundations=foundations,fingerprint=fp,matches=[e['source']for e in matches],flights=len(chain_rows),sections_generated=2),ensure_ascii=False))
