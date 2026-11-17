"""One fixed original inn; original DUN05 use, no scope expansion or credit."""
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    m=load('inspect017',BASE/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('simply_houses','*SimplyHouses*jar','local META-INF/mods.toml: Aurelj, DiamondTown & Zephyrusj',
        ['taiga_inn/taiga_inn'])]
    m.main()
    src=json.loads((OUT/'sources.json').read_text());c=src['candidates'][0]
    reader=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
    with ZipFile(c['source_archive']) as z:
        n=reader.read(z.read(c['member']));pal=n['palette'];ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']}
        resources=[]
        members=['META-INF/mods.toml','pack.mcmeta','data/simply_houses/worldgen/structure/taiga_inn.json',
            'data/simply_houses/worldgen/template_pool/taiga_inn/taiga_inn_main.json',
            'data/simply_houses/tags/worldgen/biome/has_structure/taiga_inn_biomes.json']
        for member in members:
            raw=z.read(member);r=dict(member=member,sha256=sha(raw));r['data' if member.endswith(('.json','.mcmeta')) else 'text']=json.loads(raw) if member.endswith(('.json','.mcmeta')) else raw.decode();resources.append(r)
        block_entities=[b for b in n['blocks'] if b.get('nbt')]
        loot=[]
        for b in block_entities:
            table=b['nbt'].get('LootTable')
            if not table:continue
            ns,name=table.split(':',1);member=f'data/{ns}/loot_tables/{name}.json'
            if any(e['member']==member for e in loot):continue
            r=dict(id=table,member=member,present=member in z.namelist())
            if r['present']:
                raw=z.read(member);r.update(sha256=sha(raw),data=json.loads(raw))
            loot.append(r)
    dump('author-context.json',dict(resources=resources,block_entities=block_entities,entities=n['entities'],loot_tables=loot,
        stored_positions=len(ss),explicit_air=sum(s['Name']=='minecraft:air' for s in ss.values()),
        omitted_positions=n['size'][0]*n['size'][1]*n['size'][2]-len(ss),
        bed_states=[dict(position=p,state=s) for p,s in ss.items() if s['Name'].endswith('_bed')],
        doors=[dict(position=p,state=s) for p,s in ss.items() if s['Name'].endswith('_door')],
        stairs=[dict(position=p,state=s) for p,s in ss.items() if s['Name'].endswith('_stairs')],
        native_routes_or_loot_generation_verified=False,java_run=False,game_run=False,network_requests=0))
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text());d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries']);d['formal_count_annotation_corrected_from_legacy_helper']=True;dump('dedup-evidence.json',d)
if __name__=='__main__':main()
