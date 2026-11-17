"""Verify actual candidate evidence, same-family states and conservative credit."""
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
    previous=BASE/'research-20261103-funerary-045'
    for e in get(previous/'RECEIPT.json')['files']:
        p=previous/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    screen=get(OUT/'functional-prefilter.json');src=get(OUT/'sources.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json');context=get(OUT/'author-context.json');review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json')
    check(screen['fixed_metadata']);check(screen['fixed_archive_inventory'])
    for e in screen['prior_indices']:check(e)
    assert len(screen['entries'])==screen['screened_templates']==1131 and sum(e['candidate_signal'] for e in screen['entries'])==screen['signal_candidates']==3
    assert all(not e['actual_whole_visual_study'] and not e['semantic_use_confirmed'] and e['building_credit']==0 for e in screen['entries'])
    signals={e['member']:e for e in screen['entries'] if e['candidate_signal']}
    assert set(signals)=={c['member'] for c in src['candidates']} and src['automatic_credit']==screen['building_credit_added']==0
    states={}
    for archive in src['source_archives']:assert sha(Path(archive['path']).read_bytes())==archive['sha256']
    for c,a,h,ctx in zip(src['candidates'],audit['entries'],dedup['entries'],context['entries']):
        assert c['source_archive_sha256']==signals[c['member']]['source_archive_sha256'] and c['nbt_sha256']==signals[c['member']]['nbt_sha256']
        with ZipFile(c['source_archive']) as z:
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==a['nbt_sha256']==h['nbt_sha256'];n=read(raw)
            assert n['size']==c['size']==a['size'];pal=n['palette'];ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']};states[c['id']]=ss
            cs={q:s for q,s in ss.items() if s['Name'] not in AIR}
            assert len(ss)==len(n['blocks']) and all(0<=q[i]<c['size'][i] for q in ss for i in range(3))
            assert Counter(s['Name'] for s in cs.values())==c['materials']==a['materials'] and len(cs)==c['nonair']
            assert a['occupied_bounds']==[[min(q[i] for q in cs),max(q[i] for q in cs)] for i in range(3)]
            assert ctx['stored_positions']==len(ss) and ctx['omitted_positions']==0 and ctx['explicit_air']==sum(s['Name']=='minecraft:air' for s in ss.values())
            assert ctx['entities']==n['entities'] and ctx['block_entities']==[b for b in n['blocks'] if b.get('nbt')]
            assert ctx['brewing_stand_states']==[dict(position=list(q),state=s) for q,s in ss.items() if s['Name']=='minecraft:brewing_stand'] and len(ctx['brewing_stand_states'])==1
            assert sha(z.read('META-INF/mods.toml'))==ctx['manifest_sha256'] and z.read('META-INF/mods.toml').decode()==ctx['manifest_text']
            for e in ctx['whole_village_context_resources']:assert sha(z.read(e['member']))==e['sha256'] and json.loads(z.read(e['member']))==e['data']
            for e in ctx['exact_outgoing_pool_resolution']:assert e['present']==(e['exact_member'] in z.namelist())
            assert h['occupancy_sha256']==geometry_hash({q:1 for q in cs},c['size']) and h['role_sha256']==geometry_hash({q:role(s['Name']) for q,s in cs.items()},c['size'])
            assert h['historical_exact_matches']==[]
            for r in c['pool_references']:
                assert json.loads(z.read(r['member']))==r['data']
                ns=c['member'].split('/')[1];ident=ns+':'+c['member'].split('/structures/',1)[1][:-4]
                assert any(e['element'].get('location')==ident for e in r['data']['elements'])
    changed=[dict(position=list(p),left=states['F01'].get(p),right=states['F02'].get(p)) for p in sorted(states['F01'].keys()|states['F02'].keys()) if states['F01'].get(p)!=states['F02'].get(p)]
    assert changed==context['skul_skull_comparison']['changes'] and len(changed)==context['skul_skull_comparison']['changed_raw_states']==1
    assert changed[0]['position']==[3,5,23] and changed[0]['left']['Name']=='minecraft:air' and changed[0]['right']=={'Name':'minecraft:bone_block','Properties':{'axis':'z'}}
    assert src['candidates'][0]['pool_references']==[] and len(src['candidates'][1]['pool_references'])==len(src['candidates'][2]['pool_references'])==1
    assert [len(c['sockets']) for c in src['candidates']]==[1,1,2]
    missing=context['entries'][2]['exact_outgoing_pool_resolution'];assert len(missing)==1 and missing[0]['pool']=='minecraft:village/mushroom/villagers' and not missing[0]['present']
    assert dedup['historical_unique_local_archive_member_pairs']==239 and dedup['within_batch_exact_duplicate_pairs']==[] and dedup['formal_identity_records_checked']==150
    for e in get(OUT/'discovery-boundary.json')['indices_checked']:check(e)
    images=[]
    assert len(review['entries'])==3 and review['architectural_families_observed']==2
    assert review['entries'][0]['family']==review['entries'][1]['family']!=review['entries'][2]['family']
    for r in review['entries']:
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'} and r['formal_credit_added']==r['proposed_credit']==0
        assert not r['independent_human_review'] and not r['native_generation_or_collision_verified']
        for k in ('source_evidence','author_evidence'):check(r[k])
        images.extend(r['actual_images_viewed'])
    assert len(images)==len({e['path'] for e in images})==review['actual_new_images_viewed']==6
    for e in images:
        check(e)
        with Image.open(e['path']) as im:im.verify()
    check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']));assert scope['guard']==prior['guard'] and scope['funerary']==prior['funerary']
    check(scope['funerary']['baseline']);check(scope['funerary']['coordinator_acceptance'])
    formal=get(Path(scope['funerary']['baseline']['path']));assert len(formal['entries'])==scope['funerary']['formal_baseline']==150 and scope['funerary']['remaining_formal']==850
    assert scope['guard']['reference_036_F01_formal_credit']==0 and not scope['funerary']['production_allowed'] and not scope['pending_proposal_identities']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_THREE_ROLE_CANDIDATES_TWO_FAMILIES_HOLD0',date='2026-11-03',batch=46,
        functional_prefilter_templates=1131,functional_prefilter_reference_credit=0,signal_templates=3,
        actual_source_templates_visually_studied=3,actual_new_images_viewed=6,architectural_families_observed=2,
        original_tent_pair_changed_states=1,missing_exact_minecraft_villager_pool_retained=True,
        new_first_scope_proposals=0,formal_credit_added=0,funerary_formal_count=150,remaining_formal=850,
        previous_045_receipted_files_unchanged=True,previous_integrity_receipt_bound_not_reexecuted=evidence(previous/'verification.json'),
        reference_036_F01_formal_credit=0,old_D010_hold0_retained=True,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=46,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
