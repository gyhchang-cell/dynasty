"""Verify native prerequisite audit and partial viewed-source receipts without executing mods."""
from pathlib import Path
import json,zipfile,hashlib
from PIL import Image
from io import BytesIO
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 a=read('candidate-resolution.json');assert sha(R/a['input'])==a['input_sha256'];assert sha(R/a['prior_ledger'])==a['prior_ledger_sha256'];assert len(a['candidates'])==69
 records=a['model_source_records']+read('unaccepted-visual-source.json')['records']
 for jar,data in a['archives'].items():
  assert sha(Path(jar))==data['sha256']
  with zipfile.ZipFile(jar) as z:
   for rec in records:
    if rec['jar']!=jar:continue
    b=z.read(rec['entry']);assert (D/rec['local']).read_bytes()==b and hashlib.sha256(b).hexdigest()==rec['sha256']
    if 'size' in rec:assert list(Image.open(BytesIO(b)).size)==rec['size']
    if 'disassembly' in rec:assert sha(D/rec['disassembly'])==rec['disassembly_sha256']
   for row in a['candidates']:
    if row['jar']!=jar:continue
    for p in row['parts']:
     if 'native_png' in p:
      n=p['native_png'];b=z.read(n['entry']);assert hashlib.sha256(b).hexdigest()==n['sha256'] and list(Image.open(BytesIO(b)).size)==n['size']
     if p.get('missing_from_native_jar'):assert p['texture_entry'] not in z.namelist()
 assert a['counts']=={'NATIVE_RESOLUTION_INCOMPLETE':8,'ALL_FOUR_NATIVE_LAYER0_PNG_PRESENT':61};assert a['native_missing_png_parts']==32 and a['reference_credit']==0
 review=read('semantic-review.json');assert len(review['pages_actually_viewed'])==10
 for p in review['pages_actually_viewed']:assert sha(D/p['path'])==p['sha256']
 part=read('partial-class-slot-texture-study.json');assert len(part['rows'])==12 and not part['registry_to_factory_closed']
 for row in part['rows']:
  assert sha(D/row['disassembly'])==row['disassembly_sha256'];assert '// String '+row['texture_resource'] in (D/row['disassembly']).read_text();assert sha(D/row['source_texture']['local'])==row['source_texture']['sha256']
 inf=[r for r in part['rows'] if r['case_key']=='infectum:test'];assert len(inf)==4 and all(r['texture_resource']=='infectum:textures/entities/armor_layer1_1.png' for r in inf)
 texts=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in texts})==1
 baseline=read('source-baseline.json');changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed,changed
 result={'passed':True,'candidate_models_resolved':69,'native_complete_candidates':61,'native_incomplete_candidates':8,'native_missing_texture_parts':32,'source_archives_checked':len(a['archives']),'source_records_checked':len(records),'actual_viewed_pages':10,'partial_class_slot_texture_declarations':12,'full_registry_factory_chain_proven':False,'protected_paths':len(baseline),'protected_paths_changed':changed,'new_reference_design_credit':0,'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0,'input_hashes':{n:sha(D/n) for n in ['audit.py','candidate-resolution.json','unaccepted-visual-source.json','partial-class-slot-texture-study.json','semantic-review.json','source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
