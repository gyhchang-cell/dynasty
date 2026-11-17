"""Offline byte integrity and ledger continuity; no native game acceptance."""
import ast
from collections import Counter,defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
from reference_components import geometry_hash,role

def sha(b):
    return hashlib.sha256(b).hexdigest()

def get(p):
    return json.loads(p.read_text())

def dump(n,v):
    (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def evidence(e,image=False):
    p=Path(e['path']);assert sha(p.read_bytes())==e['sha256'],p
    if image:
        with Image.open(p) as im:im.verify()

def main():
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:evidence(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/'research-20261102-dungeons-033']
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');de=get(OUT/'dedup-evidence.json');boundary=get(OUT/'boundary-evidence.json')
    assert src['new_source_templates']==4 and src['previous_source_template_rereads']==src['automatic_credit']==0
    assert len(src['candidates'])==4 and len(src['source_archives'])==1
    for a in src['source_archives']:assert sha(Path(a['path']).read_bytes())==a['sha256']
    assert de['historical_unique_local_archive_member_pairs']==221 and not de['within_batch_exact_duplicate_pairs']
    assert boundary['archive']==src['source_archives'][0] and not boundary['classes_loaded'] and not boundary['java_run']
    spec=importlib.util.spec_from_file_location('boundary_reader',OUT/'inspect_boundary.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    occupied={}
    with ZipFile(src['source_archives'][0]['path']) as z:
        manifest=z.read('META-INF/mods.toml')
        assert sha(manifest)==boundary['manifest_sha256'] and manifest.decode()==boundary['manifest_text']
        for e in boundary['author_resources']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        for e in boundary['static_class_string_evidence']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and m.constants(raw)==e['relevant_utf8_constants']
            assert not e['executed'] and e['placement_offsets_not_inferred']
        strings={e['value'] for e in boundary['static_class_string_evidence'][0]['relevant_utf8_constants']}
        assert all(f'guling_{i}' in strings for i in range(1,5))
        author=boundary['author_resources'][0]['data']
        assert author['type']=='eeeabsmobs:guling' and author['step']=='underground_decoration'
        assert boundary['author_resources'][2]['data']['values']==['#forge:is_underground']
        for c,a,h,b in zip(src['candidates'],get(OUT/'raw-source-audit.json')['entries'],de['entries'],boundary['entries']):
            assert c['id']==a['id']==h['id']==b['id']
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==b['nbt_sha256']
            d=read(raw);assert d['size']==c['size']
            pal=d.get('palette') or d['palettes'][0]
            states={tuple(r['pos']):pal[r['state']] for r in d['blocks']}
            assert len(states)==len(d['blocks']) and all(0<=p[i]<d['size'][i] for p in states for i in range(3))
            cs={p:v for p,v in states.items() if v['Name'] not in AIR}
            assert len(cs)==c['nonair'] and Counter(v['Name'] for v in cs.values())==c['materials']
            assert c['entities']==[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]
            assert c['doors']==[dict(position=list(p),state=v) for p,v in states.items() if v['Name'].endswith('_door') and v.get('Properties',{}).get('half')=='lower']
            assert not c['sockets'] and not c['pool_references']
            assert not any(v['Name']=='minecraft:jigsaw' for v in states.values())
            assert a['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
            assert h['occupancy_sha256']==geometry_hash({p:1 for p in cs},c['size'])
            assert h['role_sha256']==geometry_hash({p:role(v['Name']) for p,v in cs.items()},c['size'])
            assert not h['historical_exact_matches']
            assert b['entity_id_counts']==Counter(e.get('nbt',{}).get('id','') for e in d.get('entities',[]))
            for edge in b['boundary_profiles']:
                on={p:v for p,v in cs.items() if p[edge['axis']]==edge['coordinate']}
                assert len(on)==edge['nonair']
                assert all(sum(p[1]==int(y) for p in on)==n for y,n in edge['occupied_y_counts'].items())
            for e in a['archive_json_identity_mentions']:
                raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
            assert not a['outgoing_pools']
            occupied[c['id']]=cs
    for r in get(OUT/'detail-evidence.json')['entries']:
        assert [e['coordinate'] for e in r['cuts']]==[10,25,13,13]
        ladders=defaultdict(list)
        for p,v in occupied[r['id']].items():
            if v['Name']=='minecraft:ladder':ladders[(p[0],p[2])].append(p[1])
        assert sorted(r['ladder_runs'],key=lambda v:(v['x'],v['z']))==[dict(x=x,z=z,ys=sorted(ys)) for (x,z),ys in sorted(ladders.items())]
    review=get(OUT/'manual-review.json');imgs=set()
    assert review['new_source_templates']==4 and review['independent_references_added']==0
    assert not review['independent_human_review_claimed']
    for r,c in zip(review['entries'],src['candidates']):
        assert r['source']==c and r['credit']==0 and r['credit_identity'] is None
        assert not r['native_acceptance'] and not r['independent_human_review'] and not r['complete_building_identity_confirmed']
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        for e in r['actual_images_viewed']:evidence(e,True);imgs.add(e['path'])
    assert len(imgs)==review['actual_unique_images_viewed']==8
    scope=get(OUT/'scoped-reference-update.json')
    for k in ('prior_update','original_scope_definitions','previous_hold_evidence','height_basis_question_retained'):evidence(scope[k])
    prior=get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and not scope['added_ids'] and scope['added_credit']==0
    assert [s['accepted_references'] for s in scope['scopes']]==[8,10,1]
    for k in ('previous_two_holds_retained','other_holds_retained','recent_holds_retained','prior_58_block_assembly_exclusion_retained','prior_other_exclusions_retained','prior_additional_holds_retained','prior_ice_holds_retained','current_batch_holds'):
        assert scope[k]==prior[k]
    assert scope['prior_review_exclusions_retained']==prior['current_batch_exclusions']
    assert len(scope['current_batch_exclusions'])==4
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:evidence(e)
    assert discovery['local_only'] and discovery['production_changes']==discovery['checklist_deletions']==discovery['network_requests']==discovery['sound_brightness_window_save_changes']==0
    assert not discovery['java_run'] and not discovery['game_run']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_UNDERGROUND_TEMPLATE_BOUNDARY_EXCLUSION',batch=34,new_source_templates=4,
      actual_images_viewed=8,new_valid_scoped_references=0,scoped_counts=[8,10,1],remaining=[992,990,999],
      prior_receipt_packages_unchanged=len(preserved),construction_allowed=False,all_prior_holds_and_exclusions_retained=True,
      static_class_strings_only=True,classes_executed=False,native_composition_routes_or_terrain_acceptance=False,
      independent_human_review_claimed=False,java_run=False,game_run=False,network_requests=0,
      production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',report)
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    main()
