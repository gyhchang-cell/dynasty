"""D31 fixed-input native bytes, chain and layout/evidence verification."""
from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'docs/art/armor-candidate-resolution-20261109'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 c=read('collection.json');assert sha(Path(c['javap']))==c['javap_sha256'];assert sha(R/c['prior_visual_source'])==c['prior_visual_source_sha256'];assert sha(R/c['prior_partial_binding'])==c['prior_partial_binding_sha256']
 for a in c['records']:
  assert sha(Path(a['jar']))==a['jar_sha256']
  with zipfile.ZipFile(a['jar']) as z:assert z.read(a['entry'])==(D/a['local']).read_bytes()
  assert sha(D/a['local'])==a['sha256']
  for kind in ['plain','verbose']:assert sha(D/a[kind]['path'])==a[kind]['sha256']
 b=read('closed-static-bindings.json');assert len(b['rows'])==12 and len({r['native_registry_id'] for r in b['rows']})==12
 for row in b['rows']:
  assert row['registered_factory_slot_texture_static_chain_closed'] and not row['runtime_acceptance'];a=row['prior_slot_texture_declaration'];assert sha(P/a['disassembly'])==a['disassembly_sha256'];assert sha(P/row['actual_worn_texture']['local'])==row['actual_worn_texture']['sha256']
  assert row['native_registry_id'].split(':')[1] in row['native_icon_model']['chain'][0]['entry'];assert row['concrete_item_class'].split('/')[-1].split('$')[-1].upper() in ['HELMET','CHESTPLATE','LEGGINGS','BOOTS']
 assert sum(r['factory_kind']=='DIRECT_CONSTRUCTOR_METHOD_HANDLE' for r in b['rows'])==4
 layout=read('layout-study.json');assert sha(Path(layout['sources_jar']))==layout['sources_jar_sha256'];assert sha(R/layout['borrowed_raster'])==layout['borrowed_raster_sha256']
 with zipfile.ZipFile(layout['sources_jar']) as z:
  for a in layout['sources']:assert z.read(a['entry'])==(D/a['local']).read_bytes() and sha(D/a['local'])==a['sha256']
 assert len(layout['software_pages'])==3 and len(layout['mesh_declarations'])==10
 for p in layout['software_pages']:
  assert sha(D/p['path'])==p['sha256'];assert sha(D/p['analysis_atlas'])==p['analysis_atlas_sha256'];im=Image.open(D/p['analysis_atlas']).convert('RGBA');assert im.size==(64,64)
  assert im.crop((0,0,64,32)).tobytes()==Image.open(P/p['native_outer']['local']).convert('RGBA').tobytes();assert im.crop((0,32,64,64)).tobytes()==Image.open(P/p['native_leggings']['local']).convert('RGBA').tobytes()
 review=read('semantic-review.json');assert len(review['pages_actually_viewed'])==3
 for p in review['pages_actually_viewed']:assert sha(D/p['path'])==p['sha256']
 ledger=read('combined-semantic-ledger.json');old=json.loads((R/c['prior_ledger']).read_text());new=set(ledger['reviewed_case_keys'])-set(old['reviewed_case_keys']);assert new=={'infectum:test','poppy:player_armor_armor','theyarewatching:armorv'};assert ledger['name_families']==643 and ledger['armor_name_families']==629 and len(ledger['groups'])==213 and not ledger['gate_met'];assert review['new_validated_independent_design_credit']==0
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 base=read('source-baseline.json');changed=[p for p,h in base.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed,changed
 result={'passed':True,'native_registry_classes':3,'native_static_slot_chains':12,'direct_constructor_factories':4,'lambda_constructor_factories':8,'new_actually_viewed_standard_layout_pages':3,'prior_D30_native_pages_reused_not_recounted':10,'native_version_exact_layout_context_cases':1,'legacy_version_context_pending_cases':2,'reviewed_name_families':643,'conservative_learning_groups':213,'new_validated_independent_design_credit':0,'reference_gate_met':False,'protected_paths':len(base),'protected_paths_changed':changed,'game_starts':0,'production_changes':0,'checklist_deletions':0,'input_hashes':{n:sha(D/n) for n in ['close_bindings.py','layout_study.py','collection.json','closed-static-bindings.json','layout-study.json','semantic-review.json','combined-semantic-ledger.json','source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},ensure_ascii=False))
if __name__=='__main__':main()
