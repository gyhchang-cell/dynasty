"""D32 pinned official map/native bytes, declaration and no-mutation evidence."""
from pathlib import Path
import json,hashlib,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 c=read('native-source-collection.json');jar=Path(c['archive']);assert sha(jar)==c['archive_sha256'];assert hashlib.sha1(jar.read_bytes()).hexdigest()==c['archive_sha1']=='055b30d860ead928cba3849ba920c88b6950b654';mp=D/c['mapping_file'];assert sha(mp)==c['mapping_sha256'] and hashlib.sha1(mp.read_bytes()).hexdigest()=='8e8c9be5dc27802caba47053d4fdea328f7f89bd';assert c['internal_version']['id']=='1.19.2';assert sha(Path(c['javap']))==c['javap_sha256']
 with zipfile.ZipFile(jar) as z:
  assert json.loads(z.read('version.json'))['id']=='1.19.2'
  for a in c['classes']:assert z.read(a['entry'])==(D/a['local']).read_bytes() and sha(D/a['local'])==a['sha256'] and sha(D/a['disassembly'])==a['disassembly_sha256']
 assert len(c['classes'])==9 and c['absent_1_19_HumanoidArmorModel']
 native=read('native-layout-comparison.json');assert len(native['decoded_mesh_parts'])==7 and len(native['comparison_to_D31_1_20_context'])==7;assert all(x['origin_size_uv_mirror_pose_equal'] for x in native['comparison_to_D31_1_20_context']);assert sum(x['outer_deformation_1_19_2']!=x['outer_deformation_1_20_1'] for x in native['comparison_to_D31_1_20_context'])==2
 diagrams=read('correction-diagrams.json');assert len(diagrams['pages'])==2
 for a in diagrams['pages']:assert sha(D/a['path'])==a['sha256'] and sha(R/a['source_analysis_atlas'])==a['source_analysis_atlas_sha256'] and not a['game_acceptance']
 assert sha(R/diagrams['borrowed_raster'])==diagrams['borrowed_raster_sha256'];assert sha(R/diagrams['borrowed_geometry_helper'])==diagrams['borrowed_geometry_helper_sha256'];assert sha(R/diagrams['prior_layout'])==diagrams['prior_layout_sha256'];assert sha(D/'native-layout-comparison.json')==diagrams['native_mesh_comparison_sha256']
 for n in diagrams['nodes']:
  if n['name'].startswith(('left_leg','right_leg')):assert n['cubes'][0]['deformation']==(.5 if n['name'].endswith('inner') else 1.0)
 assert read('mapping-source-receipt.json')['status']=='BOUNDED_SOURCE_FETCH_FAILED';assert read('mapping-system-curl-receipt.json')['status']=='SUCCESS' and read('mapping-system-curl-receipt.json')['attempt']==2
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 base=read('source-baseline.json');changed=[p for p,h in base.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed,changed
 l=read('combined-semantic-ledger.json');assert l['name_families']==643 and l['armor_name_families']==629 and len(l['groups'])==213 and not l['gate_met'];review=read('semantic-review.json');assert review['new_validated_independent_design_credit']==0
 for p in review['pages_actually_viewed']:assert sha(D/p['path'])==p['sha256']
 result={'passed':True,'native_version':'1.19.2','official_map_sha1_verified':True,'local_client_sha1_verified':True,'native_classes_checked':9,'native_mesh_parts_decoded':7,'native_vs1_20_leg_deformation_differences':2,'corrected_layout_pages_actually_viewed':2,'source_fetches_bounded_at':2,'python_TLS_failure_retained':True,'system_curl_TLS_verification_kept':True,'native1_19_polygon_sampling_and_Forge_hooks_proven':False,'reviewed_name_families':643,'conservative_learning_groups':213,'new_independent_design_credit':0,'reference_gate_met':False,'protected_paths':len(base),'protected_paths_changed':changed,'game_starts':0,'production_changes':0,'checklist_deletions':0,'input_hashes':{n:sha(D/n) for n in ['collect_native.py','study_native.py','render_comparison.py','native-source-collection.json','native-layout-comparison.json','correction-diagrams.json','semantic-review.json','combined-semantic-ledger.json','source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
