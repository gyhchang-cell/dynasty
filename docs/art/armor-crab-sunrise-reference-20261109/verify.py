"""Reproducible D29 hashes, declarations, alias accounting, and protection checks."""
from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((D/n).read_text())
def main():
 p=load('provenance.json');assert sha(Path(p['archive']['path']))==p['archive']['sha256'];assert sha(R/p['prior_ledger'])==p['prior_ledger_sha256'];assert sha(Path(p['javap']))==p['javap_sha256']
 with zipfile.ZipFile(p['archive']['path']) as z:
  for a in p['records']:
   assert (D/a['local']).read_bytes()==z.read(a['entry']);assert sha(D/a['local'])==a['sha256']
   if 'size' in a:assert list(Image.open(D/a['local']).size)==a['size']
   if 'disassembly' in a:assert sha(D/a['disassembly'])==a['disassembly_sha256']
 v=load('verbose-context.json');assert sha(D/v['path'])==v['sha256']
 receipt=json.loads(next(D.glob('texture-requirements-receipt-*.json')).read_text())
 # Both authoritative requirements and their local full-text snapshot must remain the current accepted rule bytes.
 texts=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in texts})==1
 baseline=load('source-baseline.json');changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed,changed
 review=load('semantic-review.json');assert len(review['pages_actually_viewed'])==6
 for a in review['pages_actually_viewed']:assert sha(D/a['path'])==a['sha256']
 geom=load('geometry-study.json');assert sha(R/geom['borrowed_raster'])==geom['borrowed_raster_sha256'];assert [x['native_cubes'] for x in geom['cases']]==[17,18]
 bind=load('static-binding-study.json');assert len(bind['slot_chains'])==8 and all(c['static_chain_checked'] and not c['live_slot_visibility_proven'] for c in bind['slot_chains'])
 for row in bind['slot_chains']:
  s=row['source_icon_declaration'];assert s in load('declarations.json');assert s['model']['entry'].endswith(row['registry_name'].split(':')[1]+'.json');assert all(v>0 for v in row['root_descendant_cubes'].values())
 ledger=load('combined-semantic-ledger.json');prior=json.loads((R/p['prior_ledger']).read_text());assert ledger['reviewed_case_keys']==prior['reviewed_case_keys'];assert ledger['name_families']==640 and ledger['armor_name_families']==626 and ledger['conservative_learning_groups']==213
 assert all(x in ledger['case_to_group'] for x in review['aliases_do_not_add_names'].values());assert not ledger['gate_met'] and review['new_validated_independent_design_credit']==0
 result={'passed':True,'source_records_native_bytes_checked':len(p['records']),'classes_static_only':len(p['classes']),'explicit_static_slot_chains':8,'source_geometry_cubes':35,'pages_actually_viewed':6,'protected_paths':len(baseline),'protected_paths_changed':changed,'registered_aliases_not_new_designs':review['aliases_do_not_add_names'],'reviewed_name_families':640,'conservative_learning_groups':213,'reference_gate_met':False,'game_starts':0,'production_changes':0,'checklist_deletions':0,'input_hashes':{n:sha(D/n) for n in ['collect.py','study.py','bindings.py','semantic-review.json','static-binding-study.json','geometry-study.json','combined-semantic-ledger.json','source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
