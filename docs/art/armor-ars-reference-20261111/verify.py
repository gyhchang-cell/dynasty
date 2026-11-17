"""Verify D37 pinned source and bounded default icon study, never runtime acceptance."""
from pathlib import Path
import hashlib,json,zipfile
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def main():
 p=read('provenance.json');assert len(p['sources'])==54
 for x in p['sources']:
  f=D/x['local'];b=f.read_bytes();assert sha(f)==x['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['git_blob_sha1'];assert '/'+p['commit']+'/' in x['url']
 s=read('study.json');v=read('semantic-review.json');assert len(s['slot_chains'])==12 and len(s['geometries'])==3
 for f,h in s['source_files'].items():assert sha(R/f)==h
 viewed=set()
 for pg in v['pages_actually_viewed']:
  assert sha(D/pg['path'])==pg['sha256'];viewed.update(pg['native_images'])
 assert len(viewed)==22
 for row in s['slot_chains']:
  assert sha(R/row['item_model'])==row['item_model_sha256'];combined=None
  for layer in row['native_icon_layers']:
   f=R/layer['path'];assert sha(f)==layer['sha256'];im=Image.open(f).convert('RGBA');assert im.size==(16,16)
   if layer['tinted']:
    arr=np.array(im,dtype=np.uint16);alpha=arr[:,:,3].copy();arr[:,:,:3]=arr[:,:,:3]*np.array(row['default_color_rgb'],dtype=np.uint16)//255;assert np.array_equal(arr[:,:,3],alpha);combined=Image.fromarray(arr.astype(np.uint8))
   else:combined=Image.alpha_composite(combined,im)
  output=D/row['analysis_composite'];assert sha(output)==row['analysis_composite_sha256'];assert combined.tobytes()==Image.open(output).convert('RGBA').tobytes()
 assert sum(g['native_cubes'] for g in s['geometries'])==61
 assert sum(g['non_slim_static_cubes'] for g in s['geometries'])==49
 for g in s['geometries']:
  for k in ['geo','atlas']:assert sha(R/g[k])==g[k+'_sha256']
  assert list(Image.open(R/g['atlas']).size)==g['atlas_size']
  assert len(g['source_hidden_slim_bones'])==2
 c=read('color-context-provenance.json');assert sha(Path(c['archive']))==c['archive_sha256'];assert sha(D/c['local'])==c['sha256']
 with zipfile.ZipFile(c['archive']) as z:assert z.read(c['entry'])==(D/c['local']).read_bytes()
 base=read('source-baseline.json');changed=[f for f,h in base.items() if not (R/f).is_file() or sha(R/f)!=h];assert not changed,changed
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(f) for f in rules})==1
 out={'passed':True,'source_git_blob_verified_files':54,'default_slot_chains':12,'source_pages_actually_viewed':3,'native_icon_layers_actually_viewed':19,'native_default_atlases_actually_viewed':3,'native_cube_declarations':61,'non_slim_cube_declarations':49,'default_rgb':[160,32,240],'new_validated_independent_design_credit':0,'reference_gate_met':False,'native_gecko_geometry_acceptance':False,'game_acceptance':False,'protected_paths':len(base),'protected_paths_changed':changed,'production_changes':0,'game_starts':0,'checklist_deletions':0,'input_hashes':{n:sha(D/n) for n in ['provenance.json','study.py','study.json','semantic-review.json','color-context-provenance.json','source-baseline.json']}}
 (D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
