"""D23 verify exact archive sources and normal/slim semantic dedup; not in-game QA."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
import hashlib,json,zipfile,re
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    ctx=read(D/'collection-context.json')
    for k in ['collector','prior_ledger','icon_chart_collector']:assert sha(R/ctx[k])==ctx[k+'_sha256'],k
    prior=read(R/ctx['prior_ledger']);assert (len(prior['groups']),len(prior['case_to_group']),len(prior['reviewed_case_keys']))==(208,594,608)
    for a in prior['source_reviews']:assert sha(R/a['path'])==a['sha256']
    baseline=read(D/'source-baseline.json');assert len(baseline)==289
    changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
    receipt=read(next(D.glob('texture-requirements-receipt-*.json')));assert len(receipt['targets'])==len(set(receipt['targets']))==24
    assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    p=read(D/'provenance.json');decls=read(D/'resource-declarations.json');review=read(D/'semantic-review.json');cl=read(D/'class-provenance.json');lang=read(D/'language-provenance.json')
    cases={a['case_key'] for a in p['cases']};icons=[i for c in p['cases'] for i in c['icons']];worn=p['worn_textures']
    assert len(cases)==10 and cases==set(ctx['selected_case_keys']) and not cases&set(prior['reviewed_case_keys'])
    assert len(icons)==len(decls)==40 and len(worn)==20 and len(cl['classes'])==5 and not read(D/'animation-candidates.json')
    assert len(review['pages_opened'])==7 and all((D/f).is_file() for f in review['pages_opened'])
    assert sha(Path(cl['javap']))==cl['javap_sha256']
    with ExitStack() as st:
        jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']}
        for a in p['archives']:assert sha(Path(a['path']))==a['sha256']
        for a in icons+worn+[x['model'] for x in decls]+cl['classes']+[lang]:
            assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
            if 'size' in a:
                with Image.open(D/a['local']) as im:assert list(im.size)==a['size']
        labels=read(D/lang['local'])
        for a in icons:assert a['entry']+'.mcmeta' not in jars[a['jar']].namelist() and a['size']==[16,16]
        for a in decls:
            m=read(D/a['model']['local']);assert m['parent']==a['parent'] and m['textures']['layer0']==a['texture_location']
            ns,t=a['texture_location'].split(':');assert a['texture']['entry']==f'assets/{ns}/textures/{t}.png'
            assert a['texture'] in next(c['icons'] for c in p['cases'] if c['case_key']==a['case_key'])
            assert a['label']==labels.get(f"item.{ns}.{a['case_key'].split(':')[1]}_{a['source_slot']}")
        for k in cases:
            assert {a['part'] for a in decls if a['case_key']==k}=={'helmet','chestplate','leggings','boots'}
            assert {a['variant'] for a in worn if a['case_key']==k}=={'normal','slim'}
        for a in cl['classes']:assert sha(D/a['disassembly'])==a['disassembly_sha256']
    reg=(D/'disassembly/ModelProviderRegistry.class.txt').read_text()
    provider=(D/'disassembly/ArmorModelProvider.class.txt').read_text()
    forge=(D/'disassembly/ForgeHumanoidArmorItem.class.txt').read_text()
    # Static registry names and four slots only. Supplier targets/texture concatenation recipes are not assumed.
    declarations=[]
    for k in sorted(cases):
        name=k.split(':')[1];pattern=re.compile(r'// String '+re.escape(name)+r'\n[^\n]*// Field net/minecraft/world/entity/EquipmentSlot\.(HEAD|CHEST|LEGS|FEET):')
        slots=pattern.findall(reg);assert sorted(slots)==['CHEST','FEET','HEAD','LEGS']
        declarations.append({'case_key':k,'provider_registry_slots':slots,'name_and_slot_declaration_checked':True,'final_runtime_selected_chain_proven':False})
    assert '// String slim' in provider and 'getTexture(net.minecraft.world.entity.Entity)' in provider
    assert 'ArmorModelProvider.getTexture:' in forge and 'aconst_null' in forge
    save('static-context-study.json',{'registry_declarations':declarations,'source_classes':cl['classes'],'observation':'10系列名在ModelProviderRegistry各声明HEAD/CHEST/LEGS/FEET；Forge物品有provider时调用getTexture，无provider时返回null。isSlim还受偏好/同步配置影响，不仅看皮肤。','unproven':['字符串拼接bootstrap模板未读，不由命名猜最终图层路径','具体supplier目标和当前运行注册选择未逐链核验','玩家四槽模型几何、实际UV与实机未验'],'full_runtime_binding_proven':False,'new_design_credit_from_classes':0})
    facts=[]
    for a in worn:
        im=Image.open(D/a['local']).convert('RGBA');h=im.getchannel('A').histogram();assert not a['binding_proven']
        facts.append({'case_key':a['case_key'],'variant':a['variant'],'source':a,'alpha_nonzero':sum(h[1:]),'alpha_extrema':list(im.getchannel('A').getextrema()),'standard_64x32_uv_assumed':False,'all_slots_binding_proven':False})
    save('native-layer-facts.json',{'layers':facts,'normal_slim_pairs':10,'variant_design_credit':0,'worn_binding_proven':False,'pixels_modified':False,'warning':'即便64×32文件也未证为普通玩家UV；常规/细臂只是同套适配，不能多计设计。'})
    flat=[c for row in review['observations'] for c in row['cases']];assert len(flat)==len(set(flat))==10 and set(flat)==cases and not review['excluded_cases']
    groups={g['semantic_group']:g for g in prior['groups']};new=append=0
    for row in review['observations']:
        k=row['semantic_group']
        if row['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP':assert k not in groups;groups[k]={'semantic_group':k,'cases':[],'observations':[]};new+=1
        else:assert row['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group']==k and k in groups;append+=1
        groups[k]['cases']=sorted(set(groups[k]['cases'])|set(row['cases']));groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':row['observation']})
    owners={}
    for k,g in groups.items():
        for c in g['cases']:assert c not in owners;owners[c]=k
    reviewed=sorted(set(owners)|{e['case_key'] for e in prior['excluded_cases']});assert (new,append,len(groups),len(owners),len(reviewed))==(3,4,211,604,618)
    save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':618,'armor_name_families':604,'conservative_learning_groups':211})
    save('reference-gate-accounting.json',{'required_valid_related_independent_designs':1000,'reviewed_name_families':618,'armor_name_families_after_exclusion':604,'excluded_from_full_armor_gate':14,'conservative_learning_groups_in_current_subset':211,'validated_independent_design_total':None,'maximum_credit_under_current_one_per_group_policy':211,'unfilled_minimum_under_current_policy':789,'reference_gate_met':False,'gap_limit':'211组含变体、局部和反例，不是211个已验完整独立设计；789仅是每组都合格时的最低缺口。常规/细臂、槽位、图标和原图集不重复计设计。'})
    assert all(review[k]==0 for k in ['new_artwork','production_changes','game_starts']) and not review['gate_met']
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'archive_sources':len(p['archives']),'new_complete_name_families_viewed':10,'native_icon_entries_viewed':40,'distinct_icon_payloads':len({a['sha256'] for a in icons}),'model_json_declarations_checked':40,'native_atlas_entries_viewed':20,'normal_slim_pairs':10,'static_context_class_payloads':5,'registry_name_four_slot_declarations':10,'final_worn_binding_proven':False,'new_learning_groups':3,'append_observations':4,'combined_learning_groups':211,'combined_reviewed_names':618,'combined_armor_names':604,'validated_independent_design_total':None,'reference_gate_met':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_scripts':{f:sha(D/f) for f in ['collect.py','record_review.py','verify.py']}}
    save('verification.json',result);print(json.dumps(result,ensure_ascii=False));assert not changed
if __name__=='__main__':main()
