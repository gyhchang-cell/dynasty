"""Verify fixed D24 static evidence. No model execution, game, build or art mutation."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
import json,hashlib,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    c=read(D/'context.json')
    for k in ['capture','prior_progress','prior_ledger','prior_provenance','prior_declarations','prior_language']:
        assert sha(R/c[k])==c[k+'_sha256'],k
    prior=read(R/c['prior_progress']);ledger=read(R/c['prior_ledger'])
    assert (len(ledger['reviewed_case_keys']),len(ledger['case_to_group']),len(ledger['groups']))==(618,604,211)
    assert not prior['reference_gate_met']
    a=read(D/'class-provenance.json');base=read(D/'additional-class-provenance.json');factory=read(D/'factory-provenance.json')
    assert sha(D/'capture_base.py')==base['capture_base_sha256']
    assert sha(D/'capture_factory.py')==factory['capture_factory_sha256']
    classes=a['classes']+[base['class']]+factory['classes'];assert len(classes)==len({x['entry'] for x in classes})==27
    assert len(base['vanilla_sources'])==3
    archives=[a['archive'],base['vanilla_archive']]
    with ExitStack() as stack:
        jars={x['path']:stack.enter_context(zipfile.ZipFile(x['path'])) for x in archives}
        for x in archives:assert sha(Path(x['path']))==x['sha256']
        for x in classes+base['vanilla_sources']:
            assert sha(D/x['local'])==x['sha256']==hashlib.sha256(jars[x['jar']].read(x['entry'])).hexdigest()
            if 'disassembly' in x:assert sha(D/x['disassembly'])==x['disassembly_sha256']
        p=read(R/c['prior_provenance']);P=(R/c['prior_provenance']).parent
        decls=read(R/c['prior_declarations']);b=read(D/'binding-study.json');u=read(D/'uv-call-study.json')
        assert b['all_family_slot_chains']==len(b['slot_chains'])==40
        assert len({x['item_id'] for x in b['slot_chains']})==40
        for x in b['slot_chains']:
            assert x['provider_key']==x['item_id'].split(':')[1]
            assert x['item_model']['entry'].endswith(x['provider_key']+'.json')
            for source in [x['item_model'],x['item_icon'],x['normal_texture']]+([x['slim_texture_if_selected']] if x['slim_texture_if_selected'] else []):
                assert sha(P/source['local'])==source['sha256']==hashlib.sha256(jars[source['jar']].read(source['entry'])).hexdigest()
            im=read(P/x['item_model']['local']);assert im['textures']['layer0']=='armoroftheages:item/'+x['provider_key']
        for n,h in b['source_sha256'].items():assert sha(D/'disassembly'/f'{n}.class.txt')==h
        sr=[x for x in b['slot_chains'] if x['geometry_source_read']]
        assert len(sr)==12 and {x['family'] for x in sr}==set(c['selected_complete_families'])
        assert all(bool(x['slim_texture_if_selected'])==(x['slot']=='CHEST') for x in sr)
        assert (u['slot_classes'],u['methods_read'],len(u['models']),u['raw_addbox_calls'],u['out_of_grid_uv_rectangles'])==(12,15,15,149,6)
        for x in u['models']:
            row=next(z for z in sr if z['family']==x['family'] and z['slot']==x['slot'].upper())
            texture=row['slim_texture_if_selected'] if 'Slim' in x['method'] else row['normal_texture']
            assert x['texture_source']==texture
            assert list(Image.open(P/texture['local']).size)==x['declared_grid']
            assert len(x['source_addbox_calls'])==x['source_addbox_call_count']
            assert not x['all_final_model_geometry_or_runtime_visibility_proven']
        flags=[(x,z) for x in u['models'] for z in x['out_of_grid_uv_rectangles']]
        zero=[(x,z) for x,z in flags if z['rect'][0]==z['rect'][2]]
        thin=[(x,z) for x,z in flags if z['rect'][0]!=z['rect'][2]]
        assert len(zero)==4 and all(x['family']=='centurion_armor' and z['offset'] in [204,228] for x,z in zero)
        assert len(thin)==2 and all(x['family']=='japanese_light_armor' and z['offset']==168 for x,z in thin)
    review=read(D/'manual-review.json');assert {x['family'] for x in review['observations']}==set(c['selected_complete_families'])
    assert all(x['independent_credit_delta']==0 and x['slots']==4 for x in review['observations'])
    for x in review['pages_actually_reopened']:assert sha(R/x['path'])==x['sha256']
    assert len(review['pages_actually_reopened'])==4
    assert review['dedup_decision']['new_independent_design_credit']==0 and not review['reference_gate_met']
    receipt=read(next(D.glob('texture-requirements-receipt-*.json')))
    assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    assert len(receipt['targets'])==len(set(receipt['targets']))==24
    baseline=read(D/'source-baseline.json');assert len(baseline)==289
    changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
    gate={'required_valid_related_independent_designs':1000,'reviewed_name_families':618,'armor_name_families':604,'conservative_learning_groups':211,
          'excluded_cases':14,'validated_independent_design_total':None,'minimum_open_gap_under_current_policy':789,'reference_gate_met':False,
          'note':'完整静态对应加深不新增设计信用；211组包括变体/局部/反例，789仅是每组都合格时的最小缺口。'}
    save('reference-gate-accounting.json',gate)
    files=['capture.py','capture_base.py','capture_factory.py','read_uv_calls.py','read_binding.py','record_review.py','verify.py','context.json','class-provenance.json','additional-class-provenance.json','factory-provenance.json','uv-call-study.json','binding-study.json','manual-review.json','source-baseline.json','reference-gate-accounting.json']
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_STATIC_CORRESPONDENCE_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED',
            'source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'foreign_classes_fixed':27,'vanilla_uv_sources':3,
            'static_slot_chains':40,'selected_complete_set_geometry_uv_correspondences':3,'selected_slots':12,'geometry_methods_read':15,
            'raw_uv_flags':6,'confirmed_live_defects':0,'new_names':0,'new_learning_groups':0,'new_independent_design_credit':0,
            'cumulative':gate,'runtime_acceptance':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,
            'evidence_sha256':{f:sha(D/f) for f in files}}
    save('verification.json',result);print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},ensure_ascii=False));assert not changed
if __name__=='__main__':main()
