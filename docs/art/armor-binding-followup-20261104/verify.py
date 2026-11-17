"""Verify D17 static-only follow-up against original outer/nested ZIP entries."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
import hashlib,json,zipfile,importlib.util
D=Path(__file__).resolve().parent;R=D.parents[2];OLD=R/'docs/art/armor-binding-reference-20261103';PRIOR=R/'docs/art/armor-local-complete-reference-20261104/combined-semantic-ledger.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 baseline=read(D/'source-baseline.json'); assert len(baseline)==289
 changes=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
 receipt=read(next(D.glob('texture-requirements-receipt-*.json')));assert len(receipt['targets'])==len(set(receipt['targets']))==24
 assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
 cp=read(D/'class-provenance.json'); np=read(D/'nested-class-provenance.json'); sp=read(D/'source-provenance.json'); study=read(D/'static-binding-study.json'); prior=read(PRIOR)
 assert (len(prior['groups']),len(prior['reviewed_case_keys']))==(203,532)
 assert len(cp['classes'])==9 and len(np['classes'])==6
 assert sha(Path(cp['javap']))==cp['javap_sha256']
 for a in prior['source_reviews']:assert sha(R/a['path'])==a['sha256']
 with ExitStack() as st:
  jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in cp['archives']}
  for a in cp['archives']: assert sha(Path(a['path']))==a['sha256']
  for a in cp['classes']:
   assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest();assert sha(D/a['disassembly'])==a['disassembly_sha256']
  nested=np['nested_archive'];assert sha(D/nested['local'])==nested['sha256']==hashlib.sha256(jars[nested['container']['path']].read(nested['entry'])).hexdigest()
  with zipfile.ZipFile(D/nested['local']) as z:
   for a in np['classes']:
    assert sha(D/a['local'])==a['sha256']==hashlib.sha256(z.read(a['entry'])).hexdigest();assert sha(D/a['disassembly'])==a['disassembly_sha256']
  assert sha(Path(sp['archive']))==sp['archive_sha256']
  with zipfile.ZipFile(sp['archive']) as z:assert sha(D/sp['local'])==sp['sha256']==hashlib.sha256(z.read(sp['entry'])).hexdigest()
  assert len(study['chains'])==16 and len({c['registered_item'] for c in study['chains']})==16
  missing=[]
  for c in study['chains']:
   for k in ['item_model','inventory_texture']:
    a=c[k];assert sha(OLD/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
   m=read(OLD/c['item_model']['local']);ns,tex=m['textures']['layer0'].split(':');assert c['inventory_texture']['entry']==f'assets/{ns}/textures/{tex}.png'
   path='assets/'+c['base_worn_location_before_forge_hook'].replace(':','/',1);jar=c['item_model']['jar'];exists=path in jars[jar].namelist()
   assert exists==c['default_target_found_in_prior_atlases']
   if exists:
    a=c['native_atlas'];assert a['entry']==path and sha(OLD/a['local'])==a['sha256']==hashlib.sha256(jars[jar].read(path)).hexdigest()
   else: assert c['case_key']=='celestial_core:guardian_ocean' and c['native_atlas'] is None;missing.append(c['base_worn_location_before_forge_hook'])
   assert not c['game_acceptance'] and not c['global_renderer_override_excluded'] and not c['standard_dynasty_uv_assumed']
  assert len(missing)==4 and len(set(missing))==2
 for x in study['reused_prior_disassembly'].values():assert sha(R/x['path'])==x['sha256']
 before=sha(D/'static-binding-study.json');before_excerpts=sha(D/'method-excerpts.json');spec=importlib.util.spec_from_file_location('binding_study',D/'study.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main();assert sha(D/'static-binding-study.json')==before and sha(D/'method-excerpts.json')==before_excerpts
 assert study['fresh_reference_design_credit']==0 and not study['native_or_game_acceptance'] and not study['final_hook_overrides_excluded']
 result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_STATIC_DEFAULT_RESOURCE_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changes,'changed_paths':changes,'outer_classes_read':9,'nested_classes_read':6,'prior_disassemblies_reused':4,'previous_name_families':4,'default_resource_chains_reconstructed':16,'default_resource_chains_with_matching_archive_payloads':12,'default_resource_chains_with_missing_archive_payloads':4,'missing_distinct_default_paths':sorted(set(missing)),'missing_paths_are_runtime_bug_proof':False,'final_hook_override_excluded':False,'new_reference_design_credit':0,'combined_learning_groups_unchanged':203,'combined_reviewed_names_unchanged':532,'validated_independent_design_total':None,'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_inputs':{'prior_ledger':{'path':str(PRIOR.relative_to(R)),'sha256':sha(PRIOR)},'prior_binding_study':{'path':str((OLD/'binding-and-rectangle-study.json').relative_to(R)),'sha256':sha(OLD/'binding-and-rectangle-study.json')},'scripts':{f:sha(D/f) for f in ['read_nested.py','study.py','verify.py']}}}
 save('verification.json',result);print(json.dumps(result,ensure_ascii=False));assert not changes
if __name__=='__main__':main()
