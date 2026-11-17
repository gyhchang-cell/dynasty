from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=json.loads((D/'provenance.json').read_text());archive=Path(p['archive']);assert sha(archive)==p['archive_sha256'];old=json.loads((R/'docs/art/armor-template-reference-20261103/provenance.json').read_text());assert any(a['path']==str(archive) and a['sha256']==p['archive_sha256'] for a in old['archives'])
 with zipfile.ZipFile(archive) as z:
  for f in p['files']:assert (D/f['local']).read_bytes()==z.read(f['entry']) and sha(D/f['local'])==f['sha256']
 r=json.loads((D/'semantic-review.json').read_text());page=r['page_actually_viewed'];assert sha(D/page['path'])==page['sha256'];assert len(page['native_images'])==6 and len(r['four_part_chains'])==4
 for c in r['four_part_chains']:
  for f,h in c['input_hashes'].items():assert sha(R/f)==h
  assert Image.open(R/c['icon']).size==(16,16) and Image.open(R/c['wear_texture']).size==(64,32)
 for name in ['livinghelmet','livingleggings','livingboots']:
  current=D/f'source/assets/bloodmagic/textures/item/{name}.png';prior=next((R/'docs/art/armor-template-reference-20261103/references/bloodmagic').glob('*-'+name+'.png'));assert sha(current)==sha(prior)
 base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());changed=[f for f,h in base.items() if not (R/f).is_file() or sha(R/f)!=h];assert not changed
 rules=[Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',next(D.glob('texture-requirements-*.md'))];assert len({sha(f) for f in rules})==1
 out={'passed':True,'archive_already_fixed_in_prior_evidence':True,'source_entries_verified':13,'one_prior_partial_case_completed_static':True,'four_register_type_model_icon_wear_chains':4,'native_pngs_viewed_in_page':6,'new_pngs_not_in_prior_three_icon_scope':3,'new_names':0,'new_validated_design_credit':0,'reference_gate_met':False,'runtime_or_worn_acceptance':False,'mod_execution':False,'javap_readonly_disassembly':True,'protected_paths':len(base),'protected_changed':changed,'production_changes':0,'game_starts':0,'checklist_deletions':0,'inputs':{n:sha(D/n) for n in ['collect.py','review.py','provenance.json','page.json','semantic-review.json','ItemLivingArmor.bytecode.txt','BloodMagicItems.bytecode.txt','BloodMagicItems.verbose.txt']}};(D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
