"""One original complete settlement; offline read-only evidence, no production."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.OUT=OUT
    return mod
def sha(data):return hashlib.sha256(data).hexdigest()
def dump(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    m=load('inspect017',BASE/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('trek','*远足*jar','https://modrinth.com/datapack/trek',['overworld/rare/villager_island'])]
    m.main()
    src=json.loads((OUT/'sources.json').read_text());c=src['candidates'][0]
    reader=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
    with ZipFile(c['source_archive']) as z:
        n=reader.read(z.read(c['member']));pal=n['palette']
        ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']}
        solid={p:s for p,s in ss.items() if s['Name'] not in reader.AIR}
        members=['META-INF/mods.toml','pack.mcmeta',
          'data/trek/worldgen/structure/overworld/rare/villager_island.json',
          'data/trek/worldgen/template_pool/overworld/rare/villager_island.json',
          'data/trek/worldgen/structure_set/overworld/rare.json',
          'data/trek/tags/worldgen/biome/ocean/combination/cold_default.json']
        resources=[]
        for member in members:
            raw=z.read(member)
            resources.append(dict(member=member,sha256=sha(raw),**({'text':raw.decode()} if member.endswith('.toml') else {'data':json.loads(raw)})))
        block_entities=[b for b in n['blocks'] if b.get('nbt')]
        loot=[]
        for b in block_entities:
            table=b['nbt'].get('LootTable')
            if not table:continue
            ns,name=table.split(':',1);member=f'data/{ns}/loot_tables/{name}.json'
            if any(e['member']==member for e in loot):continue
            r=dict(id=table,member=member,present_in_source_archive=member in z.namelist())
            if r['present_in_source_archive']:
                raw=z.read(member);r.update(sha256=sha(raw),data=json.loads(raw))
            loot.append(r)
    dump('author-context.json',dict(resources=resources,block_entities=block_entities,
        entities=n.get('entities',[]),loot_tables=loot,stored_positions=len(ss),
        explicit_air=sum(s['Name'] in reader.AIR for s in ss.values()),
        omitted_positions=n['size'][0]*n['size'][1]*n['size'][2]-len(ss),
        nonair_bounds={a:[min(p[i] for p in solid),max(p[i] for p in solid)] for i,a in enumerate('xyz')},
        bed_states=[dict(position=p,state=s) for p,s in ss.items() if s['Name'].endswith('_bed')],
        lower_doors=[dict(position=p,state=s) for p,s in ss.items() if s['Name'].endswith('_door') and s.get('Properties',{}).get('half')=='lower'],
        lower_door_layers=dict(Counter(p[1] for p,s in ss.items() if s['Name'].endswith('_door') and s.get('Properties',{}).get('half')=='lower')),
        stairs=[dict(position=p,state=s) for p,s in ss.items() if s['Name'].endswith('_stairs')],
        ladders=[dict(position=p,state=s) for p,s in ss.items() if s['Name']=='minecraft:ladder'],
        route_or_native_generation_verified=False,java_run=False,game_run=False,network_requests=0))
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text())
    d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries'])
    d['formal_count_annotation_corrected_from_legacy_helper']=True
    dump('dedup-evidence.json',d)
if __name__=='__main__':main()
