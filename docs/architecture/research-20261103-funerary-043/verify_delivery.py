"""Audit fixed inputs, old holds and evidence bindings; never run Java/game."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def check(e):assert sha(Path(e['path']).read_bytes())==e['sha256'],e['path']
def main():
    spec=importlib.util.spec_from_file_location('read_class043',OUT/'read_class.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    import sys
    sys.path.insert(0,str(ROOT/'tools/architecture'))
    from nbt_read import read
    from PIL import Image
    old=[BASE/'research-20261101-proposal-semantic-acceptance-010-015']+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in range(36,41)]+[BASE/f'research-20261103-funerary-{n:03d}' for n in (41,42)]
    for folder in old:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'recipe-source.json');primary=get(OUT/'class-evidence.json');layout=get(OUT/'layout-evidence.json');review=get(OUT/'manual-review.json');scope=get(OUT/'scope-status.json')
    jar=Path(src['source_archive']);assert sha(jar.read_bytes())==src['source_archive_sha256']==primary['source_archive_sha256']=='0bdc89263616d1b35c32ef82c5e9c14cbd20368e2fe8b468c72a28320be7a778'
    with ZipFile(jar) as z:
        for e in [dict(member=primary['member'],sha256=primary['class_sha256'],data=primary['class_data'])]+src['classes']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256']
            data,resolve=m.parse(raw)
            assert data['major']==61
            for method,recorded in zip(data['methods'],e['data']['methods']):
                assert method['name']==recorded['name'] and method.get('code_hex')==recorded.get('code_hex')
                if 'instructions' in recorded:
                    code=bytes.fromhex(method['code_hex']);assert sha(code)==recorded['code_sha256']
                    offsets={i['pc'] for i in recorded['instructions']}
                    assert all(t in offsets for i in recorded['instructions'] for t in i['branch_targets'])
                    # Direct byte checks for the signed constants that affect geometry.
                    for i in recorded['instructions']:
                        if i['opcode'] in (16,17):
                            width={16:1,17:2}[i['opcode']]
                            assert i['operands']==[int.from_bytes(code[i['pc']+1:i['pc']+1+width],'big',signed=True)]
        for e in src['templates']:
            raw=z.read(e['member']);assert sha(raw)==e['sha256'];n=read(raw)
            assert n['size']==e['size'] and n['palette']==e['palette'] and len(n['blocks'])==e['blocks']
        for member,e in src['primary_metadata'].items():assert sha(z.read(member))==e['sha256'] and z.read(member).decode()==e['text']
    method=next(x for x in primary['class_data']['methods'] if x['name']=='m_142674_')
    bypc={e['pc']:e for e in method['instructions']}
    assert len(bypc)==605 and bypc[228]['operands']==[-8] and bypc[897]['operands']==[-2]
    assert bypc[951]['reference'].endswith('StructureTemplate.m_230328_(Lnet/minecraft/world/level/ServerLevelAccessor;Lnet/minecraft/core/BlockPos;Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/levelgen/structure/templatesystem/StructurePlaceSettings;Lnet/minecraft/util/RandomSource;I)Z')
    assert bypc[945]['operands']==[19] # grave placement reuses processor-bearing settings.
    assert layout['raw_fence_count']==66 and layout['raw_fence_is_closed_perimeter'] and layout['raw_template_door_or_gate_count']==0
    assert {tuple(p) for p in layout['grave_origins']}=={(x,-1,z) for x in (3,8,13,18) for z in (2,4,8,10)}
    assert layout['grave_slot_count']==16 and not layout['all_full_random_outcome_or_seed_verified'] and layout['diagram_is_not_native_generated_instance'] and layout['explicit_air_writes_honored']
    for key in ('old_index','old_review','source_recipe','source_class','source_layout'):check(review[key])
    old_hold=get(Path(review['old_review']['path']))['not_credited']['D010'];assert old_hold==review['old_hold_reason']
    old_candidate=next(e for e in get(Path(review['old_index']['path']))['candidates'] if e['id']=='D010')
    assert old_candidate['nbt_sha256']==src['templates'][0]['sha256'] and old_candidate['member']==src['templates'][0]['member']
    assert set(review['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    for e in review['actual_images_viewed']:
        check(e)
        with Image.open(e['path']) as img:img.verify()
    assert len(review['actual_images_viewed'])==2 and not review['independent_human_review'] and review['formal_credit_added']==review['proposed_credit']==0
    check(scope['prior_scope_status']);assert scope['guard']==get(Path(scope['prior_scope_status']['path']))['guard'] and scope['guard']['reference_036_F01_formal_credit']==0
    fun=scope['funerary'];check(fun['baseline']);check(fun['coordinator_acceptance'])
    accepted=get(Path(fun['coordinator_acceptance']['path']));formal=get(Path(fun['baseline']['path']))
    assert fun['coordinator_acceptance']['sha256']=='db8ba566b809e6a6c307a2021c5b5947196076a67b58406d7cc0b8ca491f2975'
    assert accepted['previous_formal_count']==148 and accepted['result_formal_count']==len(formal['entries'])==fun['formal_baseline']==149 and accepted['scope_gap']==fun['remaining_formal']==851
    assert accepted['baseline_before_sha256']=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
    assert sum(e['id']=='COD4-R001-W028' for e in formal['entries'])==1 and all(e['id']!='COD4-R004-D010' for e in formal['entries'])
    assert not fun['formal_register_written'] and not fun['production_allowed'] and not scope['pending_proposal_identities']
    preserved=get(old[0]/'scoped-reference-register.json')['preserved_registries']
    for e in preserved:
        if Path(e['path'])==Path(fun['baseline']['path']):
            assert e['sha256']==accepted['baseline_before_sha256']
        else:check(e)
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_D010_RECIPE_SUPPLEMENT_HOLD0',date='2026-11-03',batch=43,
        actual_images_viewed=2,source_classes_read=3,source_templates_read=5,
        old_identity='COD4-R004-D010',newly_discovered_designs=0,formal_credit_added=0,new_proposals=0,
        authored_layout_slots=16,closed_raw_fence_cells=66,native_whole_instance_verified=False,native_entry_or_routes_verified=False,
        previous_042_coordinator_accepted=True,funerary_formal_count=149,remaining_formal=851,
        prior_receipt_packages_unchanged=len(old),reference_036_F01_formal_credit=0,
        production_allowed=False,java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=43,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT/'RECEIPT.json')['files']:
        p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256']
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
