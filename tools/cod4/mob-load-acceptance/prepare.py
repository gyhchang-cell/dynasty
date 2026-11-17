from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent; W=B/'.work'; W.mkdir(exist_ok=True)
O=R/'docs/cod4/audit-20261022/mob-load-acceptance'
for folder in ['src/main/java','src/main/resources','src/generated/resources']:
 s=R/folder;d=W/'frozen'/folder
 if s.exists() and not d.exists():
  d.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['cp','-cR',str(s),str(d)],check=True)
hashes={str(p.relative_to(W/'frozen')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'frozen').rglob('*') if p.is_file()}
(O/'frozen-source-sha256.json').write_text(json.dumps(hashes,indent=2))
home=W/'gradle-home';home.mkdir(exist_ok=True)
for name in ['caches','wrapper','native','jdks']:
 s=Path.home()/'.gradle'/name;d=home/name
 if s.exists() and not d.exists(): subprocess.run(['cp','-cR',str(s),str(d)],check=True)
print('Isolated source and caches ready')
