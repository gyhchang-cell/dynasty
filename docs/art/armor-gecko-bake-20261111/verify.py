from pathlib import Path
import json,hashlib,math
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 contract=json.loads((D/'source-contract.json').read_text());study=json.loads((D/'local-bake-study.json').read_text())
 for s in contract['sources']:assert sha(R/s['path'])==s['sha256']
 assert sha(D/'geckolib-4.8.4-sources.jar')==contract['archive_sha256']
 counts={'mirror':0,'rotated':0,'quads':0,'face_uv':0,'box_uv':0}
 for row in study['cubes']:
  c=row['source_cube'];b=row['bake'];inf=(c.get('inflate',row['source_bone_inflate'] or 0) or 0)/16
  assert b['inflate_blocks']==inf
  verts=[v for q in b['quads'] for v in q['vertices']]
  for axis in range(3):assert math.isclose(max(v[axis] for v in verts)-min(v[axis] for v in verts),c['size'][axis]/16+2*inf,abs_tol=1e-8)
  assert b['pivot_pixels']==[-c.get('pivot',[0,0,0])[0],*c.get('pivot',[0,0,0])[1:]]
  counts['mirror']+=b['cube_mirror'];counts['rotated']+=any(c.get('rotation',[0,0,0]));counts['quads']+=len(b['quads']);counts['box_uv' if isinstance(c['uv'],list) else 'face_uv']+=1
  if not isinstance(c['uv'],list):assert {q['direction'] for q in b['quads']}==set(c['uv'])
 for g in study['geometries']:
  assert sha(R/g['geo'])==g['sha256'];assert sum(g['slot_cube_counts_assuming_base_parts_visible'].values()) in [14,19,16]
  for names in g['slot_visible_bones_assuming_base_parts_visible'].values():assert not any('slim' in n.lower() for n in names)
 base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());changed=[p for p,h in base.items() if not (R/p).is_file() or sha(R/p)!=h];assert not changed
 rules=[R/'docs/art/USER_TEXTURE_REQUIREMENTS.md',Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),next(D.glob('texture-requirements-*.md'))];assert len({sha(p) for p in rules})==1
 out={'passed':True,'scope':'61 source-derived local cubes; native source contract, not Java execution or equipped rendering','checked_counts':counts,'source_files':len(contract['sources']),'slot_cube_counts':{g['model']:g['slot_cube_counts_assuming_base_parts_visible'] for g in study['geometries']},'protected_paths':len(base),'protected_paths_changed':changed,'new_design_credit':0,'production_changes':0,'game_starts':0,'reference_gate_met':False,'checklist_deletions':0,'pending':['full equipped hierarchy/animation/external hooks and per-entity branches not runtime-tested','Ars pinned upstream build dependency version and custom factory registration not yet ruled out;4.8.4 Builtin contract is bounded'],'input_hashes':{n:sha(D/n) for n in ['source-contract.json','local-bake-study.json','study.py']}}
 (D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
