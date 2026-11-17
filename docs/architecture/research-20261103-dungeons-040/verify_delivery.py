"""Check fixed sources, raw markers, review limits and preserved receipts offline."""
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))

def main():
    v=module('helpers036',BASE/'research-20261103-dungeons-036/verify_delivery.py')
    inspector=module('boundary040',OUT/'inspect_boundary.py')
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:v.check(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in range(36,40)]
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');assert src['new_source_templates']==2 and src['automatic_credit']==src['previous_source_template_rereads']==0
    assert len(src['source_archives'])==1 and len(src['candidates'])==2
    archive=src['source_archives'][0];assert sha(Path(archive['path']).read_bytes())==archive['sha256']
    boundary=get(OUT/'boundary-evidence.json');audit=get(OUT/'raw-source-audit.json')['entries']
    detail=get(OUT/'detail-evidence.json')['entries'];dedup=get(OUT/'dedup-evidence.json')
    assert dedup['historical_unique_local_archive_member_pairs']==228 and not dedup['within_batch_exact_duplicate_pairs']
    assert boundary['archive']==archive and not boundary['classes_loaded'] and not boundary['java_run']
    with ZipFile(archive['path']) as z:
        for c,a,b,d,h in zip(src['candidates'],audit,boundary['entries'],detail,dedup['entries']):
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==a['nbt_sha256']==b['nbt_sha256']
            root=v.read(raw);assert root['size']==c['size']==a['size']
            pal=root.get('palette') or root['palettes'][0]
            states={tuple(x['pos']):pal[x['state']] for x in root['blocks']}
            assert len(states)==len(root['blocks']) and all(0<=p[i]<root['size'][i] for p in states for i in range(3))
            cells={p:s for p,s in states.items() if s['Name'] not in v.AIR}
            assert len(cells)==c['nonair'] and Counter(s['Name'] for s in cells.values())==c['materials']==a['materials']
            bounds=[[min(p[i] for p in cells),max(p[i] for p in cells)] for i in range(3)]
            assert bounds==a['occupied_bounds']==d['occupied_bounds']
            assert c['entities']==c['sockets']==c['doors']==c['pool_references']==[] and not root.get('entities',[])
            assert not any(s['Name']=='minecraft:jigsaw' or s['Name']=='minecraft:ladder' or s['Name'].endswith('_door') for s in states.values())
            assert a['outgoing_pools']==a['archive_json_identity_mentions']==[]
            markers=[dict(position=x['pos'],state=pal[x['state']],data=x['nbt']) for x in root['blocks'] if x.get('nbt') and pal[x['state']]['Name'] in ['minecraft:structure_block','structure_gel:data_handler']]
            assert markers==b['markers'] and not b['gel_processing_verified'] and not b['complete_building_identity_confirmed']
            if c['id']=='F01':
                assert c['size']==[29,32,29] and bounds==[[0,28],[0,31],[0,28]]
                assert c['materials']['structure_gel:blue_gel']==8724 and c['materials']['structure_gel:yellow_gel']==1282 and b['original_gel_cells']==10006
                assert Counter(m['data']['metadata'] for m in markers)=={'loot_chest':3,'platinum_chest':1,'boss':1}
                assert next(m['position'] for m in markers if m['data']['metadata']=='boss')==[14,30,14]
            else:
                assert c['size']==[47,23,47] and len(markers)==68
                assert all(h['type']=='structure_gel:configured_feature' and h['entries']['feature']=='aether:crystal_tree' for m in markers for h in m['data']['handlers'])
            assert h['occupancy_sha256']==v.geometry_hash({p:1 for p in cells},c['size'])
            assert h['role_sha256']==v.geometry_hash({p:v.role(s['Name']) for p,s in cells.items()},c['size'])
            assert not h['historical_exact_matches']
        for e in boundary['author_resources']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        for e in boundary['static_class_string_evidence']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and inspector.constants(raw)==e['relevant_utf8_constants']
            assert not e['executed'] and e['placement_offsets_not_inferred']
        assert len(boundary['static_class_string_evidence'])==4
        raw=z.read('META-INF/mods.toml');assert sha(raw)==boundary['manifest_sha256'] and raw.decode()==boundary['manifest_text']
        assert boundary['author_resources'][0]['data']['type']=='lost_aether_content:platinum_dungeon'
    review=get(OUT/'manual-review.json');assert review['actual_images_viewed']==4 and review['independent_references_added']==0
    actual=[]
    for r in review['entries']:
        v.check(r['source_evidence']);assert r['credit']==0 and r['credit_identity'] is None
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        assert not r['complete_author_complex_boundary_confirmed'] and not r['native_acceptance'] and not r['independent_human_review']
        for e in r['actual_images_viewed']:v.check(e,True);actual.append(e['path'])
    assert len(actual)==len(set(actual))==4 and review['diagnostic_mask_is_not_native_output']
    scope=get(OUT/'scoped-reference-update.json');v.check(scope['prior_update']);prior=get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and [s['accepted_references'] for s in scope['scopes']]==[9,10,1]
    assert scope['added_ids']==[] and scope['added_credit']==0 and scope['new_source_discoveries']==2
    assert scope['prior_039_exclusions_retained']==prior['current_batch_exclusions'] and len(scope['current_batch_boundary_holds'])==2
    changed={'prior_update','new_source_discoveries','current_batch_exclusions','current_batch_boundary_holds','limits'}
    assert all(scope[k]==value for k,value in prior.items() if k not in changed)
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:v.check(e)
    assert discovery['local_only'] and not discovery['java_run'] and not discovery['game_run'] and not discovery['full_author_complex_assembled']
    assert discovery['network_requests']==discovery['production_changes']==discovery['checklist_deletions']==discovery['sound_brightness_window_save_changes']==0
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_CUSTOM_TOWER_GROUND_BOUNDARY_HOLD',date='2026-11-03',batch=40,
        new_source_templates=2,actual_images_viewed=4,new_valid_scoped_references=0,
        original_gel_cells=10006,ground_feature_handlers=68,full_author_complex_assembled=False,
        gel_processing_verified=False,scoped_counts=[9,10,1],remaining=[991,990,999],
        prior_receipt_packages_unchanged=len(preserved),all_prior_observations_holds_and_exclusions_retained=True,
        construction_allowed=False,native_routes_verified=False,java_run=False,game_run=False,network_requests=0,
        production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=40,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scoped-reference-update.json'),
        review=evidence(OUT/'manual-review.json'),shared_coordinator_session_not_overwritten=True,
        main_checklist_edits=0,duration_hours_claimed=0,complete_production_task=False,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
