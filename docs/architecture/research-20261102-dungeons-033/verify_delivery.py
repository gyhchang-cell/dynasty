"""Offline integrity verification; semantic exclusions remain recorded observations."""
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(OUT.parents[2] / 'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash, role
from whole_building_candidates import AIR

def sha(b):
    return hashlib.sha256(b).hexdigest()

def get(p):
    return json.loads(p.read_text())

def dump(n, v):
    (OUT / n).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')

def evidence(e, image=False):
    p = Path(e['path'])
    assert sha(p.read_bytes()) == e['sha256'], p
    if image:
        with Image.open(p) as im:
            im.verify()

def main():
    original = BASE / 'research-20261101-proposal-semantic-acceptance-010-015'
    definitions = get(original / 'scoped-reference-register.json')
    for e in definitions['preserved_registries']:
        evidence(e)
    preserved = [original] + [BASE / f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]
    for folder in preserved:
        for e in get(folder / 'RECEIPT.json')['files']:
            p = folder / e['path']
            assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256'], p
    src = get(OUT / 'sources.json')
    assert src['new_source_templates'] == 4 and src['automatic_credit'] == src['previous_source_template_rereads'] == 0
    assert len(src['candidates']) == 4
    for a in src['source_archives']:
        assert sha(Path(a['path']).read_bytes()) == a['sha256']
    de = get(OUT / 'dedup-evidence.json')
    assert de['historical_unique_local_archive_member_pairs'] == 217 and not de['within_batch_exact_duplicate_pairs']
    occupied = {}
    for c, a, h, r in zip(src['candidates'], get(OUT/'raw-source-audit.json')['entries'], de['entries'], get(OUT/'role-evidence.json')['entries']):
        assert c['id'] == a['id'] == h['id'] == r['id']
        with ZipFile(c['source_archive']) as z:
            raw = z.read(c['member'])
            assert sha(raw) == c['nbt_sha256'] == r['nbt_sha256']
            d = read(raw)
            assert d['size'] == c['size']
            pal = d.get('palette') or d['palettes'][0]
            states = {tuple(b['pos']):pal[b['state']] for b in d['blocks']}
            assert len(states) == len(d['blocks'])
            assert all(0<=p[i]<d['size'][i] for p in states for i in range(3))
            cs = {p:v for p,v in states.items() if v['Name'] not in AIR}
            assert len(cs) == c['nonair'] and Counter(v['Name'] for v in cs.values()) == c['materials']
            assert c['entities'] == [dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]
            assert c['doors'] == [dict(position=list(p),state=v) for p,v in states.items() if v['Name'].endswith('_door') and v.get('Properties',{}).get('half')=='lower']
            assert c['sockets'] == [dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
            assert r['entity_id_counts'] == Counter(e.get('nbt',{}).get('id','') for e in d.get('entities',[]))
            assert r['entity_summary'] == [dict(position=e.get('pos'),block_position=e.get('blockPos'),id=e.get('nbt',{}).get('id'),custom_name=e.get('nbt',{}).get('CustomName'),is_baby=e.get('nbt',{}).get('IsBaby')) for e in d.get('entities',[])]
            assert sha(z.read('META-INF/mods.toml')) == r['archive_manifest_sha256']
            for e in c['pool_references']:
                assert json.loads(z.read(e['member'])) == e['data']
            for e in a['archive_json_identity_mentions']+r['author_resources']:
                raw = z.read(e['member'])
                assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
            for e in a['outgoing_pools']:
                assert not e['assembled'] and e['building_credit']==0
                if e['status']=='FOUND_LOCAL':
                    raw = z.read(e['member'])
                    assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
            for e in r['author_images']:
                assert z.read(e['member']) == Path(e['path']).read_bytes()
                evidence(e, True)
                assert e['original_author_reference'] and not e['newly_created_texture']
        assert a['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
        assert h['occupancy_sha256']==geometry_hash({p:1 for p in cs},c['size'])
        assert h['role_sha256']==geometry_hash({p:role(v['Name']) for p,v in cs.items()},c['size'])
        assert not h['historical_exact_matches']
        occupied[c['id']]=cs
    cuts = {'F01':[3,14,12,10], 'F02':[3,14,12,11], 'F03':[15,25,13,9], 'F04':[3,10,16,16]}
    for r in get(OUT/'detail-evidence.json')['entries']:
        assert [e['coordinate'] for e in r['cuts']]==cuts[r['id']]
        ladders = defaultdict(list)
        for p,v in occupied[r['id']].items():
            if v['Name']=='minecraft:ladder':
                ladders[(p[0],p[2])].append(p[1])
        assert sorted(r['ladder_runs'],key=lambda v:(v['x'],v['z']))==[dict(x=x,z=z,ys=sorted(ys)) for (x,z),ys in sorted(ladders.items())]
    tree = src['candidates'][2]
    assert len(tree['sockets'])==4 and {s['data']['pool'] for s in tree['sockets']}=={'trek:mobs/villagers/jungle/unemployed'}
    resources = get(OUT/'role-evidence.json')['entries'][3]['author_resources']
    chinese = next(e['data'] for e in resources if '/zh_cn/' in e['member'])
    assert chinese['name']=='兔子棚屋' and '养了很多兔子' in chinese['pages'][0]['text']
    review = get(OUT/'manual-review.json')
    assert review['independent_references_added']==0 and review['new_source_templates']==4
    assert review['actual_unique_images_viewed']==9 and not review['independent_human_review_claimed']
    imgs = set()
    for r,c in zip(review['entries'],src['candidates']):
        assert r['source']==c and r['credit']==0 and r['credit_identity'] is None
        assert not r['native_acceptance'] and not r['independent_human_review']
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        for e in r['actual_images_viewed']:
            evidence(e,True)
            imgs.add(e['path'])
    assert len(imgs)==9
    scope = get(OUT/'scoped-reference-update.json')
    for k in ('prior_update','original_scope_definitions','previous_hold_evidence','height_basis_question_retained'):
        evidence(scope[k])
    prior = get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and not scope['added_ids'] and scope['added_credit']==0
    assert [s['accepted_references'] for s in scope['scopes']]==[8,10,1]
    for k in ('previous_two_holds_retained','other_holds_retained','recent_holds_retained','prior_58_block_assembly_exclusion_retained','prior_other_exclusions_retained','prior_additional_holds_retained'):
        assert scope[k]==prior[k]
    assert scope['prior_ice_holds_retained']==prior['current_batch_holds']
    assert not scope['current_batch_holds'] and len(scope['current_batch_exclusions'])==4
    boundary = get(OUT/'discovery-boundary.json')
    for e in boundary['indices_checked']:
        evidence(e)
    assert all(Path(p).is_file() for p in de['historical_indices_checked'])
    assert boundary['local_only'] and not boundary['java_run'] and not boundary['game_run'] and boundary['network_requests']==0
    assert boundary['production_changes']==boundary['checklist_deletions']==boundary['sound_brightness_window_save_changes']==0
    for p in OUT.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    report = dict(status='PASS_FOUR_NEW_TEMPLATES_EXCLUDED_FROM_CURRENT_GUARD_SCOPES', batch=33,
        new_source_templates=4, actual_images_viewed=9, new_valid_scoped_references=0,
        scoped_counts=[8,10,1],remaining=[992,990,999],
        prior_receipt_packages_unchanged=len(preserved),author_role_and_source_bytes_verified=True,
        all_old_holds_and_height_basis_question_retained=True,construction_allowed=False,
        independent_human_review_claimed=False,native_collision_terrain_or_gameplay_acceptance=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
        sound_brightness_window_save_changes=0)
    dump('verification.json',report)
    files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path']
        assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))

if __name__ == '__main__':
    main()
