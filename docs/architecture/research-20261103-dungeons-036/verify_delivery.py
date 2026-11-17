"""Verify original castle bytes, room/height evidence and scope continuity offline."""
import ast
from collections import Counter,defaultdict
import hashlib
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

def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def check(e,image=False):
    p=Path(e['path']);assert sha(p.read_bytes())==e['sha256'],p
    if image:
        with Image.open(p) as im:im.verify()

def main():
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:check(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');assert src['new_source_templates']==1 and src['automatic_credit']==src['previous_source_template_rereads']==0
    assert len(src['candidates'])==len(src['source_archives'])==1
    for a in src['source_archives']:assert sha(Path(a['path']).read_bytes())==a['sha256']
    c=src['candidates'][0];a=get(OUT/'raw-source-audit.json')['entries'][0]
    h=get(OUT/'dedup-evidence.json')['entries'][0];room=get(OUT/'room-height-placement-evidence.json')
    assert c['id']==a['id']==h['id']==room['id']=='F01'
    with ZipFile(c['source_archive']) as z:
        raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==room['nbt_sha256']
        d=read(raw);assert d['size']==c['size']==[27,40,31]
        pal=d.get('palette') or d['palettes'][0]
        states={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
        assert len(states)==len(d['blocks']) and all(0<=p[i]<d['size'][i] for p in states for i in range(3))
        cs={p:s for p,s in states.items() if s['Name'] not in AIR}
        assert len(cs)==c['nonair'] and Counter(v['Name'] for v in cs.values())==c['materials']
        assert c['doors']==[dict(position=list(p),state=s) for p,s in states.items() if s['Name'].endswith('_door') and s.get('Properties',{}).get('half')=='lower']
        assert len(c['doors'])==9
        assert c['entities']==[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]==[]
        assert c['sockets']==[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
        assert Counter(s['data']['pool'] for s in c['sockets'])=={'terralith:village/fortified/roads':4,'minecraft:village/plains/villagers':4}
        for e in c['pool_references']:assert json.loads(z.read(e['member']))==e['data']
        for e in a['archive_json_identity_mentions']+room['author_structure_resources']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        for e in a['outgoing_pools']:
            assert not e['assembled'] and e['building_credit']==0
            if e['status']=='FOUND_LOCAL':
                raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
            else:assert e['pool']=='minecraft:village/plains/villagers' and e['status']=='NOT_PRESENT_IN_FIXED_SOURCE_ARCHIVE'
        manifest=z.read('META-INF/mods.toml')
        assert sha(manifest)==room['manifest_sha256'] and manifest.decode()==room['manifest_text']
    bounds=[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
    assert bounds==a['occupied_bounds']==[[0,26],[0,30],[0,30]]
    assert h['occupancy_sha256']==geometry_hash({p:1 for p in cs},c['size'])
    assert h['role_sha256']==geometry_hash({p:role(s['Name']) for p,s in cs.items()},c['size'])
    de=get(OUT/'dedup-evidence.json')
    assert de['historical_unique_local_archive_member_pairs']==225 and not h['historical_exact_matches'] and not de['within_batch_exact_duplicate_pairs']
    details=get(OUT/'detail-evidence.json')['entries'][0]
    assert [r['coordinate'] for r in details['cuts']]==[3,12,13,15]
    ladders=defaultdict(list)
    for p,s in cs.items():
        if s['Name']=='minecraft:ladder':ladders[(p[0],p[2])].append(p[1])
    assert details['ladder_runs']==[dict(x=22,z=4,ys=list(range(8,15)))]
    assert details['ladder_runs']==[dict(x=x,z=z,ys=sorted(ys)) for (x,z),ys in ladders.items()]
    assert [r['coordinate'] for r in room['cuts']]==[5,9,22,4]
    for plane in room['original_horizontal_planes']:
        assert {tuple(r['position']):r['state'] for r in plane['original_states']}=={p:s for p,s in states.items() if p[1]==plane['y']}
    for r in room['upper_occupied_profile']:
        layer={p:s for p,s in cs.items() if p[1]==r['y']}
        assert len(layer)==r['nonair'] and Counter(s['Name'] for s in layer.values())==r['materials']
        assert r['horizontal_bounds']==[[min(p[i] for p in layer),max(p[i] for p in layer)] for i in (0,2)]
    assert cs[(5,30,5)]['Name']=='minecraft:red_banner'
    assert all(sum(p[1]==y for p in cs)==1 for y in range(26,31))
    root=room['author_structure_resources'][0]['data']
    assert root['start_pool']=='terralith:village/fortified/starts' and root['step']=='surface_structures'
    pool=c['pool_references'][0]['data']
    assert any(e['element'].get('location')=='terralith:village/fortified/start_castle' for e in pool['elements'])
    review=get(OUT/'manual-review.json');r=review['entries'][0]
    assert review['independent_references_added']==r['credit']==1 and r['credit_identity']=='036-F01'
    assert not review['independent_human_review_claimed'] and not r['independent_human_review'] and not r['native_acceptance']
    assert r['source']==c and set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    imgs=[]
    for e in r['actual_images_viewed']+r['actual_comparison_images_viewed']:check(e,True);imgs.append(e['path'])
    assert len(set(imgs))==5 and len(r['actual_images_viewed'])==3 and len(r['actual_comparison_images_viewed'])==2
    assert r['height_basis']['occupied_height_including_banner']==31 and r['height_basis']['stored_height']==40
    assert r['height_basis']['scope_definition_unchanged']
    scope=get(OUT/'scoped-reference-update.json')
    for k in ('prior_update','original_scope_definitions','previous_hold_evidence','height_basis_question_retained'):check(scope[k])
    prior=get(Path(scope['prior_update']['path']))
    assert scope['added_ids']==['036-F01'] and scope['added_credit']==1
    assert scope['scopes'][0]['accepted_ids']==prior['scopes'][0]['accepted_ids']+['036-F01']
    assert scope['scopes'][0]['scope_definition']==prior['scopes'][0]['scope_definition']
    assert scope['scopes'][1:]==prior['scopes'][1:]
    assert [s['accepted_references'] for s in scope['scopes']]==[9,10,1]
    assert [s['remaining'] for s in scope['scopes']]==[991,990,999]
    assert not any(s['construction_allowed'] for s in scope['scopes'])
    for k in ('previous_two_holds_retained','other_holds_retained','recent_holds_retained','prior_58_block_assembly_exclusion_retained','prior_other_exclusions_retained','prior_additional_holds_retained','prior_ice_holds_retained','prior_review_exclusions_retained','prior_034_exclusions_retained'):
        assert scope[k]==prior[k]
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:check(e)
    assert discovery['local_only'] and not discovery['java_run'] and not discovery['game_run']
    assert discovery['network_requests']==discovery['production_changes']==discovery['checklist_deletions']==discovery['sound_brightness_window_save_changes']==discovery['prior_033_035_images_reopened']==0
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_ONE_COMPLETE_CASTLE_LAYOUT_OBSERVATION',batch=36,date='2026-11-03',
      new_source_templates=1,new_images_viewed=3,prior_comparison_images_viewed=2,new_scoped_layout_observations=1,
      scoped_counts=[9,10,1],remaining=[991,990,999],prior_receipt_packages_unchanged=len(preserved),
      saved40_occupied31_banner_tip_explicit=True,scope_definitions_unchanged=True,
      semantic_novelty_not_machine_certified=True,independent_human_review_claimed=False,
      all_prior_holds_and_exclusions_retained=True,construction_allowed=False,
      native_collision_routes_terrain_or_gameplay_acceptance=False,java_run=False,game_run=False,
      network_requests=0,production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'),next='继续尚未实看的本地相关完整建筑；本批新增一例待主协调按证据合并，未达1000不制作。')
    dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=36,
      session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),
      scope=evidence(OUT/'scoped-reference-update.json'),review=evidence(OUT/'manual-review.json'),
      shared_coordinator_session_not_overwritten=True,main_checklist_edits=0,duration_hours_claimed=0,
      complete_production_task=False,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
