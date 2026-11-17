"""Offline receipt and original-source checks; semantic decisions remain manual."""
import ast
from collections import Counter
import hashlib
import itertools
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
    previous=BASE/'research-20261103-funerary-046'
    for e in get(previous/'RECEIPT.json')['files']:
        p=previous/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json')
    context=get(OUT/'author-context.json');review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json')
    inventory=BASE/'research-20261101-dungeons-024/fixed-source-screen.json'
    fixed={a['path']:a['sha256'] for a in get(inventory)['archives']}
    assert len(src['candidates'])==len(audit['entries'])==len(dedup['entries'])==len(context['entries'])==3
    assert src['automatic_credit']==dedup['formal_credit_added']==0
    for a in src['source_archives']:assert fixed[a['path']]==a['sha256']==sha(Path(a['path']).read_bytes())
    states={}
    for c,a,h,ctx in zip(src['candidates'],audit['entries'],dedup['entries'],context['entries']):
        assert c['id']==a['id']==h['id']==ctx['id']
        with ZipFile(c['source_archive']) as z:
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==a['nbt_sha256']==h['nbt_sha256'];n=read(raw)
            assert n['size']==c['size']==a['size'];ss={tuple(b['pos']):n['palette'][b['state']] for b in n['blocks']};states[c['id']]=ss
            cs={p:s for p,s in ss.items() if s['Name'] not in AIR}
            assert len(ss)==len(n['blocks'])==ctx['stored_positions']
            assert all(0<=p[i]<c['size'][i] for p in ss for i in range(3))
            assert ctx['omitted_positions']==0 and ctx['explicit_air']==sum(s['Name']=='minecraft:air' for s in ss.values())
            assert Counter(s['Name'] for s in cs.values())==c['materials']==a['materials'] and len(cs)==c['nonair']
            assert a['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
            assert ctx['block_entities']==[b for b in n['blocks'] if b.get('nbt')] and ctx['entities']==n['entities']
            assert len(n['entities'])==1 and n['entities'][0]['nbt']['id']=='minecraft:illusioner'
            assert c['sockets']==a['sockets']==[] and a['outgoing_pools']==[]
            assert h['occupancy_sha256']==geometry_hash({p:1 for p in cs},c['size'])
            assert h['role_sha256']==geometry_hash({p:role(s['Name']) for p,s in cs.items()},c['size'])
            assert h['historical_exact_matches']==[]
            for e in ctx['resources']:
                assert e['present']==(e['member'] in z.namelist())
                if e['present']:assert sha(z.read(e['member']))==e['sha256'] and json.loads(z.read(e['member']))==e['data']
            for e in ctx['manifests']:assert sha(z.read(e['member']))==e['sha256'] and z.read(e['member']).decode()==e['text']
            root,pool,biomes,processor=ctx['resources']
            assert root['data']['start_pool']=='ati_structures:haunted_ruin' and root['data']['size']==7
            assert root['data']['project_start_to_heightmap']=='WORLD_SURFACE_WG' and root['data']['terrain_adaptation']=='beard_thin'
            assert root['data']['spawn_overrides']['monster']['spawns']==[]
            elements=pool['data']['elements'];assert len(elements)==3 and all(e['weight']==2 for e in elements)
            assert all(e['element']['projection']=='rigid' and e['element']['processors']=='minecraft:mossify_20_percent' for e in elements)
            assert not processor['present'] and biomes['present']
            ident='ati_structures:'+c['member'].split('/structures/',1)[1][:-4]
            assert len(c['pool_references'])==1 and sum(e['element'].get('location')==ident for e in elements)==1
            for r in c['pool_references']:assert json.loads(z.read(r['member']))==r['data']==pool['data']
    assert [c['size'] for c in src['candidates']]==[[15,10,15],[15,11,15],[15,10,15]]
    assert [a['occupied_bounds'][1] for a in audit['entries']]==[[0,7],[0,5],[0,7]]
    assert [c['nonair'] for c in src['candidates']]==[535,492,523]
    assert [ctx['explicit_air'] for ctx in context['entries']]==[1715,1983,1727]
    assert [sum(s['Name']=='minecraft:tnt' for s in states[c].values()) for c in states]==[7,3,5]
    candles={p:s for p,s in states['F02'].items() if s['Name']=='minecraft:red_candle'}
    assert set(candles)=={(4,2,6),(5,2,5),(5,2,7),(6,2,4),(6,2,8),(7,2,5),(7,2,7),(8,2,6)}
    assert all(s['Properties']=={'waterlogged':'false','lit':'true','candles':'1'} for s in candles.values())
    assert states['F02'][(6,2,6)]['Name']=='minecraft:trapped_chest'
    assert {p for p,s in states['F02'].items() if s['Name']=='minecraft:tnt'}=={(5,0,6),(6,0,6),(7,0,6)}
    for ctx,pos in zip(context['entries'],([4,2,4],[6,2,6],[5,2,8])):
        boxes=[b for b in ctx['block_entities'] if b['nbt']['id']=='minecraft:trapped_chest']
        assert len(boxes)==1 and boxes[0]['pos']==pos and boxes[0]['nbt']['LootTable']=='minecraft:chests/simple_dungeon'
    changes=[]
    for pair,e in zip(itertools.combinations(states,2),context['pairwise_raw_state_comparisons']):
        a,b=pair;sa,sb=states[a],states[b];union=sa.keys()|sb.keys();common=sa.keys()&sb.keys()
        assert e['pair']==[a,b] and e['left_stored']==len(sa) and e['right_stored']==len(sb) and e['common_positions']==len(common)
        assert e['identical_original_states']==sum(sa[p]==sb[p] for p in common)
        changed=sum(sa.get(p)!=sb.get(p) for p in union);assert e['changed_or_absent_positions']==changed;changes.append(changed)
    assert changes==[589,426,453] and dedup['within_batch_exact_duplicate_pairs']==[]
    assert dedup['historical_unique_local_archive_member_pairs']==242 and dedup['formal_identity_records_checked']==150
    for e in get(OUT/'discovery-boundary.json')['indices_checked']:check(e)
    task=get(OUT/'task-use-boundary.json')
    for e in task['excerpts']:
        check(e['source']);lines=Path(e['source']['path']).read_text().splitlines()
        for row in e['lines']:assert lines[row['line']-1]==row['text']
    images=[]
    for r in review['entries']:
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        assert r['formal_credit_added']==r['proposed_credit']==0 and not r['independent_human_review'] and not r['native_generation_or_collision_verified']
        check(r['source_evidence']);check(r['author_evidence']);images.extend(r['actual_images_viewed'])
    assert len(images)==len({e['path'] for e in images})==review['actual_new_images_viewed']==7
    assert review['semantic_families_newly_confirmed']==0 and not review['semantic_family_identity_resolved']
    assert len(review['actual_old_comparison_images_viewed'])==1;check(review['old_comparison_source'])
    for e in images+review['actual_old_comparison_images_viewed']:
        check(e)
        with Image.open(e['path']) as im:im.verify()
    check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']))
    assert scope['guard']==prior['guard'] and scope['funerary']==prior['funerary'] and scope['guard']['reference_036_F01_formal_credit']==0
    check(scope['funerary']['baseline']);check(scope['funerary']['coordinator_acceptance'])
    assert len(get(Path(scope['funerary']['baseline']['path']))['entries'])==scope['funerary']['formal_baseline']==150
    assert scope['funerary']['remaining_formal']==850 and not scope['funerary']['production_allowed'] and not scope['pending_proposal_identities']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_THREE_HAUNTED_RUIN_ALTERNATIVES_HOLD0',date='2026-11-03',batch=47,
        actual_source_templates_visually_studied=3,actual_new_images_viewed=7,actual_old_comparison_images_viewed=1,
        alternative_set_groups_observed=1,semantic_families_newly_confirmed=0,
        F02_eight_lit_candles_trapped_chest_and_three_TNT_original_coordinates_verified=True,
        new_first_scope_proposals=0,formal_credit_added=0,funerary_formal_count=150,remaining_formal=850,
        previous_046_receipted_files_unchanged=True,earlier_integrity_bound_not_reexecuted=evidence(previous/'verification.json'),
        fixed_archive_inventory=evidence(inventory),reference_036_F01_formal_credit=0,old_D010_hold0_retained=True,
        semantic_or_native_review_not_replaced_by_hashes=True,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=47,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
