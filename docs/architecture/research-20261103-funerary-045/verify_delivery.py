"""Bind this batch to original resources and the accepted formal-count transition."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
from reference_components import geometry_hash,role
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def check(e):assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']
def main():
    previous=BASE/'research-20261103-funerary-044'
    for e in get(previous/'RECEIPT.json')['files']:
        p=previous/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json');author=get(OUT/'author-context.json');review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json')
    assert len(src['candidates'])==len(author['entries'])==len(review['entries'])==2 and src['automatic_credit']==0
    archive=src['source_archives'][0];assert sha(Path(archive['path']).read_bytes())==archive['sha256']=='fea95f69d7d023a8d990c043ee63bc07ea0a85cde1a558b369ef4884d3ac5012'
    with ZipFile(archive['path']) as z:
        for c,a,h,ctx in zip(src['candidates'],audit['entries'],dedup['entries'],author['entries']):
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==a['nbt_sha256']==h['nbt_sha256'];n=read(raw)
            assert n['size']==c['size']==a['size'];p=n['palette'];ss={tuple(b['pos']):p[b['state']] for b in n['blocks']};cs={q:s for q,s in ss.items() if s['Name'] not in AIR}
            assert len(ss)==len(n['blocks']) and all(0<=q[i]<c['size'][i] for q in ss for i in range(3))
            assert Counter(s['Name'] for s in cs.values())==c['materials']==a['materials'] and len(cs)==c['nonair']
            assert a['occupied_bounds']==[[min(q[i] for q in cs),max(q[i] for q in cs)] for i in range(3)]
            assert c['sockets']==c['doors']==a['sockets']==a['outgoing_pools']==[]
            assert ctx['stored_positions']==len(ss) and ctx['explicit_air']==0 and ctx['omitted_positions']==c['size'][0]*c['size'][1]*c['size'][2]-len(ss)
            assert ctx['entities']==n['entities']==[] and ctx['block_entities']==[b for b in n['blocks'] if b.get('nbt')]
            assert ctx['candle_and_fire_states']==[dict(position=list(q),state=s) for q,s in ss.items() if s['Name'] in ('minecraft:candle','minecraft:campfire','minecraft:fire','minecraft:soul_fire')]
            assert ctx['bone_states']==[dict(position=list(q),state=s) for q,s in ss.items() if s['Name']=='minecraft:bone_block']
            assert sha(z.read('META-INF/mods.toml'))==ctx['manifest_sha256'] and z.read('META-INF/mods.toml').decode()==ctx['manifest_text']
            for e in ctx['resources']:assert sha(z.read(e['member']))==e['sha256'] and json.loads(z.read(e['member']))==e['data']
            assert h['occupancy_sha256']==geometry_hash({q:1 for q in cs},c['size']) and h['role_sha256']==geometry_hash({q:role(s['Name']) for q,s in cs.items()},c['size']) and h['historical_exact_matches']==[]
            pool=c['pool_references'];assert len(pool)==1 and len(pool[0]['data']['elements'])==1
            element=pool[0]['data']['elements'][0]['element'];assert element['location']=='trek:'+c['member'].split('/structures/',1)[1][:-4] and element['projection']=='terrain_matching'
        assert len(author['entries'][0]['bone_states'])==6 and [e['stored_positions'] for e in author['entries']]==[270,68] and [e['omitted_positions'] for e in author['entries']]==[5346,777]
        fires=author['entries'][1]['candle_and_fire_states'];assert len(fires)==9 and sum(e['state']['Properties']['lit']=='true' for e in fires)==2
        processor=next(e['data'] for e in author['entries'][1]['resources'] if '/processor_list/' in e['member'])
        rules=processor['processors'][0]['rules'];brick=[r for r in rules if r['input_predicate']['block']=='minecraft:stone_bricks']
        assert [r['input_predicate']['probability'] for r in brick]==[0.375,0.6]
    assert dedup['historical_unique_local_archive_member_pairs']==237 and dedup['within_batch_exact_duplicate_pairs']==[] and dedup['formal_identity_records_checked']==149
    assert dedup['formal_count_annotation_corrected_from_legacy_helper']
    check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']));assert scope['guard']==prior['guard'] and scope['guard']['reference_036_F01_formal_credit']==0
    fun=scope['funerary'];check(fun['baseline']);check(fun['coordinator_acceptance']);formal=get(Path(fun['baseline']['path']));accepted=get(Path(fun['coordinator_acceptance']['path']))
    assert len(formal['entries'])==fun['formal_baseline']==150 and fun['remaining_formal']==850
    assert accepted['formal_identity']=='COD4-R044-F01' and accepted['formal_count_before']==149 and accepted['formal_count_after']==150 and accepted['old149_complete_records_preserved']
    assert fun['coordinator_acceptance']['sha256']=='d46caeef4e56fd246fb2f2623b7a6c483932c94c30fcb3855ab7eead3958d602'
    assert len([e for e in formal['entries'] if e['id']=='COD4-R044-F01'])==1
    assert not fun['production_allowed'] and not fun['formal_register_written'] and not scope['pending_proposal_identities']
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:
        if Path(e['path'])==Path(fun['baseline']['path']):
            # This index was actually read at149, before coordinator acceptance.
            assert e==prior['funerary']['baseline'] and e['sha256']!=fun['baseline']['sha256']
            assert e==scope['discovery_formal_index_transition']['old_record']
        else:check(e)
    assert discovery['local_only'] and discovery['network_requests']==0 and not discovery['java_run'] and not discovery['game_run']
    images=[]
    for r in review['entries']:
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'} and r['formal_credit_added']==r['proposed_credit']==0
        assert not r['independent_human_review'] and not r['native_generation_or_collision_verified']
        for key in ('source_evidence','author_evidence'):check(r[key])
        images.extend(r['actual_images_viewed'])
    images.extend(review['old_comparison_images']);assert len(images)==len({e['path'] for e in images})==review['actual_images_viewed']==5
    for e in images:
        check(e)
        with Image.open(e['path']) as im:im.verify()
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_TWO_AUTHORED_SITES_HOLD0',date='2026-11-03',batch=45,
        source_templates_read=2,actual_new_images_viewed=4,actual_old_comparison_images_viewed=1,
        new_first_scope_proposals=0,formal_credit_added=0,funerary_formal_count=150,remaining_formal=850,
        previous_044_receipted_files_unchanged=True,previous_29_package_integrity_receipt_bound_not_reexecuted=evidence(previous/'verification.json'),
        formal_discovery_input149_retained=True,coordinator_transition149_to150_bound=True,
        reference_036_F01_formal_credit=0,old_D010_hold0_retained=True,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=45,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
