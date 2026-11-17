"""Pinned bytecode declarations and research-only native-face diagram integrity."""
from pathlib import Path
import json,hashlib,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 c=read(D/'collection.json');prior=R/c['prior_native_collection'];assert sha(prior)==c['prior_native_collection_sha256'];old=read(prior);jar=Path(old['archive']);assert sha(jar)==old['archive_sha256'];assert hashlib.sha1(jar.read_bytes()).hexdigest()=='055b30d860ead928cba3849ba920c88b6950b654'
 mp=prior.parent/old['mapping_file'];assert sha(mp)==old['mapping_sha256'];assert hashlib.sha1(mp.read_bytes()).hexdigest()=='8e8c9be5dc27802caba47053d4fdea328f7f89bd'
 contract=read(D/'native-uv-contract.json');assert len(contract['faces'])==6 and len(contract['vertices'])==8 and len(contract['uv_local_linear_expressions'])==9;assert sorted(f['array_index'] for f in contract['faces'])==list(range(6));assert contract['mirror_rule']['post_remap_reverse_vertices_and_uv_together']
 with zipfile.ZipFile(jar) as z:
  for a in c['classes']:
   assert z.read(a['entry'])==(D/a['local']).read_bytes();assert sha(D/a['local'])==a['sha256'];assert sha(D/a['disassembly'])==a['disassembly_sha256']
 a=contract['cube_source'];base=R/contract['cube_source_base'];assert sha(base/a['local'])==a['sha256'] and sha(base/a['disassembly'])==a['disassembly_sha256'];assert len(c['classes'])==3
 pages=read(D/'native-layout-pages.json');assert sha(D/'native-uv-contract.json')==pages['contract_sha256'];assert sha(R/pages['source_nodes'])==pages['source_nodes_sha256'];assert sha(R/pages['raster'])==pages['raster_sha256'];assert len(pages['face_records'])==60 and sum(f['mirror'] for f in pages['face_records'])==18
 # Mirrored UV order must reverse with geometry, rather than relabel only the x bounds.
 for face in pages['face_records']:
  uv=face['pixel_uv_corners'];assert (uv[2][1]<uv[0][1])==(face['mirror'] != (face['face']=='UP'))
 for a in pages['pages']:assert sha(D/a['path'])==a['sha256'] and sha(R/a['analysis_atlas'])==a['analysis_atlas_sha256'] and not a['game_acceptance']
 assert len(pages['pages'])==2
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 base=read(D/'source-baseline.json');changed=[p for p,h in base.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed,changed
 result={'passed':True,'native_version':'1.19.2','native_cube_plus_helper_classes_verified':4,'native_declared_faces':6,'assembled_faces':60,'mirrored_faces':18,'software_pages_actually_viewed':2,'native_polygon_uv_and_mirror_declaration_closed':True,'Forge_hooks_and_game_equipment_acceptance':False,'new_names':0,'new_groups':0,'new_validated_independent_design_credit':0,'reference_gate_met':False,'protected_paths':len(base),'protected_paths_changed':changed,'production_changes':0,'game_starts':0,'checklist_deletions':0,'input_hashes':{p.name:sha(p) for p in [D/'collection.json',D/'decode_faces.py',D/'native-uv-contract.json',D/'render_native.py',D/'native-layout-pages.json',D/'source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
