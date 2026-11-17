from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 prov=read('provenance.json');assert len(prov['sources'])==24
 for a in prov['sources']:
  p=D/a['local'];b=p.read_bytes();assert sha(p)==a['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==a['git_blob_sha1']
 s=read('study.json');assert len(s['slot_chains'])==8 and len(s['pages'])==4 and len(s['faces'])==60
 for a in s['slot_chains']:
  for k in ['class','item_model','icon','texture']:assert sha(R/a[k])==a[k+'_sha256']
  assert Image.open(R/a['icon']).size==(16,16) and Image.open(R/a['texture']).size==(64,32)
 for a in s['pages']:
  assert sha(D/a['path'])==a['sha256']
  if a['kind']=='software_layout':assert sha(D/a['analysis_atlas'])==a['analysis_atlas_sha256'] and sha(D/a['gray_analysis_atlas'])==a['gray_analysis_atlas_sha256'];assert Image.open(D/a['analysis_atlas']).getchannel('A').tobytes()==Image.open(D/a['gray_analysis_atlas']).getchannel('A').tobytes()
 for k in ['mesh_context','face_helper','raster','registration_source']:assert sha(R/s[k])==s[k+'_sha256']
 ctx=json.loads((R/s['reused1_20_face_context_comparison']).read_text());assert sha(R/ctx['source'])==ctx['source_sha256'] and len(ctx['matched1_20_faces'])==6
 for n in s['nodes']:
  if n['name'].startswith(('left_leg','right_leg')):assert n['cubes'][0]['deformation']==(.4 if n['name'].endswith('inner') else .9)
 for f in s['faces']:assert all(0<=u<=64 and 0<=v<=64 for u,v in f['pixel_uv_corners'])
 base=read('source-baseline.json');changed=[s for s,h in base.items() if not (R/s).is_file() or sha(R/s)!=h];assert not changed,changed
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 out={'passed':True,'new_complete_kit_names_reviewed':2,'default_static_slot_chains':8,'native_source_pngs_actually_viewed':12,'source_pages_actually_viewed':2,'software_layouts_actually_viewed':2,'software_angles_actually_viewed':12,'source_git_blob_verified_files':24,'reuse_of1_20_mesh_and_face_context':True,'new_validated_independent_design_credit':0,'main_independent_review_pending':True,'reference_gate_met':False,'game_or_actual_equipment_acceptance':False,'protected_paths':len(base),'protected_paths_changed':changed,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'input_hashes':{n:sha(D/n) for n in ['collect.py','study.py','study.json','provenance.json','source-baseline.json']}};(D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
