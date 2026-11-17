"""Verify one held-family proposal, original states and unchanged formal baselines."""
import ast
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def main():
    v=module('helpers036',BASE/'research-20261103-dungeons-036/verify_delivery.py')
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:v.check(e)
    old=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in range(36,41)]+[BASE/'research-20261103-funerary-041']
    for folder in old:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json');review=get(OUT/'manual-review.json');family=get(OUT/'author-and-family-evidence.json')
    assert src['automatic_credit']==0 and src['new_source_templates']==2 and src['previous_source_template_rereads']==1
    assert len(src['candidates'])==2 and len(review['entries'])==2
    assert dedup['historical_unique_local_archive_member_pairs']==233 and not dedup['within_batch_exact_duplicate_pairs']
    archive=src['source_archives'][0];assert sha(Path(archive['path']).read_bytes())==archive['sha256']
    states={}
    with ZipFile(archive['path']) as z:
        for b in family['bodies']:
            raw=z.read(b['member']);assert sha(raw)==b['nbt_sha256'];d=v.read(raw);assert d['size']==b['size']==[37,48,37]
            pal=d.get('palette') or d['palettes'][0];ss={tuple(x['pos']):pal[x['state']] for x in d['blocks']};states[b['member'].rsplit('/',1)[1][:-4]]=ss
            assert len(ss)==len(d['blocks']) and all(0<=p[i]<d['size'][i] for p in ss for i in range(3))
            cs={p:s for p,s in ss.items() if s['Name'] not in v.AIR}
            assert b['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]==[[0,36],[0,46],[0,36]]
            assert b['jigsaw_count']==b['lower_door_count']==0 and not any(s['Name']=='minecraft:jigsaw' or s['Name'].endswith('_door') for s in ss.values())
            assert b['black_wool_cells']==sum(s['Name']=='minecraft:black_wool' for s in cs.values())==3934
            assert b['top_centre_states']==[dict(pos=[18,y,18],state=ss.get((18,y,18))) for y in range(40,48)]
            assert ss[(18,45,18)]['Name']=='minecraft:barrel' and ss[(18,46,18)]['Name']=='goety:crypt_tiles_slab'
            assert b['block_entity_counts']==Counter(x['nbt'].get('id') for x in d['blocks'] if x.get('nbt'))
        for c,a,h in zip(src['candidates'],audit['entries'],dedup['entries']):
            ss=states[c['member'].rsplit('/',1)[1][:-4]];cs={p:s for p,s in ss.items() if s['Name'] not in v.AIR}
            assert len(cs)==c['nonair'] and Counter(s['Name'] for s in cs.values())==c['materials']==a['materials']
            assert not c['sockets'] and not c['doors'] and not c['entities'] and a['outgoing_pools']==[]
            for r in c['pool_references']:
                assert json.loads(z.read(r['member']))==r['data'] and r['member'].endswith('/the_mausoleum/start_pool.json')
                assert any(e['element'].get('location')=='goetyawaken:'+c['member'].rsplit('/',1)[1][:-4] for e in r['data']['elements'])
            assert len(c['pool_references'])==1
            for r in a['archive_json_identity_mentions']:assert sha(z.read(r['member']))==r['sha256'] and json.loads(z.read(r['member']))==r['data']
            assert h['occupancy_sha256']==v.geometry_hash({p:1 for p in cs},c['size']) and h['role_sha256']==v.geometry_hash({p:v.role(s['Name']) for p,s in cs.items()},c['size']) and not h['historical_exact_matches']
        for e in family['author_resources']:assert sha(z.read(e['member']))==e['sha256'] and json.loads(z.read(e['member']))==e['data']
        manifest=z.read('META-INF/mods.toml');assert sha(manifest)==family['manifest_sha256'] and manifest.decode()==family['manifest_text']
    for pair in family['pairs']:
        a,b=states[pair['left']],states[pair['right']]
        changes=[dict(position=list(p),left=a.get(p),right=b.get(p)) for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
        assert pair['changes']==changes and pair['changed_raw_states']==len(changes)
        names=set(pair['original_core_names']);ca={p:s for p,s in a.items() if s['Name'] in names};cb={p:s for p,s in b.items() if s['Name'] in names}
        assert ca==cb and len(ca)==pair['original_core_cells']==30022 and pair['original_core_states_identical']
    assert [p['changed_raw_states'] for p in family['pairs']]==[2,1811,1809]
    p=family['pairs'][2];assert next(e['count'] for e in p['changed_state_pairs'] if e['left']=='OMITTED' and e['right']=='minecraft:air')==1721
    for k in ['old_candidate_index','old_review']:v.check(family[k])
    old_candidate=next(c for c in get(Path(family['old_candidate_index']['path']))['candidates'] if c['id']=='W028')
    assert old_candidate['nbt_sha256']==family['bodies'][0]['nbt_sha256'] and family['old_hold_reason']==get(Path(family['old_review']['path']))['not_credited']['W028']
    assert family['old_family_not_newly_discovered'] and not family['native_entry_digging_route_verified'] and family['wool_not_hidden_or_replaced']
    resources={e['member']:e['data'] for e in family['author_resources']}
    root=resources['data/goetyawaken/worldgen/structure/the_mausoleum.json'];pool=resources['data/goetyawaken/worldgen/template_pool/the_mausoleum/start_pool.json']
    assert root['start_pool']=='goetyawaken:the_mausoleum/start_pool' and root['terrain_adaptation']=='bury' and root['step']=='underground_structures'
    assert [e['element']['location'] for e in pool['elements']]==family['direct_author_start_alternatives']
    assert [e['weight'] for e in pool['elements']]==[1,1]
    book=resources['assets/goety/patchouli_books/black_book/zh_cn/entries/world/strctures/the_mausoleum.json']
    assert book['name']=='陵墓' and '陪葬品' in book['pages'][0]['text']
    processor=resources['data/goetyawaken/worldgen/processor_list/the_mausoleum_loot.json']
    assert all(r['output_state']['Name']!='minecraft:jigsaw' for p in processor['processors'] for r in p.get('rules',[]))
    actual=[]
    for r in review['entries']:
        v.check(r['source_evidence']);assert r['formal_credit_added']==0 and r['complete_author_template_body_confirmed'] and not r['native_entry_or_routes_verified'] and not r['independent_human_review']
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        for e in r['actual_images_viewed']:v.check(e,True);actual.append(e['path'])
    for e in review['old_comparison_images']:v.check(e,True);actual.append(e['path'])
    assert len(actual)==len(set(actual))==review['actual_images_viewed']==6
    assert sum(r['proposed_credit'] for r in review['entries'])==review['proposed_first_scope_admissions']==1 and review['formal_credit_added']==0
    assert review['entries'][0]['proposal_identity']=='COD4-R001-W028' and not review['entries'][0]['newly_discovered_design']
    scope=get(OUT/'scope-status.json');v.check(scope['prior_scope_status']);prior=get(Path(scope['prior_scope_status']['path']))
    assert scope['guard']==prior['guard'] and scope['guard']['reference_036_F01_formal_credit']==0
    fun=scope['funerary'];v.check(fun['baseline']);formal=get(Path(fun['baseline']['path']))
    assert len(formal['entries'])==fun['formal_baseline']==148 and all(e['id']!='COD4-R001-W028' for e in formal['entries'])
    assert fun['formal_credit_added']==0 and fun['batch_proposed_credit']==1 and fun['coordinator_acceptance_pending'] and not fun['formal_register_written']
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:v.check(e)
    assert discovery['local_only'] and discovery['network_requests']==0 and not discovery['java_run'] and not discovery['game_run']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_W028_WHOLE_FAMILY_PROPOSAL_WITH_ENTRY_LIMIT_RETAINED',date='2026-11-03',batch=42,
        new_source_templates=2,old_source_template_rereads=1,actual_new_images_viewed=5,old_comparison_images_viewed=1,
        old_identity_first_scope_proposals=1,newly_discovered_designs=0,formal_credit_added=0,funerary_formal_baseline=148,remaining_formal=852,
        original_core_cells_identical=30022,three_templates_one_family=True,native_entry_or_routes_verified=False,
        prior_receipt_packages_unchanged=len(old),reference_036_F01_formal_credit=0,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=42,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
