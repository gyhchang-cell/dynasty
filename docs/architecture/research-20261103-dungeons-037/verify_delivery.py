"""Verify two raw body templates, padding distinction and unchanged layout credit."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR

def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def check(e):assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']

def main():
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:check(e)
    preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/'research-20261103-dungeons-036']
    for folder in preserved:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    audit=get(OUT/'component-boundary-audit.json');check(audit['metadata']);check(audit['archive'])
    metadata=get(Path(audit['metadata']['path']))
    md={(r['source_archive'],r['member']):r for r in metadata['entries']}
    maps=[];occupied=[]
    with ZipFile(audit['archive']['path']) as z:
        raw=z.read('META-INF/mods.toml')
        assert sha(raw)==audit['manifest_sha256'] and raw.decode()==audit['manifest_text']
        for e in audit['pool_resources']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'] and json.loads(raw)==e['data']
        for r in audit['entries']:
            raw=z.read(r['member'])
            assert sha(raw)==r['nbt_sha256']==md[(r['source_archive'],r['member'])]['nbt_sha256']
            d=read(raw);assert d['size']==r['size']==[37,32,25]
            pal=d.get('palette') or d['palettes'][0]
            states={tuple(b['pos']):pal[b['state']] for b in d['blocks']}
            assert len(states)==len(d['blocks'])==r['stored_positions']
            cs={p:s for p,s in states.items() if s['Name'] not in AIR}
            assert len(cs)==r['nonair_positions']
            assert r['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
            sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if pal[b['state']]['Name']=='minecraft:jigsaw']
            assert sockets==r['sockets']
            external=[s for s in sockets if s['data']['pool'] not in ('betterfortresses:mobs','minecraft:empty')]
            assert external==r['non_actor_non_empty_interfaces'] and len(external)==8
            assert Counter(s['data']['pool'] for s in sockets)['betterfortresses:mobs']==11
            assert not r['actual_visual_reading'] and not r['complete_building_identity_confirmed'] and r['building_credit']==0
            maps.append(states);occupied.append(set(cs))
    assert audit['entries'][0]['sockets']==audit['entries'][1]['sockets']
    changes=[dict(position=list(p),before=maps[0].get(p),after=maps[1].get(p)) for p in sorted(set(maps[0])|set(maps[1])) if maps[0].get(p)!=maps[1].get(p)]
    is_padding=lambda r:r['before'] is None and r['after']['Name'] in AIR
    actual=[r for r in changes if not is_padding(r)]
    comp=audit['comparison']
    assert len(changes)==comp['state_changes']==5100
    assert sum(is_padding(r) for r in changes)==comp['omitted_to_explicit_air']==4925
    assert actual==comp['original_states_for_non_air_padding_changes'] and len(actual)==comp['other_state_changes']==175
    assert comp['occupied_positions_added']==[list(p) for p in sorted(occupied[1]-occupied[0])]
    assert comp['occupied_positions_removed']==[list(p) for p in sorted(occupied[0]-occupied[1])]
    assert comp['all_jigsaw_positions_states_and_data_identical']
    assert not audit['components_assembled'] and not audit['java_run'] and not audit['game_run'] and audit['network_requests']==0
    assert audit['actual_images_viewed']==audit['new_visually_studied_source_templates']==audit['new_valid_scoped_references']==0
    scope=get(OUT/'scoped-reference-update.json');check(scope['prior_update'])
    prior=get(Path(scope['prior_update']['path']))
    assert scope['scopes']==prior['scopes'] and [s['accepted_references'] for s in scope['scopes']]==[9,10,1]
    assert scope['previous_batch_scope_observations_retained']==prior['current_scope_observations']
    assert scope['current_scope_observations']==scope['added_ids']==[] and scope['added_credit']==scope['new_source_discoveries']==0
    changed={'prior_update','added_ids','added_credit','new_source_discoveries','current_scope_observations','limits'}
    assert all(scope[k]==v for k,v in prior.items() if k not in changed)
    assert len(scope['current_batch_boundary_holds'])==2
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(OUT.glob('*.png')) and not (OUT/'sources.json').exists()
    result=dict(status='PASS_TWO_KEEP_VARIANTS_BOUNDARY_PRECHECK_ZERO_CREDIT',date='2026-11-03',batch=37,
      raw_templates_prechecked=2,actual_images_viewed=0,new_valid_scoped_references=0,
      state_changes=5100,omitted_to_explicit_air=4925,other_state_changes=175,
      scoped_counts=[9,10,1],remaining=[991,990,999],prior_receipt_packages_unchanged=len(preserved),
      complete_design_boundary_unresolved=True,all_old_holds_and_scope_observations_retained=True,
      construction_allowed=False,java_run=False,game_run=False,network_requests=0,
      production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('verification.json',result)
    session=get(OUT/'session.json');session.update(status=result['status'],verification=evidence(OUT/'verification.json'))
    dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=37,
      session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scoped-reference-update.json'),
      boundary=evidence(OUT/'component-boundary-audit.json'),shared_coordinator_session_not_overwritten=True,
      main_checklist_edits=0,duration_hours_claimed=0,complete_production_task=False,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=result['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
