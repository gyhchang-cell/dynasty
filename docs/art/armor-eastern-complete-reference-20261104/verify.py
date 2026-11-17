"""D21 exact local source/provenance checks; no game/art execution or mutations."""
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
    prior=read(R/ctx['prior_ledger'])
    assert (len(prior['groups']),len(prior['case_to_group']),len(prior['reviewed_case_keys']))==(207,565,579)
    for a in prior['source_reviews']:assert sha(R/a['path'])==a['sha256']
    baseline=read(D/'source-baseline.json');assert len(baseline)==289
    changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
    receipt=read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets'])==len(set(receipt['targets']))==24
    assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    p=read(D/'provenance.json');decls=read(D/'resource-declarations.json');review=read(D/'semantic-review.json')
    stat=read(D/'static-declarations.json');geo=read(D/'geometry-animation-context.json');cl=read(D/'class-provenance.json');lang=read(D/'language-provenance.json')
    cases={a['case_key'] for a in p['cases']};icons=[i for c in p['cases'] for i in c['icons']];worn=p['worn_textures']
    assert len(cases)==12 and cases==set(ctx['selected_case_keys']) and not cases&set(prior['reviewed_case_keys'])
    assert len(icons)==len(decls)==48 and len(worn)==len(stat)==len(cl['classes'])==12 and len(geo)==24
    assert not read(D/'animation-candidates.json')
    assert len(review['pages_opened'])==8 and all((D/f).is_file() for f in review['pages_opened'])
    assert sha(Path(cl['javap']))==cl['javap_sha256']
    with ExitStack() as st:
        jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']}
        for a in p['archives']:assert sha(Path(a['path']))==a['sha256']
        for a in icons+worn+[x['model'] for x in decls]+geo+cl['classes']+[lang]:
            assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
            if 'size' in a:
                with Image.open(D/a['local']) as im:assert list(im.size)==a['size']
        labels=read(D/lang['local'])
        for a in icons:assert a['entry']+'.mcmeta' not in jars[a['jar']].namelist()
        for a in decls:
            m=read(D/a['model']['local']);assert m['parent']==a['parent'] and m['textures']['layer0']==a['texture_location']
            ns,t=a['texture_location'].split(':');assert a['texture']['entry']==f'assets/{ns}/textures/{t}.png'
            assert a['texture'] in next(c['icons'] for c in p['cases'] if c['case_key']==a['case_key'])
            assert a['label']==labels[f"item.{ns}.{a['case_key'].split(':')[1]}_{a['part']}"]
        for k in cases:assert {a['part'] for a in decls if a['case_key']==k}=={'helmet','chestplate','leggings','boots'}
        for a in cl['classes']:assert sha(D/a['disassembly'])==a['disassembly_sha256']
        facts=[]
        for a in stat:
            k=a['case_key'];clsource=a['class_source'];assert clsource in cl['classes']
            dis=(D/clsource['disassembly']).read_text();assert a['method_excerpt'] in dis
            ns,t=a['declared_texture'].split(':');assert f'// String {ns}' in a['method_excerpt'] and f'// String {t}' in a['method_excerpt']
            assert a['archive_entry']==f'assets/{ns}/{t}' and not a['runtime_selected_chain_proven']
            tex=next(x for x in worn if x['case_key']==k);assert tex['entry']==a['archive_entry'] and not tex['binding_proven']
            g=next(x for x in geo if x['case_key']==k and x['kind']=='GEOMETRY_ATLAS_CONTEXT')
            ani=next(x for x in geo if x['case_key']==k and x['kind']=='DECLARED_ANIMATION_CONTEXT')
            # Prove declarations occur in the saved class; do not infer an equipped player's selected chain.
            for c in [g,ani]:assert '// String '+c['entry'].split(f'assets/{ns}/')[1] in dis
            payload=read(D/g['local']);des=[v['description'] for v in payload['minecraft:geometry']];assert des==g['descriptions']
            Image.open(D/tex['local']).verify();im=Image.open(D/tex['local']).convert('RGBA');hist=im.getchannel('A').histogram()
            ratios=[{'uv_width':v['texture_width'],'uv_height':v['texture_height'],'png_width':im.width,'png_height':im.height,'x_ratio':im.width/v['texture_width'],'y_ratio':im.height/v['texture_height']} for v in des]
            # Every source uses a 2x physical PNG/declared UV grid, a source fact, not a rendering defect.
            assert all(v['x_ratio']==v['y_ratio']==2 for v in ratios)
            read(D/ani['local'])
            facts.append({'case_key':k,'source':tex,'declared_geometry':g,'declared_animation':ani,'atlas_uv_ratios':ratios,'alpha_nonzero':sum(hist[1:]),'alpha_extrema':list(im.getchannel('A').getextrema()),'runtime_selected_chain_proven':False,'standard_64x32_uv_assumed':False})
    save('native-layer-facts.json',{'layers':facts,'static_declarations_checked':12,'all_png_to_declared_uv_grid_scale':2,'interpretation':'源PNG边长均为geo声明UV网格的2倍，记录等比例高分辨率采样；不据此判断出错，不缩小/重写源图。专用GeoModel图集不能按普通盔甲UV裁切。','worn_binding_proven':False,'pixels_modified':False,'design_credit_from_layers':0})
    flat=[c for row in review['observations'] for c in row['cases']]
    assert len(flat)==len(set(flat))==12 and set(flat)==cases and not review['excluded_cases']
    groups={g['semantic_group']:g for g in prior['groups']}
    for row in review['observations']:
        k=row['semantic_group'];assert row['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group']==k and k in groups
        groups[k]['cases']=sorted(set(groups[k]['cases'])|set(row['cases']))
        groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':row['observation']})
    owners={}
    for k,g in groups.items():
        for c in g['cases']:assert c not in owners;owners[c]=k
    reviewed=sorted(set(owners)|{e['case_key'] for e in prior['excluded_cases']})
    assert (len(review['observations']),len(groups),len(owners),len(reviewed))==(8,207,577,591)
    save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':591,'armor_name_families':577,'conservative_learning_groups':207})
    save('reference-gate-accounting.json',{'required_valid_related_independent_designs':1000,'reviewed_name_families':591,'armor_name_families_after_exclusion':577,'excluded_from_full_armor_gate':14,'conservative_learning_groups_in_current_subset':207,'validated_independent_design_total':None,'maximum_credit_under_current_one_per_group_policy':207,'unfilled_minimum_under_current_policy':793,'reference_gate_met':False,'gap_limit':'207组含变体、局部和反例，不是207个已验完整独立设计；793仅是每组都合格时的最低缺口。中式四件名称本批零新增信用。'})
    assert all(review[k]==0 for k in ['new_artwork','production_changes','game_starts','new_conservative_learning_groups']) and not review['gate_met']
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'archive_sources':len(p['archives']),'new_complete_name_families_viewed':12,'native_icon_entries_viewed':48,'distinct_icon_payloads':len({a['sha256'] for a in icons}),'model_json_declarations_checked':48,'native_atlas_entries_viewed':12,'static_texture_declarations_checked':12,'exact_class_payloads':12,'geo_animation_context_payloads':24,'all_png_to_declared_uv_grid_scale':2,'final_worn_binding_proven':False,'new_learning_groups':0,'append_observations':8,'combined_learning_groups':207,'combined_reviewed_names':591,'combined_armor_names':577,'validated_independent_design_total':None,'reference_gate_met':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_scripts':{f:sha(D/f) for f in ['collect.py','record_review.py','verify.py']}}
    save('verification.json',result);print(json.dumps(result,ensure_ascii=False));assert not changed
if __name__=='__main__':main()
