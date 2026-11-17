"""Verify exact D26 source assets, read-only native chains and conservative dedup."""
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
 ctx=read(D/'collection-context.json')
 for key in ['collector','prior_ledger','candidate_inventory','icon_chart_collector','prior_continuation','prior_continuation_verification','reused_static_context']:assert sha(R/ctx[key])==ctx[key+'_sha256'],key
 prior=read(R/ctx['prior_ledger']);assert (len(prior['groups']),len(prior['reviewed_case_keys']),len(prior['case_to_group']))==(212,623,609)
 p=read(D/'provenance.json');dec=read(D/'resource-declarations.json');cl=read(D/'class-provenance.json');extra=read(D/'additional-provenance.json');lang=read(D/'language-provenance.json');resources=read(D/'static-declarations.json');geo=read(D/'geometry-animation-context.json');study=read(D/'geometry-study.json');bind=read(D/'binding-study.json');review=read(D/'semantic-review.json')
 keys={c['case_key'] for c in p['cases']};assert len(keys)==6 and keys==set(ctx['selected_case_keys']) and not keys&set(prior['reviewed_case_keys'])
 icons=[i for c in p['cases'] for i in c['icons']];assert len(icons)==len(dec)==24 and len(p['worn_textures'])==6 and len(cl['classes'])==31 and len(geo)==12
 assert not read(D/'animation-candidates.json')
 assert sha(Path(cl['javap']))==cl['javap_sha256']
 archives=p['archives']+[extra['geckolib_archive']]
 with ExitStack() as st:
  jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in archives}
  for a in archives:assert sha(Path(a['path']))==a['sha256']
  for a in icons+p['worn_textures']+[x['model'] for x in dec]+cl['classes']+geo+[lang,extra['geckolib_class'],extra['slot_switch_class']]:
   assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
   if 'size' in a:assert list(Image.open(D/a['local']).size)==a['size']
   if 'disassembly' in a:assert sha(D/a['disassembly'])==a['disassembly_sha256']
 assert sha(D/'additional-provenance.json')==ctx['reused_static_context_sha256']
 labels=read(D/lang['local'])
 for a in dec:
  m=read(D/a['model']['local']);assert m['textures']['layer0']==a['texture_location'] and m['parent']==a['parent']
  ns,path=a['texture_location'].split(':');assert a['texture']['entry']==f'assets/{ns}/textures/{path}.png'
  assert labels['item.'+a['case_key'].replace(':','.')+'_'+a['part']]==a['label']
 v=extra['registry_verbose'];assert sha(D/v['local'])==v['sha256']
 assert sha(R/study['borrowed_raster'])==study['borrowed_raster_sha256']
 assert len(study['cases'])==6 and len(bind['slot_chains'])==24 and len({x['item_id'] for x in bind['slot_chains']})==24
 for a in study['cases']:
  source=next(x for x in geo if x['case_key']==a['case_key'] and x['kind']=='GEOMETRY_ATLAS_CONTEXT');g=read(D/source['local'])['minecraft:geometry'][0]
  cubes=[c for b in g['bones'] for c in b.get('cubes',[])];assert len(cubes)==a['cubes']==len(a['cube_uv_records'])
  assert len(g['bones'])==a['bones']
  rawbones={b['name']:b for b in g['bones']}
  def ancestry(n):
   out=[]
   while n:
    assert n not in out
    out.append(n);n=rawbones[n].get('parent')
   return out
  for c,row in zip(cubes,a['cube_uv_records']):
   for k in ['origin','size','uv']:assert row[k]==c[k]
   assert len(row['faces'])==6
  assert a['native_texture_size'][0]/a['uv_grid'][0]==a['native_texture_size'][1]/a['uv_grid'][1]==a['texture_to_uv_scale']
  assert sha(D/a['software_assembly'])==a['software_assembly_sha256']
  chains=[x for x in bind['slot_chains'] if x['case_key']==a['case_key']];assert {x['slot_type'] for x in chains}=={'HELMET','CHESTPLATE','LEGGINGS','BOOTS'}
  for row in chains:
   assert row['geometry_source']==source and row['declared_chain_checked'] and not row['current_live_render_or_slot_visibility_proven']
   expected={root:sum(len(b.get('cubes',[])) for b in g['bones'] if root in ancestry(b['name'])) for root in row['relevant_armor_roots']}
   assert expected==row['canonical_root_descendant_cube_counts'] and all(expected.values())
   assert row['geometry_slot_correspondence_complete'] and not row['missing_expected_geometry_roots'] and not row['empty_expected_geometry_roots']
 assert sum(x['cubes'] for x in study['cases'])==1144
 assert len(review['pages_actually_viewed'])==15
 for a in review['pages_actually_viewed']:assert sha(D/a['path'])==a['sha256']
 flat=[k for x in review['observations'] for k in x['cases']];assert len(flat)==len(set(flat))==6 and set(flat)==keys
 groups={g['semantic_group']:g for g in prior['groups']};new=0
 for row in review['observations']:
  k=row['semantic_group']
  if row['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP':assert k not in groups;groups[k]={'semantic_group':k,'cases':[],'observations':[]};new+=1
  else:assert row['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group']==k and k in groups
  groups[k]['cases']=sorted(set(groups[k]['cases'])|set(row['cases']));groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':row['observation']})
 owners={}
 for k,g in groups.items():
  for case in g['cases']:assert case not in owners;owners[case]=k
 reviewed=sorted(set(owners)|{x['case_key'] for x in prior['excluded_cases']});assert (new,len(groups),len(owners),len(reviewed))==(0,212,615,629)
 save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':629,'armor_name_families':615,'conservative_learning_groups':212})
 receipt=read(next(D.glob('texture-requirements-receipt-*.json')));assert len(receipt['targets'])==len(set(receipt['targets']))==24
 assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
 baseline=read(D/'source-baseline.json');assert len(baseline)==289
 changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
 gate={'required_valid_related_independent_designs':1000,'reviewed_name_families':629,'armor_name_families':615,'excluded_from_full_armor_gate':14,'conservative_learning_groups':212,'validated_independent_design_total':None,'minimum_open_gap_under_current_policy':788,'reference_gate_met':False,'note':'名称/槽位/体块/图集密度/软件视角不算独立设计；212含变体/局部/反例，788仅是每组都合格时的最低缺口。'}
 save('reference-gate-accounting.json',gate)
 files=['collect.py','study_geometry.py','study_binding.py','record_review.py','verify.py','collection-context.json','provenance.json','resource-declarations.json','class-provenance.json','additional-provenance.json','language-provenance.json','static-declarations.json','geometry-animation-context.json','geometry-study.json','binding-study.json','semantic-review.json','source-baseline.json','reference-gate-accounting.json','combined-semantic-ledger.json']
 result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changed else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changed,'changed_paths':changed,'new_names':6,'native_icons':24,'native_atlases':6,'geo_models':6,'geo_cubes_read':1144,'native_classes':31,'additional_geckolib_classes':2,'static_native_slot_chains':24,'actual_viewed_analysis_sheets':15,'new_learning_groups':0,'new_validated_independent_design_credit':0,'cumulative':gate,'runtime_acceptance':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_sha256':{f:sha(D/f) for f in files}}
 save('verification.json',result);print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},ensure_ascii=False));assert not changed
if __name__=='__main__':main()
