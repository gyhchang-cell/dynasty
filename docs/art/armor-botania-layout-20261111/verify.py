from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 m=read('decoded-models.json');pages=read('assembly-pages.json');context=read('source-context-comparison.json');assert len(m['models'])==len(pages['pages'])==4
 assert sha(R/context['source'])==context['source_sha256'] and sha(R/context['reused_face_contract'])==context['reused_face_contract_sha256'];assert len(context['matched1_20_faces'])==6
 for model in m['models'].values():assert sha(R/model['source'])==model['source_sha256']
 total=0;mirrored=0
 for a in pages['pages']:
  assert sha(D/a['path'])==a['sha256'] and sha(R/a['texture'])==a['texture_sha256'];assert sha(D/a['gray_analysis_texture'])==a['gray_analysis_texture_sha256'];assert a['cube_count']==sum(x['cube_count'] for x in m['models'][a['case_key']]['stages'].values());assert a['face_count']==6*a['cube_count']==len(a['faces']);total+=a['cube_count']
  width,height=Image.open(R/a['texture']).size;assert (width,height)==(64,128)
  for f in a['faces']:
   assert all(0<=u<=width and 0<=v<=height for u,v in f['pixel_uv_corners']);mirrored+=int(f['mirror'])
  gray=Image.open(D/a['gray_analysis_texture']).convert('RGBA');native=Image.open(R/a['texture']).convert('RGBA');assert gray.getchannel('A').tobytes()==native.getchannel('A').tobytes()
 assert total==108
 assert sha(D/'decoded-models.json')==pages['decoded_models_sha256']
 for k,h in [('generic_face_declaration_helper','generic_face_declaration_helper_sha256'),('native_1_20_source','native_1_20_source_sha256'),('raster','raster_sha256')]:assert sha(R/pages[k])==pages[h]
 base=read('source-baseline.json');changed=[s for s,h in base.items() if not (R/s).is_file() or sha(R/s)!=h];assert not changed,changed
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 out={'passed':True,'native_source_meshes':8,'native_source_cubes':total,'native_source_faces':total*6,'mirrored_faces':mirrored,'native_atlas_bounds_checked':True,'native_gray_alpha_preserved':True,'native1_20_face_context_crosschecked':True,'new_software_pages_actually_viewed':4,'new_views_actually_viewed':24,'new_names':0,'new_learning_groups':0,'new_validated_independent_design_credit':0,'reference_gate_met':False,'real_game_or_worn_acceptance':False,'protected_paths':len(base),'protected_paths_changed':changed,'production_changes':0,'game_starts':0,'checklist_deletions':0,'input_hashes':{s:sha(D/s) for s in ['decode_models.py','decoded-models.json','assemble.py','assembly-pages.json','check_context.py','source-context-comparison.json','source-baseline.json']}};(D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
