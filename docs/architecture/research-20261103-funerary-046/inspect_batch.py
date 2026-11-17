"""Read only three functional-signal candidates; screening is not credit."""
import importlib.util
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    m=load('renderer017',BASE/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('kaisyn','*城镇与塔楼*jar','https://modrinth.com/mod/towns-and-towers',[
        'village/exclusives/piglin/houses/piglin_skul_tent_1','village/exclusives/piglin/houses/piglin_skull_tent_1']),
        ('trek','*远足*jar','https://modrinth.com/datapack/trek',['village/mushroom/houses/brewing_stand'])]
    context_only='--context-only' in sys.argv
    if not context_only:m.main()
    src=json.loads((OUT/'sources.json').read_text());contexts=[];states={}
    reader=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
    for c in src['candidates']:
        prefix,tail=c['member'].split('/structures/',1);ns=prefix.split('/')[-1];identifier=ns+':'+tail[:-4]
        c['pool_references']=[r for r in c['pool_references'] if any(e['element'].get('location')==identifier for e in r['data'].get('elements',[]))]
        with ZipFile(c['source_archive']) as z:
            n=reader.read(z.read(c['member']));pal=n['palette'];ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']};states[c['id']]=ss
            raw=z.read('META-INF/mods.toml');resources=[]
            for member in z.namelist():
                if not member.endswith('.json') or '/worldgen/' not in member:continue
                if (ns=='kaisyn' and ('/village/piglin' in member or '/village/exclusives/piglin' in member)) or (ns=='trek' and '/village/mushroom' in member):
                    raw_json=z.read(member);resources.append(dict(member=member,sha256=sha(raw_json),data=json.loads(raw_json)))
            outgoing=[]
            for socket in c['sockets']:
                pool=socket['data'].get('pool','minecraft:empty')
                if pool=='minecraft:empty':continue
                pns,ptail=pool.split(':',1);member='data/'+pns+'/worldgen/template_pool/'+ptail+'.json'
                present=member in z.namelist();outgoing.append(dict(pool=pool,exact_member=member,present=present))
                if present and not any(r['member']==member for r in resources):
                    raw_json=z.read(member);resources.append(dict(member=member,sha256=sha(raw_json),data=json.loads(raw_json)))
            contexts.append(dict(id=c['id'],manifest_text=raw.decode(),manifest_sha256=sha(raw),
                whole_village_context_resources=resources,block_entities=[b for b in n['blocks'] if b.get('nbt')],entities=n['entities'],
                exact_outgoing_pool_resolution=outgoing,
                stored_positions=len(ss),explicit_air=sum(s['Name']=='minecraft:air' for s in ss.values()),
                omitted_positions=n['size'][0]*n['size'][1]*n['size'][2]-len(ss),
                brewing_stand_states=[dict(position=q,state=s) for q,s in ss.items() if s['Name']=='minecraft:brewing_stand'],
                native_use_or_profession_not_inferred_from_workstation=True))
    positions=states['F01'].keys()|states['F02'].keys()
    changes=[dict(position=q,left=states['F01'].get(q),right=states['F02'].get(q)) for q in sorted(positions) if states['F01'].get(q)!=states['F02'].get(q)]
    (OUT/'sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2)+'\n')
    (OUT/'author-context.json').write_text(json.dumps(dict(entries=contexts,skul_skull_comparison=dict(changed_raw_states=len(changes),changes=changes,raw_block_states_identical=not changes),network_requests=0,java_run=False,game_run=False),ensure_ascii=False,indent=2)+'\n')
    if context_only:
        print('Updated exact piglin and outgoing-pool context only; no repeated render/dedup.')
        return
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text());d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries']);d['formal_count_annotation_corrected_from_legacy_helper']=True
    (OUT/'dedup-evidence.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
