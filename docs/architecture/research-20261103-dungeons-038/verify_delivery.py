"""Verify citadel source, pool field roles and zero-credit scope decision offline."""
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
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))

def main():
    v=module('integrity_helpers',BASE/'research-20261103-dungeons-036/verify_delivery.py')
    f=module('selection_fields',OUT/'finalize_review.py')
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:v.check(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in (36,37)]
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');assert src['new_source_templates']==1 and src['automatic_credit']==src['previous_source_template_rereads']==0
    assert len(src['candidates'])==len(src['source_archives'])==1
    for a in src['source_archives']:assert sha(Path(a['path']).read_bytes())==a['sha256']
    c=src['candidates'][0];a=get(OUT/'raw-source-audit.json')['entries'][0]
    h=get(OUT/'dedup-evidence.json')['entries'][0];selection=get(OUT/'selection-role-audit.json')
    with ZipFile(c['source_archive']) as z:
        raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']
        d=v.read(raw);assert d['size']==c['size']==[31,33,31]
        pal=d.get('palette') or d['palettes'][0]
        states={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
        assert len(states)==len(d['blocks']) and all(0<=p[i]<d['size'][i] for p in states for i in range(3))
        cs={p:s for p,s in states.items() if s['Name'] not in v.AIR}
        assert len(cs)==c['nonair'] and Counter(s['Name'] for s in cs.values())==c['materials']
        assert c['doors']==[] and not any(s['Name'].endswith('_door') for s in states.values())
        assert not any(s['Name']=='minecraft:ladder' for s in states.values())
        assert c['entities']==[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]==[]
        assert c['sockets']==[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
        assert Counter(s['data']['pool'] for s in c['sockets'])=={'friendsandfoes:citadel/small_chain':12,'friendsandfoes:citadel/entity/wither_skeleton':8,'friendsandfoes:citadel/bridge/bridge_beginning':4,'friendsandfoes:citadel/entity/wildfire':1}
        for e in c['pool_references']:assert json.loads(z.read(e['member']))==e['data']
        mentions={e['member']:e for e in a['archive_json_identity_mentions']}
        for e in list(mentions.values())+selection['author_resources']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        for e in a['outgoing_pools']:
            assert not e['assembled'] and e['building_credit']==0 and e['status']=='FOUND_LOCAL'
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        direct=[]
        for e in selection['relations']:
            raw=z.read(e['member']);value=json.loads(raw);hits=list(f.fields(value,selection['target']))
            assert sha(raw)==e['sha256']==mentions[e['member']]['sha256']
            assert hits==e['matching_fields']
            assert e['directly_selects_template']==any(p.endswith('.location') for p in hits)
            assert e['shared_processor_only']==(not e['directly_selects_template'])
            if e['directly_selects_template']:direct.append(dict(member=e['member'],data=value))
            else:assert all(p.endswith('.processors') for p in hits)
        assert direct==c['pool_references'] and len(direct)==selection['direct_location_selection_pools']==1
        assert len(selection['relations'])==selection['exact_value_mentions']==11
        assert sum(e['shared_processor_only'] for e in selection['relations'])==selection['processor_only_mentions']==10
        manifest=z.read('META-INF/mods.toml');assert sha(manifest)==selection['manifest_sha256'] and manifest.decode()==selection['manifest_text']
    assert a['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]==[[0,30],[0,32],[0,30]]
    assert h['occupancy_sha256']==v.geometry_hash({p:1 for p in cs},c['size'])
    assert h['role_sha256']==v.geometry_hash({p:v.role(s['Name']) for p,s in cs.items()},c['size'])
    assert not h['historical_exact_matches']
    de=get(OUT/'dedup-evidence.json');assert de['historical_unique_local_archive_member_pairs']==226 and not de['within_batch_exact_duplicate_pairs']
    detail=get(OUT/'detail-evidence.json')['entries'][0]
    assert [r['coordinate'] for r in detail['cuts']]==[4,16,15,15] and detail['ladder_runs']==[]
    assert cs[(10,4,10)]['Name']==cs[(15,19,15)]['Name']=='minecraft:lava'
    root=selection['author_resources'][0]['data'];assert root['start_pool']=='friendsandfoes:citadel/base_plate' and root['terrain_adaptation']=='none'
    processor=selection['author_resources'][1]['data']['processors'][0]
    assert processor['processor_type']=='friendsandfoes:citadel_bottom_processor' and processor['target_block']['Name']=='minecraft:yellow_concrete'
    assert processor['target_block_output']['Name']=='minecraft:nether_bricks' and not selection['custom_bottom_processor_executed']
    review=get(OUT/'manual-review.json');r=review['entries'][0]
    assert review['independent_references_added']==r['credit']==0 and r['credit_identity'] is None
    assert r['source']==c and set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    assert not r['complete_author_complex_boundary_confirmed'] and not r['native_acceptance'] and not r['independent_human_review']
    assert len(r['actual_images_viewed'])==review['actual_images_viewed']==2
    for e in r['actual_images_viewed']:v.check(e,True)
    scope=get(OUT/'scoped-reference-update.json');v.check(scope['prior_update']);prior=get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and [s['accepted_references'] for s in scope['scopes']]==[9,10,1]
    assert scope['added_ids']==[] and scope['added_credit']==0 and scope['new_source_discoveries']==1
    assert scope['prior_keep_boundary_holds_retained']==prior['current_batch_boundary_holds'] and not scope['current_batch_boundary_holds']
    changed={'prior_update','new_source_discoveries','current_batch_exclusions','current_batch_boundary_holds','limits'}
    assert all(scope[k]==value for k,value in prior.items() if k not in changed)
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:v.check(e)
    assert discovery['local_only'] and not discovery['java_run'] and not discovery['game_run']
    assert discovery['network_requests']==discovery['production_changes']==discovery['checklist_deletions']==discovery['sound_brightness_window_save_changes']==0
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_CITADEL_SCOPE_EXCLUSION_AND_PRECISE_LOCATION_ROLE',date='2026-11-03',batch=38,
      new_source_templates=1,actual_images_viewed=2,new_valid_scoped_references=0,
      exact_value_pool_mentions=11,direct_location_selection_pools=1,processor_only_mentions=10,
      scoped_counts=[9,10,1],remaining=[991,990,999],prior_receipt_packages_unchanged=len(preserved),
      all_prior_observations_holds_and_exclusions_retained=True,construction_allowed=False,
      author_complex_boundary_or_native_routes_not_certified=True,java_run=False,game_run=False,network_requests=0,
      production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'))
    dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=38,
      session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scoped-reference-update.json'),
      review=evidence(OUT/'manual-review.json'),shared_coordinator_session_not_overwritten=True,
      main_checklist_edits=0,duration_hours_claimed=0,complete_production_task=False,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
