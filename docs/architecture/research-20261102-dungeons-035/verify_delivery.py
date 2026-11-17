"""Verify queue partition, original archive bytes and immutable prior deliveries."""
from collections import Counter,defaultdict
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent

def sha(b):
    return hashlib.sha256(b).hexdigest()

def get(p):
    return json.loads(p.read_text())

def dump(n,v):
    (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def evidence(e):
    assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']

def main():
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:evidence(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in (33,34)]
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    inputs=get(OUT/'input-evidence.json')
    for e in [inputs['queue'],inputs['metadata'],inputs['fixed_inventory']]+inputs['historical_indices']+inputs['archives']:evidence(e)
    spec=importlib.util.spec_from_file_location('queue_reader',OUT/'reconcile_queue.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    spec=importlib.util.spec_from_file_location('history',BASE/'research-20261101-dungeons-002/check_dedup.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    history={}
    for e in inputs['historical_indices']:h.find_records(get(Path(e['path'])),e['path'],history)
    assert len(history)==225
    report=get(OUT/'queue-reconciliation.json');rows=report['entries'];summary=report['summary']
    original_rows=get(Path(inputs['queue']['path']))['entries']
    key=lambda r:(r['source_archive'],r['member'])
    originals={key(r):r for r in original_rows}
    assert len(originals)==len(rows)==summary['queue_rows']==479
    assert set(originals)=={key(r) for r in rows}
    groups=defaultdict(list)
    for r in rows:groups[r['source_archive']].append(r)
    resources=defaultdict(list)
    for r in inputs['template_pool_resources']:resources[r['archive']].append(r)
    for archive,group in groups.items():
        with ZipFile(archive) as z:
            pools={}
            for e in resources[archive]:
                raw=z.read(e['member']);assert sha(raw)==e['sha256']
                pools[e['member']]=set(m.locations(json.loads(raw)))
            for r in group:
                raw=z.read(r['member']);assert sha(raw)==r['nbt_sha256']
                d=m.read(raw);assert d['size']==r['size']==originals[key(r)]['size']
                pal=d.get('palette') or d['palettes'][0]
                ps=[tuple(b['pos']) for b in d['blocks'] if pal[b['state']]['Name'] not in m.AIR]
                bounds=[[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(3)]
                assert bounds==r['occupied_bounds']==originals[key(r)]['occupied_bounds']
                assert r['occupied_height']==bounds[1][1]-bounds[1][0]+1
                assert r['stored_height_padding']==d['size'][1]-r['occupied_height']
                sockets=[dict(position=b['pos'],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
                assert sockets==r['jigsaw_interfaces']
                prefix,tail=r['member'].split('/structures/',1);identifier=prefix.split('/')[-1]+':'+tail[:-4]
                for e in r['direct_exact_location_pool_mentions']:assert identifier in pools[e['member']]
                indices=sorted(set(history.get(key(r),{}).get('prior_indices',[])))
                assert r['historical_indices']==indices
                assert bool(indices)==(r['next_review_route']=='ALREADY_IN_STUDY_INDEX_REUSE_EXISTING_DECISION')
                assert r['building_credit']==0 and not r['actual_visual_reading_in_this_batch'] and not r['complete_building_identity_confirmed']
    assert summary['routes']==Counter(r['next_review_route'] for r in rows)
    assert summary['historical_queue_rows']==56 and summary['unmatched_queue_rows']==423
    assert summary['historical_queue_rows']+summary['unmatched_queue_rows']==479
    assert summary['archives_rechecked']==len(groups)==22
    assert len(inputs['template_pool_resources'])==194
    assert summary['actual_visual_readings']==summary['new_visually_studied_sources']==summary['new_valid_scoped_references']==0
    scope=get(OUT/'scoped-reference-update.json');evidence(scope['prior_update'])
    prior=get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and not scope['added_ids'] and scope['added_credit']==scope['new_source_discoveries']==0
    assert scope['prior_034_exclusions_retained']==prior['current_batch_exclusions'] and not scope['current_batch_exclusions']
    changed={'prior_update','current_batch_exclusions','limits','new_source_discoveries'}
    assert all(scope[k]==v for k,v in prior.items() if k not in changed)
    assert [s['accepted_references'] for s in scope['scopes']]==[8,10,1]
    boundary=get(OUT/'discovery-boundary.json')
    assert boundary['local_only'] and not boundary['java_run'] and not boundary['game_run']
    assert all(boundary[k]==0 for k in ('network_requests','production_changes','checklist_deletions','sound_brightness_window_save_changes','actual_images_viewed','new_source_templates_visually_studied','building_credit_added'))
    assert not list(OUT.glob('*.png')) and not (OUT/'sources.json').exists()
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    result=dict(status='PASS_METADATA_QUEUE_RECONCILED_WITH_NO_REFERENCE_CREDIT',batch=35,
      queue_rows=479,historical_queue_rows=56,unmatched_queue_rows=423,archives_rechecked=22,
      template_pool_resources_verified=194,actual_images_viewed=0,new_valid_scoped_references=0,
      scoped_counts=[8,10,1],remaining=[992,990,999],prior_receipt_packages_unchanged=len(preserved),
      construction_allowed=False,all_prior_holds_and_exclusions_retained=True,
      metadata_is_not_visual_reference=True,java_run=False,game_run=False,network_requests=0,
      production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',result)
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=result['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    main()
