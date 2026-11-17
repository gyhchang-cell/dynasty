"""Offline integrity checks for the mansion exclusion and immutable history."""
import ast
from collections import Counter,defaultdict
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
    f=module('fields038',BASE/'research-20261103-dungeons-038/finalize_review.py')
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:v.check(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in range(36,39)]
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');assert src['new_source_templates']==1 and src['automatic_credit']==src['previous_source_template_rereads']==0
    c=src['candidates'][0];a=get(OUT/'raw-source-audit.json')['entries'][0]
    h=get(OUT/'dedup-evidence.json')['entries'][0];sel=get(OUT/'selection-role-audit.json')
    assert len(src['candidates'])==len(src['source_archives'])==1
    for e in src['source_archives']:assert sha(Path(e['path']).read_bytes())==e['sha256']
    with ZipFile(c['source_archive']) as z:
        raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']
        d=v.read(raw);assert d['size']==c['size']==[33,30,32]
        pal=d.get('palette') or d['palettes'][0]
        states={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
        assert len(states)==len(d['blocks']) and all(0<=p[i]<d['size'][i] for p in states for i in range(3))
        cs={p:s for p,s in states.items() if s['Name'] not in v.AIR}
        assert len(cs)==c['nonair'] and Counter(s['Name'] for s in cs.values())==c['materials']
        doors=[dict(position=list(p),state=s) for p,s in states.items() if s['Name'].endswith('_door') and s.get('Properties',{}).get('half')=='lower']
        detail=get(OUT/'detail-evidence.json')['entries'][0]
        assert sorted(doors,key=lambda x:x['position'])==sorted(detail['lower_doors'],key=lambda x:x['position']) and len(doors)==22
        ladders=defaultdict(list)
        for (x,y,zz),s in states.items():
            if s['Name']=='minecraft:ladder':ladders[(x,zz)].append(y)
        assert {k:sorted(ys) for k,ys in ladders.items()}=={(28,9):[8,9,10]}
        assert detail['ladder_runs']==[dict(x=28,z=9,ys=[8,9,10])]
        assert c['sockets']==[] and not any(s['Name']=='minecraft:jigsaw' for s in states.values())
        assert c['entities']==[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]
        assert Counter(e['id'] for e in c['entities'])=={'minecraft:armor_stand':8,'minecraft:painting':8,'minecraft:item_frame':5}
        for e in a['archive_json_identity_mentions']+sel['author_resources']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        assert a['outgoing_pools']==[]
        direct=[]
        for e in sel['relations']:
            raw=z.read(e['member']);data=json.loads(raw);hits=list(f.fields(data,sel['target']))
            assert sha(raw)==e['sha256'] and hits==e['matching_fields']
            assert e['directly_selects_template']==any(p.endswith('.location') for p in hits)
            if e['directly_selects_template']:direct.append(dict(member=e['member'],data=data))
        assert direct==c['pool_references'] and len(direct)==sel['direct_location_selection_pools']==1
        root=sel['author_resources'][0]['data']
        assert root['start_pool']=='simply_houses:plains_mansion/plains_mansion_main' and root['terrain_adaptation']=='beard_thin' and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'
        manifest=z.read('META-INF/mods.toml');assert sha(manifest)==sel['manifest_sha256'] and manifest.decode()==sel['manifest_text']
    bounds=[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
    assert bounds==a['occupied_bounds']==detail['occupied_bounds']==[[0,32],[0,28],[0,31]]
    assert h['occupancy_sha256']==v.geometry_hash({p:1 for p in cs},c['size'])
    assert h['role_sha256']==v.geometry_hash({p:v.role(s['Name']) for p,s in cs.items()},c['size'])
    assert not h['historical_exact_matches']
    de=get(OUT/'dedup-evidence.json');assert de['historical_unique_local_archive_member_pairs']==227 and not de['within_batch_exact_duplicate_pairs']
    review=get(OUT/'manual-review.json');r=review['entries'][0]
    assert review['independent_references_added']==r['credit']==0 and r['credit_identity'] is None
    v.check(r['source_evidence']);assert r['source_candidate_id']==c['id']
    assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    assert not r['native_acceptance'] and not r['independent_human_review']
    assert len(r['actual_images_viewed'])==review['actual_images_viewed']==2
    for e in r['actual_images_viewed']:v.check(e,True)
    scope=get(OUT/'scoped-reference-update.json');v.check(scope['prior_update']);prior=get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and [s['accepted_references'] for s in scope['scopes']]==[9,10,1]
    assert scope['added_ids']==[] and scope['added_credit']==0 and scope['new_source_discoveries']==1
    assert scope['prior_038_exclusions_retained']==prior['current_batch_exclusions']
    changed={'prior_update','new_source_discoveries','current_batch_exclusions','limits'}
    assert all(scope[k]==value for k,value in prior.items() if k not in changed)
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:v.check(e)
    assert discovery['local_only'] and not discovery['java_run'] and not discovery['game_run']
    assert discovery['network_requests']==discovery['production_changes']==discovery['checklist_deletions']==discovery['sound_brightness_window_save_changes']==0
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_RESIDENTIAL_SCOPE_EXCLUSION',date='2026-11-03',batch=39,
        new_source_templates=1,actual_images_viewed=2,new_valid_scoped_references=0,
        direct_location_selection_pools=1,scoped_counts=[9,10,1],remaining=[991,990,999],
        prior_receipt_packages_unchanged=len(preserved),all_prior_observations_holds_and_exclusions_retained=True,
        construction_allowed=False,native_routes_verified=False,java_run=False,game_run=False,network_requests=0,
        production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=39,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scoped-reference-update.json'),
        review=evidence(OUT/'manual-review.json'),shared_coordinator_session_not_overwritten=True,
        main_checklist_edits=0,duration_hours_claimed=0,complete_production_task=False,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
