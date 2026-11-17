"""Verify the original inn and received048 transition, without Java or old reruns."""
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
sys.path.insert(0,str(BASE.parents[1]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
from reference_components import geometry_hash,role
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def check(e):assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']
def main():
    previous=BASE/'research-20261103-funerary-048'
    for e in get(previous/'RECEIPT.json')['files']:
        p=previous/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');ctx=get(OUT/'author-context.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json')
    review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json');task=get(OUT/'task-use-boundary.json');function=get(OUT/'functional-evidence.json')
    trans=scope['discovery_formal_index_transition'];check(trans['authority']);check(trans['current_formal_index'])
    authority=get(Path(trans['authority']['path']));assert authority['accepted_complete_designs']==1 and authority['prior_cod4_total']==150 and authority['cod4_total']==151 and authority['cod4_gap']==849
    assert trans['accepted_identity']=='COD4-R048-F01' and trans['accepted_previous_batch_credit']==1 and trans['current_batch_credit']==0
    assert trans['discovery_formal_index_before_acceptance']['sha256']=='3cca92c5cbc8aea69ca3f26ec38c8b02c13ee3053532d1e60c442e2c610b24ce'
    assert trans['current_formal_index']['sha256']=='0852fc0944b3e083a42cae4c00d07f343d0ca67e93595bbab1ab93cf2d2042aa'
    for e in get(OUT/'discovery-boundary.json')['indices_checked']:
        if e==trans['discovery_formal_index_before_acceptance']:continue
        check(e)
    assert len(src['candidates'])==len(src['source_archives'])==len(audit['entries'])==len(dedup['entries'])==1
    c=src['candidates'][0];archive=src['source_archives'][0]
    assert archive['publisher_url'] is None and c['publisher_url'] is None
    assert archive['sha256']==c['source_archive_sha256']==sha(Path(archive['path']).read_bytes())=='19600e85f62677245ca77428e2b16f0501ebd709c13bda24072675d3753a38c2'
    inv=get(BASE/'research-20261101-dungeons-024/fixed-source-screen.json')['archives']
    assert any(a['path']==archive['path'] and a['sha256']==archive['sha256'] for a in inv)
    with ZipFile(archive['path']) as z:
        raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==audit['entries'][0]['nbt_sha256']==dedup['entries'][0]['nbt_sha256'];n=read(raw)
        ss={tuple(b['pos']):n['palette'][b['state']] for b in n['blocks']};cells={p:s for p,s in ss.items() if s['Name'] not in AIR}
        assert len(ss)==len(n['blocks'])==ctx['stored_positions']==5699 and len(cells)==c['nonair']==3889
        assert n['size']==c['size']==[22,25,25] and all(0<=p[i]<n['size'][i] for p in ss for i in range(3))
        assert ctx['explicit_air']==sum(s['Name']=='minecraft:air' for s in ss.values())==1810 and ctx['omitted_positions']==8051
        assert Counter(s['Name'] for s in cells.values())==c['materials']==audit['entries'][0]['materials']
        assert audit['entries'][0]['occupied_bounds']==[[0,21],[0,21],[0,24]]
        assert ctx['block_entities']==[b for b in n['blocks'] if b.get('nbt')] and ctx['entities']==n['entities']
        assert Counter(e['nbt']['id'] for e in n['entities'])=={'minecraft:armor_stand':1,'minecraft:item_frame':1}
        for r in ctx['resources']:
            raw=z.read(r['member']);assert sha(raw)==r['sha256']
            assert (json.loads(raw) if r['member'].endswith(('.json','.mcmeta')) else raw.decode())==r.get('data',r.get('text'))
        root,pool,tag=[r['data'] for r in ctx['resources'][2:]]
        assert root['start_pool']=='simply_houses:taiga_inn/taiga_inn_main' and root['project_start_to_heightmap']=='WORLD_SURFACE_WG' and root['terrain_adaptation']=='beard_thin'
        assert tag['values']==['#minecraft:is_taiga'] and len(pool['elements'])==1
        element=pool['elements'][0]['element'];assert element['location']=='simply_houses:taiga_inn/taiga_inn' and element['processors']=='minecraft:empty' and element['projection']=='rigid'
        assert c['sockets']==audit['entries'][0]['sockets']==[] and len(c['pool_references'])==1 and c['pool_references'][0]['data']==pool
        for t in ctx['loot_tables']:
            assert t['present']==(t['member'] in z.namelist())
            if t['present']:assert sha(z.read(t['member']))==t['sha256'] and json.loads(z.read(t['member']))==t['data']
        missing=[t for t in ctx['loot_tables'] if not t['present']];assert len(missing)==1 and missing[0]['id']==function['missing_exact_loot_id']=='luna_structures:chests/taiga_inn/taiga_inn_barrels'
    assert Counter(b['nbt']['LootTable'] for b in ctx['block_entities'] if b['nbt'].get('LootTable'))==function['original_loot_reference_counts']
    assert function['original_loot_reference_counts'][function['missing_exact_loot_id']]==function['missing_exact_loot_reference_blocks']==4
    assert ctx['bed_states']==[dict(position=list(p),state=s) for p,s in ss.items() if s['Name'].endswith('_bed')]
    heads=[e for e in ctx['bed_states'] if e['state']['Properties']['part']=='head']
    assert heads==function['bed_heads'] and len(heads)==function['complete_beds_observed']==3 and len(ctx['bed_states'])==function['bed_block_states']==6
    for h in heads:
        x,y,z=h['position'];f=h['state']['Properties']['facing'];foot=ss[(x+(1 if f=='west' else -1),y,z)]
        assert foot['Name']==h['state']['Name'] and foot['Properties']['part']=='foot' and foot['Properties']['facing']==f
    doors=[dict(position=list(p),state=s) for p,s in ss.items() if s['Name'].endswith('_door')];assert ctx['doors']==doors
    assert {str(k):v for k,v in Counter(e['position'][1] for e in doors if e['state']['Properties']['half']=='lower').items()}==function['door_lower_counts_by_y']=={'0':1,'4':6,'10':5}
    for sign in function['inn_signs']:
        original=next(b['nbt'] for b in ctx['block_entities'] if b['pos']==sign['position'])
        assert all(original[k]==v for k,v in sign['texts'].items())
    assert len(function['inn_signs'])==1 and function['inn_signs'][0]['position']==[16,7,15]
    stairs=[dict(position=list(p),state=s) for p,s in ss.items() if s['Name'].endswith('_stairs')];assert stairs==ctx['stairs'] and len(stairs)==288
    h=dedup['entries'][0];assert h['occupancy_sha256']==geometry_hash({p:1 for p in cells},c['size']) and h['role_sha256']==geometry_hash({p:role(s['Name']) for p,s in cells.items()},c['size'])
    assert h['historical_exact_matches']==[] and dedup['within_batch_exact_duplicate_pairs']==[]
    assert dedup['historical_unique_local_archive_member_pairs']==249 and dedup['formal_identity_records_checked']==150
    check(task['task_source']);lines=Path(task['task_source']['path']).read_text().splitlines()
    for e in task['lines']:assert lines[e['line']-1]==e['text']
    check(task['existing_lodging_scope']);urban=get(Path(task['existing_lodging_scope']['path']))
    assert urban['scope_definition']==task['existing_definition'] and urban['accepted_references']==task['existing_accepted']==2
    assert not task['new_scope_definition'] and task['scoped_credit_added']==0 and task['candidate_occupied_height']==22
    assert len(review['entries'])==1 and review['actual_original_templates_visually_studied']==1
    e=review['entries'][0];assert e['formal_credit_added']==e['proposed_credit']==0 and e['complete_authored_designs_observed']==1
    assert not e['independent_human_review'] and not e['native_generation_or_collision_verified']
    assert set(e['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    for k in ('source_evidence','author_evidence','function_evidence'):check(e[k])
    assert len(e['actual_images_viewed'])==review['actual_new_images_viewed']==6 and len(review['actual_old_comparison_images_viewed'])==2
    for image in e['actual_images_viewed']+review['actual_old_comparison_images_viewed']:
        check(image)
        with Image.open(image['path']) as im:im.verify()
    check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']));assert scope['guard']==prior['guard'] and scope['guard']['reference_036_F01_formal_credit']==0
    check(scope['funerary']['baseline']);check(scope['funerary']['coordinator_acceptance']);check(scope['lodging']['baseline'])
    assert len(get(Path(scope['funerary']['baseline']['path']))['entries'])==scope['funerary']['formal_baseline']==151 and scope['funerary']['remaining_formal']==849
    assert scope['lodging']['formal_baseline']==2 and scope['lodging']['current_batch_added']==0 and not scope['pending_proposal_identities']
    assert not scope['funerary']['production_allowed'] and not scope['lodging']['production_allowed']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_COMPLETE_SMALLER_INN_READ_ONLY_SCOPE_BOUNDARY_RETAINED',date='2026-11-03',batch=49,
        actual_original_templates_visually_studied=1,actual_new_images_viewed=6,actual_old_comparison_images_viewed=2,
        complete_beds=3,missing_exact_loot_reference_blocks=4,native_routes_or_generation_verified=False,
        new_first_scope_proposals=0,formal_credit_added=0,lodging_formal_count=2,lodging_remaining=998,
        previous048_coordinator_credit_bound=1,funerary_formal_count=151,funerary_remaining=849,
        discovery_formal150_to151_transition_retained=True,previous_048_receipted_files_unchanged=True,
        earlier_integrity_bound_not_reexecuted=evidence(previous/'verification.json'),
        scope_definition_unchanged=True,source_exhaustion_claimed=False,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=49,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
