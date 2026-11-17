from pathlib import Path
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 p=read('provenance.json');assert len(p['sources'])==60
 for a in p['sources']:
  f=D/a['local'];b=f.read_bytes();assert sha(f)==a['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==a['git_blob_sha1'];assert '/'+p['commit']+'/' in a['url']
 tree=read('tree-root.json');commit=read('commit.json');assert tree['sha']==commit['commit']['tree']['sha']==p['tree'] and commit['sha']==p['commit'] and not tree['truncated']
 pages=read('source-pages.json')['pages'];assert len(pages)==4
 for page in pages:
  assert sha(D/page['path'])==page['sha256']
  for a in page['sources']:assert sha(D/a['path'])==a['sha256'] and list(Image.open(D/a['path']).size)==a['size']
 chains=read('static-bindings.json')['slot_chains'];assert len(chains)==16 and len({c['id'] for c in chains})==16
 for c in chains:
  for k,h in [('concrete_class','concrete_class_sha256'),('model','model_sha256'),('default_icon','icon_sha256'),('default_worn_texture','worn_texture_sha256')]:assert sha(D/c[k])==c[h]
  assert Image.open(D/c['default_worn_texture']).size==(64,128)
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(x) for x in rules})==1
 base=read('source-baseline.json');changed=[s for s,h in base.items() if not (R/s).is_file() or sha(R/s)!=h];assert not changed,changed
 l=read('combined-semantic-ledger.json');assert l['name_families']==647 and l['armor_name_families']==633 and len(l['groups'])==214 and not l['gate_met'];assert read('semantic-review.json')['new_validated_independent_design_credit']==0
 out={'passed':True,'pinned_repository':p['repository'],'commit':p['commit'],'source_files_git_blob_verified':len(p['sources']),'newly_viewed_icon_pngs':16,'newly_viewed_custom_atlases':4,'source_pages_actually_viewed':4,'default_static_slot_chains':16,'native_3d_or_game_acceptance':False,'reviewed_name_families':647,'conservative_learning_groups':214,'validated_independent_design_total':None,'new_validated_independent_design_credit':0,'reference_gate_met':False,'protected_paths':len(base),'protected_paths_changed':changed,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'input_sha256':{n:sha(D/n) for n in ['collect.py','view_sources.py','study_bindings.py','checkpoint.py','provenance.json','source-pages.json','static-bindings.json','semantic-review.json','combined-semantic-ledger.json','source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='input_sha256'},ensure_ascii=False))
if __name__=='__main__':main()
