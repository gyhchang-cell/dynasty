from pathlib import Path
import hashlib,json,zipfile,subprocess,sys
D=Path(__file__).resolve().parent;R=D.parents[2]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((D/'provenance.json').read_text());assert H(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:
 for f in p['files']:
  assert H(D/f['local'])==f['sha256']==hashlib.sha256(z.read(f['entry'])).hexdigest()
  if 'disassembly' in f:assert H(D/f['disassembly'])==f['disassembly_sha256']
subprocess.run([sys.executable,str(D/'review.py')],check=True)
baseline=R/'docs/art/armor-ars-reference-20261111/source-baseline.json';base=json.loads(baseline.read_text());assert len(base)==289
changed=[n for n,h in base.items() if not (R/n).exists() or H(R/n)!=h];assert not changed,changed
rules='1a083176c8853a666cea5176da66aac6b7893eaee157df4d37aa262ab6a526b6'
assert H(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))==H(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==H(D/'texture-requirements-1a083176c885.md')==rules
out={'result':'PASS_BOUNDED_STATIC_CORRESPONDENCE','archive_sha256':p['archive_sha256'],'native_entries_verified':len(p['files']),'class_disassemblies_verified':sum('disassembly' in f for f in p['files']),'four_part_chains':4,'layer_dimensions':[128,128],'protected_paths':len(base),'protected_changes':changed,'protected_baseline':str(baseline.relative_to(R)),'protected_baseline_sha256':H(baseline),'rules_sha256':rules,'native_page_actually_viewed':True,'reference_gate_met':False,'runtime_acceptance':False,'mod_class_execution':False,'game_starts':0,'production_changes':0,'checklist_deletions':0}
(D/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
