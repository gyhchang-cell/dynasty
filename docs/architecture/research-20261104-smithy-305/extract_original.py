import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read

def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
h=ld(P/'header-precheck.json');s=h['source'];assert bind(s['archive']['path'])==s['archive']
with ZipFile(s['archive']['path'])as z:
 raw=z.read(s['member']);d=read(raw);context_candidates=[n for n in z.namelist()if n.endswith('.json')and('bamboo'in n)and any(t in n for t in ['worldgen/structure/','worldgen/template_pool/','tags/worldgen/biome/','loot_tables/chests/villages/'])]
assert hashlib.sha256(raw).hexdigest()==s['raw_sha256'];put('source-original.json',d);put('source-binding.json',dict(**s,original_json=bind(P/'source-original.json')))
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};c=Counter(pal[b['state']]['Name']for b in bs.values());put('source-counts.json',dict(size=d['size'],DataVersion=d['DataVersion'],stored=len(bs),nonair=len(bs)-c['minecraft:air'],air=c['minecraft:air'],omitted=math.prod(d['size'])-len(bs),palette=len(pal),BE=sum('nbt'in b for b in bs.values()),entities=len(d.get('entities',[])),materials=dict(c)))
plans=[dict(y=y,rows_z=[' '.join(str(bs[x,y,z]['state'])if(x,y,z)in bs else'_'for x in range(d['size'][0]))for z in range(d['size'][2])])for y in range(d['size'][1])];put('all-layers-state-index.json',dict(legend='palette state indices; _ omitted unknown; x by column,z by row',layers=plans))
put('context-discovery.json',dict(members=context_candidates,boundary='只列归档内成员名，未读JSON正文。'))
print('COUNTS',json.dumps(ld(P/'source-counts.json'),ensure_ascii=False));print('CONTEXT_NAMES',json.dumps(context_candidates,ensure_ascii=False))
