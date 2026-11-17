"""Fixed local authored whole-site candidates, no creation or game execution."""
import importlib.util
import json
import hashlib
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    m=load('renderer017',BASE/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('trek','*远足*jar','https://modrinth.com/datapack/trek',['overworld/medium/stonehedge','overworld/common/smoldering_altar'])]
    m.main()
    src=json.loads((OUT/'sources.json').read_text());context=[]
    reader=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
    with ZipFile(src['source_archives'][0]['path']) as z:
        manifest=z.read('META-INF/mods.toml')
        for c in src['candidates']:
            tail=c['member'].split('/structures/',1)[1][:-4];ident='trek:'+tail
            c['pool_references']=[r for r in c['pool_references'] if any(e['element'].get('location')==ident for e in r['data'].get('elements',[]))]
            n=reader.read(z.read(c['member']));p=n['palette'];ss={tuple(b['pos']):p[b['state']] for b in n['blocks']}
            names=['data/trek/worldgen/structure/'+tail+'.json','data/trek/worldgen/template_pool/'+tail+'.json']
            pool=json.loads(z.read(names[1]));processor=pool['elements'][0]['element']['processors']
            if processor!='minecraft:empty':names.append('data/trek/worldgen/processor_list/'+processor.split(':',1)[1]+'.json')
            root=json.loads(z.read(names[0]));biome=root['biomes']
            if biome.startswith('#trek:'):names.append('data/trek/tags/worldgen/biome/'+biome.split(':',1)[1]+'.json')
            resources=[]
            for member in names:
                raw=z.read(member);resources.append(dict(member=member,sha256=sha(raw),data=json.loads(raw)))
            context.append(dict(id=c['id'],resources=resources,manifest_text=manifest.decode(),manifest_sha256=sha(manifest),
                stored_positions=len(ss),explicit_air=sum(s['Name']=='minecraft:air' for s in ss.values()),
                omitted_positions=n['size'][0]*n['size'][1]*n['size'][2]-len(ss),
                block_entities=[b for b in n['blocks'] if b.get('nbt')],entities=n['entities'],
                candle_and_fire_states=[dict(position=q,state=s) for q,s in ss.items() if s['Name'] in ('minecraft:candle','minecraft:campfire','minecraft:fire','minecraft:soul_fire')],
                bone_states=[dict(position=q,state=s) for q,s in ss.items() if s['Name']=='minecraft:bone_block'],
                original_states_preserved=True,native_projection_and_processors_executed=False))
    (OUT/'sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2)+'\n')
    (OUT/'author-context.json').write_text(json.dumps(dict(entries=context,network_requests=0,java_run=False,game_run=False),ensure_ascii=False,indent=2)+'\n')
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text())
    d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries'])
    d['formal_count_annotation_corrected_from_legacy_helper']=True
    (OUT/'dedup-evidence.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
