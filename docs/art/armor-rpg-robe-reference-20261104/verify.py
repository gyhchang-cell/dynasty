"""D28 read-only source proofs; keep unresolved registration/runtime limits explicit."""
from pathlib import Path
from datetime import datetime,timezone
from contextlib import ExitStack
import json,hashlib,zipfile,re
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ctx=read(D/'collection-context.json')
 for k in ['collector','prior_ledger','prior_progress','prior_verification']:assert sha(R/ctx[k])==ctx[k+'_sha256'],k
 prior=read(R/ctx['prior_ledger']);assert (len(prior['groups']),len(prior['reviewed_case_keys']),len(prior['case_to_group']))==(213,633,619)
 for fn in ['alternate-name-candidates.json','standard-name-candidates.json']:assert read(D/fn)['reference_credit']==0
 p=read(D/'provenance.json');decl=read(D/'declarations.json');s=read(D/'binding-and-geometry-study.json');v=read(D/'verbose-context.json');review=read(D/'semantic-review.json')
 keys={x['case_key'] for x in p['cases']};assert len(keys)==7 and not keys&set(prior['reviewed_case_keys'])
 icons=[x for c in p['cases'] for x in c['icons']];assert len(icons)==len(decl)==28 and len(p['native_atlases'])==7 and len(p['classes'])==7 and len(p['geometry_context'])==2
 assert sha(Path(p['javap']))==p['javap_sha256']
 with ExitStack() as st:
  jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']}
  for a in p['archives']:assert sha(Path(a['path']))==a['sha256']
  for a in icons+[x['model'] for x in decl]+p['native_atlases']+p['classes']+p['geometry_context']+p['other_context']:
   assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
   if 'size' in a:assert list(Image.open(D/a['local']).size)==a['size']
   if 'disassembly' in a:assert sha(D/a['disassembly'])==a['disassembly_sha256']
 for a in v:assert a['source_class'] in p['classes'] and sha(D/a['local'])==a['sha256']
 assert len(v)==2
 for a in decl:
  m=read(D/a['model']['local']);assert m['textures']['layer0']==a['texture_location'] and m['parent']==a['parent']
  ns,path=a['texture_location'].split(':');assert a['icon']['entry']==f'assets/{ns}/textures/{path}.png'
 assert s['source_geometry'] in p['geometry_context']
 g=read(D/s['source_geometry']['local'])['minecraft:geometry'][0];cubes=[(b['name'],i,c) for b in g['bones'] for i,c in enumerate(b.get('cubes',[]))]
 assert len(cubes)==s['native_cubes']==len(s['cube_records'])==17 and s['geometry_grid']==[64,64]
 for (name,i,c),a in zip(cubes,s['cube_records']):assert a['bone']==name and a['cube_index']==i and a['source_cube']==c
 assert sum(s['root_descendant_cubes'].values())==17 and len(s['root_descendant_cubes'])==8
 assert sha(R/s['borrowed_raster'])==s['borrowed_raster_sha256']
 assert len(s['material_cases'])==len(s['software_analysis_pages'])==7
 av=(D/'disassembly/Armors.class.txt').read_text();mv=(D/'disassembly/WizardArmorModel.verbose.txt').read_text()
 assert r'textures/armor/\u0001.png' in mv and '0: aconst_null' in s['getAnimationResource_excerpt'] and '0: return' in s['registerControllers_excerpt'] and not s['source_animation_file_is_selected']
 for a in s['material_cases']:
  assert a['native_material_constructor_excerpt'] in av and a['factory_excerpt'] in av
  assert a['source_geometry']==s['source_geometry'] and a['source_texture'] in p['native_atlases'] and a['source_texture']['size']==[64,64]
  assert a['texture_resource']=='wizards:textures/armor/'+a['case_key'].split(':')[1]+'.png'
  assert len(set(a['distinct_intermediary_slot_type_fields']))==4 and a['factory_excerpt'].count('// class net/wizards/item/WizardArmor')==4
  assert a['four_item_factory_declaration_checked'] and a['custom_material_name_concatenation_checked'] and not a['external_Armor_Set_registration_and_live_slot_visibility_proven']
 for a in s['software_analysis_pages']:assert sha(D/a['path'])==a['sha256']
 assert len(review['pages_actually_viewed'])==21
 for a in review['pages_actually_viewed']:assert sha(D/a['path'])==a['sha256']
 flat=[k for a in review['observations'] for k in a['cases']];assert len(flat)==len(set(flat))==7 and set(flat)==keys
 assert review['new_learning_groups']==review['new_validated_independent_design_credit']==0 and not review['reference_gate_met']
 groups={g['semantic_group']:g for g in prior['groups']}
 for a in review['observations']:
  k=a['semantic_group'];assert a['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and a['prior_group']==k and k in groups
  groups[k]['cases']=sorted(set(groups[k]['cases'])|set(a['cases']));groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':a['observation']})
 owners={}
 for k,g in groups.items():
  for case in g['cases']:assert case not in owners;owners[case]=k
 reviewed=sorted(set(owners)|{x['case_key'] for x in prior['excluded_cases']});assert (len(groups),len(owners),len(reviewed))==(213,626,640)
 save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':640,'armor_name_families':626,'conservative_learning_groups':213})
 receipt=read(next(D.glob('texture-requirements-receipt-*.json')));assert len(receipt['targets'])==len(set(receipt['targets']))==24
 assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
 baseline=read(D/'source-baseline.json');assert len(baseline)==289;changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
 gate={'required_valid_related_independent_designs':1000,'reviewed_name_families':640,'armor_name_families':626,'excluded_from_full_armor_gate':14,'conservative_learning_groups':213,'validated_independent_design_total':None,'minimum_open_gap_under_current_policy':787,'reference_gate_met':False,'note':'213学习组包含局部/变体/反例，640名称也不是640个有效完整独立设计；787仅在每组均合格时成立。'};save('reference-gate-accounting.json',gate)
 files=['collect.py','study.py','verify.py','collection-context.json','alternate-name-candidates.json','standard-name-candidates.json','provenance.json','declarations.json','verbose-context.json','binding-and-geometry-study.json','semantic-review.json','combined-semantic-ledger.json','reference-gate-accounting.json','source-baseline.json']
 out={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'new_names':7,'new_learning_groups':0,'new_validated_independent_design_credit':0,'native_icons':28,'native_atlases':7,'source_classes':7,'shared_geo_cubes':17,'static_material_factory_declarations':7,'actual_viewed_analysis_pages':21,'external_slot_registration_closed':False,'animation_selection_proven':False,'cumulative':gate,'runtime_acceptance':False,'production_changes':0,'new_artwork':0,'game_starts':0,'checklist_deletions':0,'evidence_sha256':{f:sha(D/f) for f in files}}
 save('verification.json',out);print(json.dumps({k:v for k,v in out.items() if k!='evidence_sha256'},ensure_ascii=False));assert not changed
if __name__=='__main__':main()
