"""Freeze parallel developers' current code for a local integrated build, never for Git staging."""
import argparse,hashlib,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('source',type=Path);args=p.parse_args();baseline=R/'build/boss-eight-baseline'
if not baseline.exists():
 for sub in ['src/main/java','src/main/resources','src/generated/resources']:
  if (args.source/sub).exists():shutil.copytree(args.source/sub,baseline/sub)
 (baseline/'manifest.json').write_text(json.dumps({str(f.relative_to(baseline)):hashlib.sha256(f.read_bytes()).hexdigest() for f in baseline.rglob('*') if f.is_file()},indent=2)+'\n')
integrated=R/'build/boss-eight-integrated';shutil.copytree(baseline/'src',integrated/'src',dirs_exist_ok=True)
for id,m in json.loads((Path(__file__).parent/'targets.json').read_text()).items():
 for kind,ext in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
  rel=Path('src/main/resources/assets/dynasty')/kind/m['folder']/(id+ext);(integrated/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,integrated/rel)
 for d in m.get('dependencies',[]):shutil.copy2(R/d['path'],integrated/d['path'])
rel=Path('src/main/java/com/dynasty/client/BossEightArtBindings.java');shutil.copy2(R/rel,integrated/rel)
print('Frozen baseline + current eight-boss art in',integrated)
