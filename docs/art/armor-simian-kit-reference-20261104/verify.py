"""Exact static source provenance, slot declarations and conservative accounting."""
from pathlib import Path
from datetime import datetime,timezone
from contextlib import ExitStack
import json,hashlib,zipfile,importlib.util,re
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ctx=read(D/'collection-context.json')
 for k in ['collector','prior_ledger','candidate_inventory','prior_progress','prior_verification']:assert sha(R/ctx[k])==ctx[k+'_sha256'],k
 prior=read(R/ctx['prior_ledger']);assert (len(prior['groups']),len(prior['reviewed_case_keys']),len(prior['case_to_group']))==(212,629,615)
 p=read(D/'provenance.json');decl=read(D/'declarations.json');study=read(D/'binding-and-geometry-study.json');assembly=read(D/'assembly-study.json');review=read(D/'semantic-review.json');reg=read(D/'registry-verbose.json')
 keys={x['case_key'] for x in p['cases']};assert len(keys)==4 and not keys&set(prior['reviewed_case_keys'])
 icons=[x for c in p['cases'] for x in c['icons']];assert len(icons)==len(decl)==16 and len({x['sha256'] for x in icons})==10 and len(p['native_atlases'])==6 and len(p['classes'])==43
 assert sha(Path(p['javap']))==p['javap_sha256']
 with ExitStack() as st:
  jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']}
  for a in p['archives']:assert sha(Path(a['path']))==a['sha256']
  for a in icons+[x['model'] for x in decl]+p['native_atlases']+p['classes']+p['languages']:
   assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
   if 'size' in a:assert list(Image.open(D/a['local']).size)==a['size']
   if 'disassembly' in a:assert sha(D/a['disassembly'])==a['disassembly_sha256']
 assert sha(D/reg['local'])==reg['sha256'] and reg['source_class'] in p['classes']
 for a in decl:
  m=read(D/a['model']['local']);assert m['textures']['layer0']==a['texture_location'] and m['parent']==a['parent']
  ns,path=a['texture_location'].split(':');assert a['icon']['entry']==f'assets/{ns}/textures/{path}.png'
 spec=importlib.util.spec_from_file_location('read_only_declaration_decoder',D/'study.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 for name,m in study['models'].items():
  assert m['source'] in p['classes']
  assert {k:v for k,v in m.items() if k!='source'}==mod.decode((D/m['source']['disassembly']).read_text())
 assert [study['models'][n]['raw_addbox_calls'] for n in ['Modelwukong_reworked1','Modelwukong_reworked2']]==[66,6]
 rows=study['slot_chains'];assert len(rows)==len({x['item_id'] for x in rows})==16
 registry=(D/reg['local']).read_text();boot=registry.split('BootstrapMethods:',1)[1];code=registry.split('  static {};',1)[1].split('BootstrapMethods:',1)[0]
 for row in rows:
  assert row['item_class'] in p['classes'] and row['client_extension'] in p['classes'] and row['source_texture'] in p['native_atlases']
  assert row['registry_instructions'] in code and row['factory_method'] in boot and row['factory_instructions'] in registry
  assert row['declared_correspondence_checked'] and not row['live_player_render_proven']
  m=study['models'][row['model']];counts={n:sum(len(x['cubes']) for x in m['nodes'] if n in mod.ancestry(x['name'],m['nodes'])) for n in row['model_fields']}
  assert counts==row['root_descendant_cubes'] and all(counts.values())
  item=(D/row['item_class']['disassembly']).read_text();assert row['texture_resource'] in item
 for a in study['atlas_alpha_context']:
  im=Image.open(D/a['source']['local']).convert('RGBA');assert a['nonzero_alpha_pixels']==sum(im.getchannel('A').histogram()[1:])
  assert a['direct_custom_item_texture_users']==sum(x['source_texture']==a['source'] for x in rows)
 for key in ['borrowed_raster','vanilla_cube_polygon_context']:assert sha(R/assembly[key])==assembly[key+'_sha256']
 assert len(assembly['software_analysis_pages'])==4
 for a in assembly['software_analysis_pages']:assert sha(D/a['path'])==a['sha256'] and a['cubes_in_static_union']==72
 assert len(review['pages_actually_viewed'])==14
 for a in review['pages_actually_viewed']:assert sha(D/a['path'])==a['sha256']
 flat=[k for a in review['observations'] for k in a['cases']];assert len(flat)==len(set(flat))==4 and set(flat)==keys
 assert review['new_validated_independent_design_credit']==0 and not review['reference_gate_met']
 groups={g['semantic_group']:g for g in prior['groups']};new=0
 for a in review['observations']:
  k=a['semantic_group'];assert a['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP' and k not in groups
  groups[k]={'semantic_group':k,'cases':a['cases'],'observations':[{'source':str((D/'semantic-review.json').relative_to(R)),'observation':a['observation']} ]};new+=1
 owners={}
 for k,g in groups.items():
  for case in g['cases']:assert case not in owners;owners[case]=k
 reviewed=sorted(set(owners)|{x['case_key'] for x in prior['excluded_cases']});assert (new,len(groups),len(owners),len(reviewed))==(1,213,619,633)
 save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':633,'armor_name_families':619,'conservative_learning_groups':213})
 receipt=read(next(D.glob('texture-requirements-receipt-*.json')));assert len(receipt['targets'])==len(set(receipt['targets']))==24
 assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
 baseline=read(D/'source-baseline.json');assert len(baseline)==289
 changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
 gate={'required_valid_related_independent_designs':1000,'reviewed_name_families':633,'armor_name_families':619,'excluded_from_full_armor_gate':14,'conservative_learning_groups':213,'validated_independent_design_total':None,'minimum_open_gap_under_current_policy':787,'reference_gate_met':False,'note':'213学习组含变体/局部/反例，不是已验完整独立设计数；787只在每组都合格时成立。'};save('reference-gate-accounting.json',gate)
 files=['collect.py','study.py','assemble.py','record_review.py','verify.py','collection-context.json','provenance.json','declarations.json','registry-verbose.json','binding-and-geometry-study.json','assembly-study.json','semantic-review.json','combined-semantic-ledger.json','reference-gate-accounting.json','source-baseline.json']
 result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'new_names':4,'new_learning_groups':1,'new_validated_independent_design_credit':0,'native_item_icons':16,'distinct_icon_png':10,'source_atlases':6,'source_classes':43,'static_native_slot_chains':16,'constant_model_definitions':2,'declaration_addbox_calls':72,'actually_viewed_analysis_pages':14,'cumulative':gate,'runtime_acceptance':False,'production_changes':0,'new_artwork':0,'game_starts':0,'checklist_deletions':0,'evidence_sha256':{f:sha(D/f) for f in files}}
 save('verification.json',result);print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},ensure_ascii=False));assert not changed
if __name__=='__main__':main()
