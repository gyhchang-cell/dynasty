"""Fixed local authored small altar: four orientations, at most one design."""
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
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def normalize(ss):
    mins=[min(p[i] for p in ss) for i in range(3)]
    return {tuple(p[i]-mins[i] for i in range(3)):s for p,s in ss.items()}
def rotate(ss):
    out={}
    for (x,y,z),s in ss.items():
        s=json.loads(json.dumps(s));props=s.get('Properties',{})
        if props.get('axis') in ('x','z'):props['axis']='z' if props['axis']=='x' else 'x'
        out[(-z,y,x)]=s
    return normalize(out)
def main():
    m=load('inspect017',BASE/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('touhou_little_maid','*touhoulittlemaid*jar','https://github.com/TartaricAcid/TouhouLittleMaid',
        ['altar_north','altar_east','altar_south','altar_west'])]
    m.main()
    src=json.loads((OUT/'sources.json').read_text());reader=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
    contexts=[];states={}
    for c in src['candidates']:
        with ZipFile(c['source_archive']) as z:
            n=reader.read(z.read(c['member']));ss={tuple(b['pos']):n['palette'][b['state']] for b in n['blocks']};states[c['id']]=normalize(ss)
            contexts.append(dict(id=c['id'],original_blocks=n['blocks'],palette=n['palette'],entities=n['entities'],
                stored_positions=len(ss),explicit_air=sum(s['Name']=='minecraft:air' for s in ss.values()),
                omitted_positions=n['size'][0]*n['size'][1]*n['size'][2]-len(ss),
                stored_placement_origin_not_native_ground=True))
    with ZipFile(src['candidates'][0]['source_archive']) as z:
        members=['META-INF/mods.toml','META-INF/MANIFEST.MF',
            'assets/touhou_little_maid/patchouli_books/memorizable_gensokyo/en_us/entries/overview/multiblocks_altar.json',
            'data/touhou_little_maid/tags/blocks/altar_pillar.json','data/touhou_little_maid/tags/blocks/altar_torii.json',
            'data/touhou_little_maid/recipes/altar/spawn_box.json','data/touhou_little_maid/recipes/altar/reborn_maid.json',
            'data/touhou_little_maid/advancements/base/build_altar.json']
        resources=[]
        for member in members:
            raw=z.read(member);r=dict(member=member,sha256=sha(raw))
            r['data' if member.endswith('.json') else 'text']=json.loads(raw) if member.endswith('.json') else raw.decode()
            resources.append(r)
        lang_member='assets/touhou_little_maid/lang/zh_cn.json';raw=z.read(lang_member);lang=json.loads(raw)
        lang_subset={k:v for k,v in lang.items() if 'entries.overview.multiblocks_altar.' in k or k.startswith('advancements.touhou_little_maid.base.build_altar.')}
        png_member='assets/touhou_little_maid/textures/book/altar.png';png=z.read(png_member);(OUT/'author-altar.png').write_bytes(png)
        mentions=[]
        needles=[('touhou_little_maid:'+c['member'].split('/structures/')[1][:-4]).encode() for c in src['candidates']]
        for member in z.namelist():
            if member.endswith('.json'):
                raw_json=z.read(member)
                if any(s in raw_json for s in needles):mentions.append(member)
    rotations=[]
    ref=states['F01']
    for ident,target in states.items():
        cur=ref;matches=[]
        for quarter in range(4):
            if cur==target:matches.append(quarter)
            cur=rotate(cur)
        rotations.append(dict(id=ident,matching_quarter_turns_from_F01=matches,translation_normalized=True,
            original_block_names_and_axis_properties_compared=True,non_rotation_changes_required=not bool(matches)))
    dump('author-context.json',dict(entries=contexts,resources=resources,
        chinese_language=dict(member=lang_member,sha256=sha(raw),selected_strings=lang_subset),
        original_author_image=dict(member=png_member,sha256=sha(png),local_file='author-altar.png',unaltered=True,research_only=True),
        json_template_identifier_mentions=mentions,rotation_comparison=rotations,
        limits='Book text and original unaltered author image establish intended multiblock purpose; no runtime activation or world placement verified. Omitted positions are not air instructions.',
        java_run=False,game_run=False,network_requests=0,formal_credit_added=0))
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text());d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries']);d['formal_count_annotation_corrected_from_legacy_helper']=True;dump('dedup-evidence.json',d)
if __name__=='__main__':main()
