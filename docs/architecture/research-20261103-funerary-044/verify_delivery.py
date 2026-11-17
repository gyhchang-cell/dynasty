"""Source/evidence integrity and scope checks; offline Python only."""
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def check(e):assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']
def main():
    import sys
    sys.path.insert(0,str(ROOT/'tools/architecture'))
    from nbt_read import read
    from whole_building_candidates import AIR
    from reference_components import geometry_hash,role
    old=[BASE/'research-20261101-proposal-semantic-acceptance-010-015']+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in range(36,41)]+[BASE/f'research-20261103-funerary-{n:03d}' for n in (41,42,43)]
    for folder in old:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json');author=get(OUT/'author-context.json');detail=get(OUT/'detail-evidence.json');review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json')
    assert src['automatic_credit']==0 and len(src['candidates'])==len(author['entries'])==2
    inventory_path=BASE/'research-20261101-dungeons-024/fixed-source-screen.json'
    inventory={e['path']:e['sha256'] for e in get(inventory_path)['archives']}
    context_by_id={e['id']:e for e in author['entries']};states={}
    for c,a,h,d in zip(src['candidates'],audit['entries'],dedup['entries'],detail['entries']):
        assert sha(Path(c['source_archive']).read_bytes())==c['source_archive_sha256']==inventory[c['source_archive']]
        with ZipFile(c['source_archive']) as z:
            raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==a['nbt_sha256']==h['nbt_sha256'];n=read(raw);assert n['size']==c['size']==a['size']
            pal=n['palette'];ss={tuple(b['pos']):pal[b['state']] for b in n['blocks']};states[c['id']]=ss
            cs={p:s for p,s in ss.items() if s['Name'] not in AIR}
            assert len(ss)==len(n['blocks']) and all(0<=p[i]<c['size'][i] for p in ss for i in range(3))
            assert Counter(s['Name'] for s in cs.values())==c['materials']==a['materials'] and len(cs)==c['nonair']
            assert a['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
            assert c['doors']==c['sockets']==a['sockets']==a['outgoing_pools']==[]
            assert h['role_sha256']==geometry_hash({p:role(s['Name']) for p,s in cs.items()},c['size']) and h['occupancy_sha256']==geometry_hash({p:1 for p in cs},c['size'])
            assert not h['historical_exact_matches']
            ctx=context_by_id[c['id']];assert sha(z.read('META-INF/mods.toml'))==ctx['manifest_sha256'] and z.read('META-INF/mods.toml').decode()==ctx['manifest_text']
            assert ctx['entities']==n['entities'] and ctx['block_entities']==[b for b in n['blocks'] if b.get('nbt')] and ctx['jigsaw_count']==0
            for r in ctx['resources']:
                assert sha(z.read(r['member']))==r['sha256'];data=json.loads(z.read(r['member']))
                if 'data' in r:assert data==r['data']
                else:assert r['selected_entries']=={k:v for k,v in data.items() if 'decayed_totem' in k}
            assert d['stored_positions']==len(ss) and d['omitted_positions']==c['size'][0]*c['size'][1]*c['size'][2]-len(ss)
            assert d['explicit_air']==sum(s['Name']=='minecraft:air' for s in ss.values())
            assert d['candle_states']==[dict(position=list(p),state=s) for p,s in ss.items() if s['Name']=='minecraft:candle']
            for r in c['pool_references']:
                assert r['data']==json.loads(z.read(r['member'])) and len(r['data']['elements'])==1
                element=r['data']['elements'][0]['element'];ident=c['member'].split('/')[1]+':'+c['member'].split('/structures/',1)[1][:-4]
                assert element['location']==ident
    assert detail['entries'][0]['stored_positions']==265 and detail['entries'][0]['omitted_positions']==635 and detail['entries'][0]['explicit_air']==0
    assert states['F01'][(7,0,7)]['Name']=='minecraft:chest' and states['F01'][(7,1,7)]['Name']=='minecraft:budding_amethyst' and states['F01'][(7,2,7)]['Name']=='minecraft:amethyst_cluster'
    candles=detail['entries'][0]['candle_states'];assert len(candles)==8 and all(e['state']['Properties']['lit']=='true' for e in candles)
    resources={ctx['id']:{r['member']:r.get('data',r.get('selected_entries')) for r in ctx['resources']} for ctx in author['entries']}
    ritual_root=resources['F01']['data/trek/worldgen/structure/overworld/medium/ritual.json']
    assert ritual_root['start_pool']=='trek:overworld/medium/ritual' and ritual_root['project_start_to_heightmap']=='WORLD_SURFACE_WG'
    assert src['candidates'][0]['pool_references'][0]['data']['elements'][0]['element']['processors']=='minecraft:empty'
    f02=src['candidates'][1];ignored=f02['pool_references'][0]['data']['elements'][0]['element']['processors']['processors'][0]
    assert ignored['processor_type']=='minecraft:block_ignore' and {e['Name'] for e in ignored['blocks']}=={'minecraft:air','minecraft:sandstone','minecraft:structure_block'}
    assert len(detail['entries'][1]['sandstone_positions'])==110 and detail['entries'][1]['omitted_positions']==0
    monster=context_by_id['F02']['entities'][0];assert monster['nbt']['id']=='radiation_zone_reborn:decayed_totem' and monster['nbt']['Health']==180 and monster['pos']==[6.5,4.0,6.5]
    assert resources['F02']['assets/radiation_zone_reborn/lang/zh_cn.json']['advancements.kill_decayed_totem.descr']=='杀死一个腐衰图腾'
    assert dedup['historical_unique_local_archive_member_pairs']==235 and not dedup['within_batch_exact_duplicate_pairs'] and dedup['formal_identity_records_checked']==149 and dedup['formal_count_annotation_corrected_from_legacy_helper']
    # Verify the recorded discovery inputs, including exclusion of old members.
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:check(e)
    assert discovery['selected_members']==[c['member'] for c in src['candidates']] and discovery['local_only'] and discovery['network_requests']==0
    imgs=[]
    for r in review['entries']:
        for key in ('source_evidence','author_evidence'):check(r[key])
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        assert r['formal_credit_added']==0 and not r['independent_human_review'] and not r['native_generation_or_collision_verified']
        imgs.extend(r['actual_images_viewed'])
    imgs.extend(review['old_comparison_images'])
    assert len(imgs)==len({e['path'] for e in imgs})==review['actual_images_viewed']==6
    for e in imgs:
        check(e)
        with Image.open(e['path']) as im:im.verify()
    assert [r['proposed_credit'] for r in review['entries']]==[1,0] and review['proposed_first_scope_admissions']==1
    check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']))
    assert scope['guard']==prior['guard'] and scope['guard']['reference_036_F01_formal_credit']==0
    fun=scope['funerary'];check(fun['baseline']);check(fun['coordinator_acceptance'])
    formal=get(Path(fun['baseline']['path']));assert len(formal['entries'])==fun['formal_baseline']==149 and fun['remaining_formal']==851
    assert all(e['id']!='COD4-R044-F01' for e in formal['entries']) and scope['pending_proposal_identities']==['COD4-R044-F01']
    assert not fun['production_allowed'] and fun['formal_credit_added']==0 and not fun['formal_register_written']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_ONE_SMALL_OPEN_AIR_RITUAL_PROPOSAL_ONE_HOLD',date='2026-11-03',batch=44,
        source_templates_read=2,actual_new_images_viewed=4,actual_old_comparison_images_viewed=2,
        new_first_scope_proposals=1,proposal_identity='COD4-R044-F01',coordinator_acceptance_pending=True,
        formal_credit_added=0,funerary_formal_count=149,remaining_formal=851,prior_receipt_packages_unchanged=len(old),
        old_D010_hold0=True,reference_036_F01_formal_credit=0,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=44,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
