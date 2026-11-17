"""Verify D22 exact archive copies, conservative semantic credit and protected assets."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
import hashlib,json,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    ctx=read(D/'collection-context.json')
    for k in ['collector','prior_ledger','candidate_inventory','icon_chart_collector']:assert sha(R/ctx[k])==ctx[k+'_sha256'],k
    prior=read(R/ctx['prior_ledger']);assert (len(prior['groups']),len(prior['case_to_group']),len(prior['reviewed_case_keys']))==(207,577,591)
    for a in prior['source_reviews']:assert sha(R/a['path'])==a['sha256']
    baseline=read(D/'source-baseline.json');assert len(baseline)==289
    changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
    receipt=read(next(D.glob('texture-requirements-receipt-*.json')));assert len(receipt['targets'])==len(set(receipt['targets']))==24
    assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    p=read(D/'provenance.json');decls=read(D/'resource-declarations.json');review=read(D/'semantic-review.json');stat=read(D/'static-declarations.json');cl=read(D/'class-provenance.json');missing=read(D/'unresolved-source-candidates.json')
    cases={a['case_key'] for a in p['cases']};icons=[i for c in p['cases'] for i in c['icons']];worn=p['worn_textures']
    assert len(cases)==17 and cases==set(ctx['selected_case_keys']) and not cases&set(prior['reviewed_case_keys'])
    assert len(icons)==len(decls)==68 and len(worn)==len(stat)==len(cl['classes'])==17 and not read(D/'animation-candidates.json')
    assert len(review['pages_opened'])==9 and all((D/f).is_file() for f in review['pages_opened'])
    assert sha(Path(cl['javap']))==cl['javap_sha256']
    with ExitStack() as st:
        jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']+[missing['archive']]}
        for a in p['archives']+[missing['archive']]:assert sha(Path(a['path']))==a['sha256']
        for a in icons+worn+[x['model'] for x in decls]+cl['classes']+missing['models']:
            assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
            if 'size' in a:
                with Image.open(D/a['local']) as im:assert list(im.size)==a['size']
        for a in icons:assert a['entry']+'.mcmeta' not in jars[a['jar']].namelist()
        for a in decls:
            m=read(D/a['model']['local']);assert m['parent']==a['parent'] and m['textures']['layer0']==a['texture_location']
            ns,t=a['texture_location'].split(':');assert a['texture']['entry']==f'assets/{ns}/textures/{t}.png'
            assert a['texture'] in next(c['icons'] for c in p['cases'] if c['case_key']==a['case_key'])
        for k in cases:assert {a['part'] for a in decls if a['case_key']==k}=={'helmet','chestplate','leggings','boots'}
        for a in cl['classes']:assert sha(D/a['disassembly'])==a['disassembly_sha256']
        for a in stat:
            cs=a['class_source'];assert cs in cl['classes']
            dis=(D/cs['disassembly']).read_text();method=dis.split('getArmorTexture(net.minecraft.world.item.ItemStack, net.minecraft.world.entity.Entity, net.minecraft.world.entity.EquipmentSlot, java.lang.String);',1)[1].split('\n  public ',1)[0]
            assert '// String '+a['declared_texture'] in method and 'areturn' in method
            ns,t=a['declared_texture'].split(':');assert a['archive_entry']==f'assets/{ns}/{t}' and not a['full_player_four_slot_chain_proven']
            tex=next(x for x in worn if x['case_key']==a['case_key']);assert tex['entry']==a['archive_entry'] and not tex['binding_proven']
        assert len(missing['models'])==12 and len({x['case_key'] for x in missing['models']})==3 and missing['reviewed_reference_credit']==0
        for a in missing['models']:
            assert read(D/a['local'])['textures']['layer0']==a['texture_location']
            assert 'assets/'+a['texture_location'].replace(':','/textures/')+'.png'==a['missing_in_this_archive_only']
            assert a['missing_in_this_archive_only'] not in jars[a['jar']].namelist()
    facts=[]
    for a in worn:
        im=Image.open(D/a['local']).convert('RGBA');h=im.getchannel('A').histogram();facts.append({'case_key':a['case_key'],'source':a,'alpha_nonzero':sum(h[1:]),'alpha_extrema':list(im.getchannel('A').getextrema()),'standard_64x32_uv_assumed':False,'all_slots_binding_proven':False})
    save('native-layer-facts.json',{'layers':facts,'static_helmet_declarations_checked':17,'worn_binding_proven':False,'pixels_modified':False,'design_credit_from_layers':0,'warning':'头盔直接返回的图集源文件，不等于四槽整套渲染与普通玩家UV已验。'})
    flat=[c for row in review['observations'] for c in row['cases']];assert len(flat)==len(set(flat))==17 and set(flat)==cases and not review['excluded_cases']
    groups={g['semantic_group']:g for g in prior['groups']};new=append=0
    for row in review['observations']:
        k=row['semantic_group']
        if row['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP':assert k not in groups;groups[k]={'semantic_group':k,'cases':[],'observations':[]};new+=1
        else:assert row['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group']==k and k in groups;append+=1
        groups[k]['cases']=sorted(set(groups[k]['cases'])|set(row['cases']));groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':row['observation']})
    owners={}
    for k,g in groups.items():
        for c in g['cases']:assert c not in owners;owners[c]=k
    reviewed=sorted(set(owners)|{e['case_key'] for e in prior['excluded_cases']});assert (new,append,len(groups),len(owners),len(reviewed))==(1,2,208,594,608)
    save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':608,'armor_name_families':594,'conservative_learning_groups':208})
    save('reference-gate-accounting.json',{'required_valid_related_independent_designs':1000,'reviewed_name_families':608,'armor_name_families_after_exclusion':594,'excluded_from_full_armor_gate':14,'conservative_learning_groups_in_current_subset':208,'validated_independent_design_total':None,'maximum_credit_under_current_one_per_group_policy':208,'unfilled_minimum_under_current_policy':792,'reference_gate_met':False,'gap_limit':'208组含变体、局部和反例，不是208个已验完整独立设计；792仅是每组都合格时的最低缺口。两个八环境系列不按16套计数。'})
    assert all(review[k]==0 for k in ['new_artwork','production_changes','game_starts']) and not review['gate_met']
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'archive_sources':len(p['archives']),'new_complete_name_families_viewed':17,'native_icon_entries_viewed':68,'distinct_icon_payloads':len({a['sha256'] for a in icons}),'model_json_declarations_checked':68,'native_atlas_entries_viewed':17,'static_helmet_texture_declarations_checked':17,'exact_class_payloads':17,'unresolved_models_zero_credit':12,'unresolved_names_zero_credit':3,'final_worn_binding_proven':False,'new_learning_groups':1,'append_observations':2,'combined_learning_groups':208,'combined_reviewed_names':608,'combined_armor_names':594,'validated_independent_design_total':None,'reference_gate_met':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_scripts':{f:sha(D/f) for f in ['collect.py','record_review.py','verify.py']}}
    save('verification.json',result);print(json.dumps(result,ensure_ascii=False));assert not changed
if __name__=='__main__':main()
