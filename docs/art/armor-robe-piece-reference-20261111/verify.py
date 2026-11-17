from pathlib import Path
import hashlib,json,zipfile,subprocess,sys
D=Path(__file__).resolve().parent;R=D.parents[2];H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((D/'provenance.json').read_text());assert H(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:
 for f in p['files']:
  assert H(D/f['local'])==f['sha256']==hashlib.sha256(z.read(f['entry'])).hexdigest()
  if 'disassembly' in f:assert H(D/f['disassembly'])==f['disassembly_sha256']
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert len(base)==289 and all(H(R/n)==h for n,h in base.items())
subprocess.run([sys.executable,str(D/'review.py')],check=True)
print('PASS original archive entries/disassembly hashes and 289 protected paths; bounded static consumers only')
