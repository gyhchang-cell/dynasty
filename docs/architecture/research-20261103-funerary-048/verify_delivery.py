"""Verify fixed original evidence and one pending proposal, offline Python only."""
import ast
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
sys.path.insert(0,str(BASE.parents[1]/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def check(e):assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    previous=BASE/'research-20261103-funerary-047'
    for e in get(previous/'RECEIPT.json')['files']:
        p=previous/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');ctx=get(OUT/'author-context.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json')
    review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json');boundary=get(OUT/'source-boundary.json')
    for e in boundary['previous_gap_analysis']:check(e)
    assert not boundary['source_exhaustion_claimed'] and not boundary['all_local_suitable_sources_proven_insufficient']
    assert boundary['fixed_inventory_archives']==292 and boundary['existing_metadata_templates']==7139
    assert len(src['source_archives'])==1
    a=src['source_archives'][0];assert sha(Path(a['path']).read_bytes())==a['sha256']=='384db435d7e448e6f0a67390ae6113e3d60895ed007961f947e989daf4ba2612'
    fixed=get(BASE/'research-20261101-dungeons-024/fixed-source-screen.json')['archives']
    assert any(e['path']==a['path'] and e['sha256']==a['sha256'] for e in fixed)
    assert len(src['candidates'])==len(ctx['entries'])==len(audit['entries'])==len(dedup['entries'])==4
    m=module('altar048',OUT/'inspect_altar.py');states={}
    with ZipFile(a['path']) as z:
        for c,e,r,h in zip(src['candidates'],ctx['entries'],audit['entries'],dedup['entries']):
            assert c['id']==e['id']==r['id']==h['id']
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==r['nbt_sha256']==h['nbt_sha256'];n=read(raw)
            assert n['size']==c['size']==r['size']==[8,6,8]
            assert e['original_blocks']==n['blocks'] and e['palette']==n['palette'] and e['entities']==n['entities']==[]
            ss={tuple(b['pos']):n['palette'][b['state']] for b in n['blocks']};states[c['id']]=m.normalize(ss)
            assert len(ss)==len(n['blocks'])==e['stored_positions']==c['nonair']==38
            assert e['explicit_air']==0 and e['omitted_positions']==346
            assert all(0<=p[i]<8 if i!=1 else 0<=p[i]<6 for p in ss for i in range(3))
            assert Counter(s['Name'] for s in ss.values())==c['materials']==r['materials']=={'minecraft:oak_log':18,'minecraft:red_wool':20}
            assert all(s['Properties']=={'axis':'y'} for s in ss.values() if s['Name']=='minecraft:oak_log')
            assert r['occupied_bounds']==[[0,7],[0,5],[0,7]]
            assert c['sockets']==r['sockets']==r['outgoing_pools']==[] and c['pool_references']==[]
            assert h['occupancy_sha256']==geometry_hash({p:1 for p in ss},c['size'])
            assert h['role_sha256']==geometry_hash({p:role(s['Name']) for p,s in ss.items()},c['size']) and h['historical_exact_matches']==[]
        for r in ctx['resources']:
            raw=z.read(r['member']);assert sha(raw)==r['sha256']
            assert (json.loads(raw) if r['member'].endswith('.json') else raw.decode())==r.get('data',r.get('text'))
        lang=ctx['chinese_language'];raw=z.read(lang['member']);assert sha(raw)==lang['sha256'];all_strings=json.loads(raw)
        assert all(all_strings[k]==v for k,v in lang['selected_strings'].items())
        assert len(lang['selected_strings'])==7 and '六个橡木柱子' in all_strings['patchouli.touhou_little_maid.book.entries.overview.multiblocks_altar.pages.3.text']
        image=ctx['original_author_image'];assert sha(z.read(image['member']))==image['sha256']==sha((OUT/image['local_file']).read_bytes())
        assert image['unaltered'] and image['research_only']
        classes=get(OUT/'class-evidence.json');check(classes['decoder']);reader=module('reader043',Path(classes['decoder']['path']))
        assert len(classes['classes'])==3 and sum(len(c['class_data']['methods']) for c in classes['classes'])==16
        for c in classes['classes']:
            raw=z.read(c['member']);assert sha(raw)==c['sha256'];data,resolve=reader.parse(raw)
            for method in data['methods']:
                if 'code_hex' in method:method['instructions']=reader.decode(bytes.fromhex(method['code_hex']),resolve)
            assert json.loads(json.dumps(data))==c['class_data']
        cl=classes['classes'][0]['class_data'];methods={r['name']:r for r in cl['methods']}
        refs=[i['reference'] for i in methods['<clinit>']['instructions']]
        assert all('altar_'+s in refs for s in ('north','east','south','west'))
        assert sum('getAltarTemplate' in (i['reference'] or '') for i in methods['getTemplate']['instructions'])==4
        registry=classes['classes'][2]['class_data'];init=next(r for r in registry['methods'] if r['name']=='init')
        assert any('anyMatcher' in (i['reference'] or '') for i in init['instructions'])
    for row in ctx['rotation_comparison']:
        cur=states['F01'];matches=[]
        for q in range(4):
            if cur==states[row['id']]:matches.append(q)
            cur=m.rotate(cur)
        assert matches==row['matching_quarter_turns_from_F01'] and matches and not row['non_rotation_changes_required']
    assert [r['matching_quarter_turns_from_F01'] for r in ctx['rotation_comparison']]==[[0],[1],[2],[3]]
    assert dedup['within_batch_exact_duplicate_pairs']==[list(p) for p in itertools.combinations(states,2)]
    assert dedup['historical_unique_local_archive_member_pairs']==245 and dedup['formal_identity_records_checked']==150
    for e in get(OUT/'discovery-boundary.json')['indices_checked']:check(e)
    assert len(review['entries'])==1 and review['distinct_authored_designs_observed']==1 and review['actual_original_templates_visually_studied']==4
    entry=review['entries'][0];assert entry['proposal_identity']=='COD4-R048-F01' and entry['proposed_credit']==1 and entry['formal_credit_added']==0
    assert entry['coordinator_acceptance_pending'] and not entry['independent_human_review'] and not entry['native_generation_or_collision_verified']
    assert set(entry['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    check(entry['source_evidence']);check(entry['author_evidence'])
    assert len(entry['actual_images_viewed'])==review['actual_new_images_viewed']==6 and len(review['actual_old_comparison_images_viewed'])==2
    for e in entry['actual_images_viewed']+review['actual_old_comparison_images_viewed']:
        check(e)
        with Image.open(e['path']) as im:im.verify()
    for k in ('source','text'):check(review['original_bytecode_reading'][k])
    check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']))
    assert scope['guard']==prior['guard'] and scope['funerary']==prior['funerary']
    check(scope['funerary']['baseline']);check(scope['funerary']['coordinator_acceptance'])
    assert len(get(Path(scope['funerary']['baseline']['path']))['entries'])==scope['funerary']['formal_baseline']==150 and scope['funerary']['remaining_formal']==850
    assert scope['current_batch_proposed_credit']==1 and scope['current_batch_formal_credit_added']==0 and scope['pending_proposal_identities']==['COD4-R048-F01']
    assert scope['guard']['reference_036_F01_formal_credit']==0 and not scope['funerary']['production_allowed']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_ONE_AUTHORED_ALTAR_FOUR_ROTATIONS_PENDING_SCOPE_ADMISSION',date='2026-11-03',batch=48,
        actual_original_templates_visually_studied=4,distinct_authored_designs_observed=1,
        actual_new_images_viewed=6,actual_old_comparison_images_viewed=2,
        original_class_files_decoded=3,original_methods_decoded=16,
        four_orientations_exact_original_states_rotations=True,author_image_and_chinese_use_preserved=True,
        new_first_scope_proposals=1,pending_identity='COD4-R048-F01',coordinator_scope_admission_pending=True,
        formal_credit_added=0,funerary_formal_count=150,remaining_formal=850,source_exhaustion_claimed=False,
        previous_047_receipted_files_unchanged=True,earlier_integrity_bound_not_reexecuted=evidence(previous/'verification.json'),
        reference_036_F01_formal_credit=0,old_D010_hold0_retained=True,
        semantic_or_native_review_not_replaced_by_hashes=True,production_allowed=False,
        java_run=False,classes_loaded=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=48,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),boundary=evidence(OUT/'source-boundary.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
