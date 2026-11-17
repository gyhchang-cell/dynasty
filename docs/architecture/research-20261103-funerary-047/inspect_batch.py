"""Read the three fixed-source haunted ruins; no production or automatic credit."""
import hashlib
import importlib.util
import itertools
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
    m.SELECTION=[('ati_structures','*ATi*jar','https://www.curseforge.com/minecraft/mc-mods/ati-structures',[
        'haunted_ruin/haunted_ruin','haunted_ruin/haunted_ruin2','haunted_ruin/haunted_ruin3'])]
    m.main()
    src=json.loads((OUT/'sources.json').read_text());contexts=[];states={}
    reader=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
    for c in src['candidates']:
        ident='ati_structures:'+c['member'].split('/structures/',1)[1][:-4]
        c['pool_references']=[r for r in c['pool_references'] if any(e['element'].get('location')==ident for e in r['data'].get('elements',[]))]
        with ZipFile(c['source_archive']) as z:
            n=reader.read(z.read(c['member']));pal=n['palette'];ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']};states[c['id']]=ss
            resources=[]
            for member in ['data/ati_structures/worldgen/structure/haunted_ruin.json','data/ati_structures/worldgen/template_pool/haunted_ruin.json','data/ati_structures/tags/worldgen/biome/haunted_ruin.json','data/minecraft/worldgen/processor_list/mossify_20_percent.json']:
                present=member in z.namelist();r=dict(member=member,present=present)
                if present:
                    raw=z.read(member);r.update(sha256=sha(raw),data=json.loads(raw))
                resources.append(r)
            manifest_members=[p for p in z.namelist() if p in ('META-INF/mods.toml','fabric.mod.json','pack.mcmeta')]
            manifests=[dict(member=p,sha256=sha(z.read(p)),text=z.read(p).decode()) for p in manifest_members]
            contexts.append(dict(id=c['id'],resources=resources,manifests=manifests,
                block_entities=[b for b in n['blocks'] if b.get('nbt')],entities=n['entities'],
                stored_positions=len(ss),explicit_air=sum(s['Name']=='minecraft:air' for s in ss.values()),
                omitted_positions=n['size'][0]*n['size'][1]*n['size'][2]-len(ss),
                notable_states=[dict(position=q,state=s) for q,s in ss.items() if any(t in s['Name'] for t in ('candle','skull','chest','tnt','dispenser','soul_sand'))],
                native_purpose_not_inferred_from_name_or_hostile_entity=True))
    comparisons=[]
    for a,b in itertools.combinations(states,2):
        sa,sb=states[a],states[b];union=sa.keys()|sb.keys();common=sa.keys()&sb.keys()
        comparisons.append(dict(pair=[a,b],left_stored=len(sa),right_stored=len(sb),common_positions=len(common),
            identical_original_states=sum(sa[p]==sb[p] for p in common),changed_or_absent_positions=sum(sa.get(p)!=sb.get(p) for p in union),
            transform='Original axes, no rotation, no normalization; comparison alone does not establish distinct architectural families.'))
    dump('sources.json',src)
    dump('author-context.json',dict(entries=contexts,pairwise_raw_state_comparisons=comparisons,network_requests=0,java_run=False,game_run=False,
        purpose_boundary='Haunted name, soul sand, skulls or illusioner do not by themselves prove burial or ritual use. Root selects one of three alternatives, not an assembled three-part building.'))
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text());d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries']);d['formal_count_annotation_corrected_from_legacy_helper']=True;dump('dedup-evidence.json',d)
if __name__=='__main__':main()
