from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=json.loads((D/'provenance.json').read_text());assert len(p['sources'])==39
 for x in p['sources']:
  f=D/x['local'];b=f.read_bytes();assert sha(f)==x['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['git_blob_sha1'];assert p['commit'] in x['url']
 s=json.loads((D/'semantic-review.json').read_text());assert len(s['pages_actually_viewed'])==2 and len(s['icon_and_primary_wear_chains'])==8
 images=set()
 for pg in s['pages_actually_viewed']:
  assert sha(D/pg['path'])==pg['sha256'];images.update(pg['native_images'])
 assert len(images)==23
 for row in s['icon_and_primary_wear_chains']:
  for key in ['item_model','primary_wear_texture']:assert sha(R/row[key])==row[key+'_sha256']
  assert Image.open(R/row['primary_wear_texture']).size==(64,32)
  model=json.loads((R/row['item_model']).read_text());assert len(model['textures'])==len(row['layers'])
  for layer in row['layers']:assert sha(R/layer['path'])==layer['sha256'] and Image.open(R/layer['path']).size==(16,16)
 base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());changed=[p for p,h in base.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed
 rules=[Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 out={'passed':True,'source_files_verified':39,'native_source_pages_actually_viewed':2,'native_pngs_actually_viewed':23,'icon_slot_and_primary_wear_chains':8,'source_read_boundaries':'semantic-review.json','full_extra_pass_and_worn_acceptance':False,'protected_paths':len(base),'protected_changed':changed,'new_design_credit':0,'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0,'inputs':{n:sha(D/n) for n in ['collect.py','provenance.json','pages.json','semantic-review.json']}};(D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
