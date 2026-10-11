"""Cross-check validated art, prior accepted hashes, production JAR and native snapshots."""
import argparse,hashlib,json,zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from build_models import REPO,OUT
p=argparse.ArgumentParser();p.add_argument('--previous',required=True);p.add_argument('--validation',required=True);p.add_argument('--native',nargs='+',required=True);p.add_argument('--output',required=True);args=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
previous=json.loads((OUT/args.previous).read_text());assert previous['passed']
validation=json.loads((OUT/args.validation).read_text());assert validation['passed']
hashes=dict(previous['resource_sha256'])
for m in validation['models']:hashes.update(m['resource_sha256'])
jar=REPO/'build/cod2-voxel-build/libs/dynasty-1.4.0.jar'
with zipfile.ZipFile(jar) as z:
 assert not any('VoxelClientQa' in name for name in z.namelist()),'QA leaked into production JAR'
 for rel,wanted in hashes.items():
  assert sha((REPO/rel).read_bytes())==wanted,'Current art changed: '+rel
  entry=rel.removeprefix('src/main/resources/')
  assert sha(z.read(entry))==wanted,'Production JAR differs: '+rel
for rel,wanted in previous['resource_sha256'].items():assert hashes[rel]==wanted,'Prior accepted art overwritten'
evidence={}
for run in args.native:
 folder=OUT/'native'/run;assert (folder/'PASS.txt').exists() and not any((folder/mark).exists() for mark in ['FAIL.txt','PARTIAL.txt','ABORTED.txt']),run
 manifest=json.loads((folder/'runtime-manifest.json').read_text());entries={x['path']:x['sha256'] for group in manifest for x in group['files'] if x['path'].startswith('assets/')}
 for rel,wanted in hashes.items():assert entries[rel.removeprefix('src/main/resources/')]==wanted,(run,rel,'Snapshot differs')
 samples=json.loads((folder/'samples.json').read_text())
 evidence[run]=dict(passed=True,png_poses=len(list(folder.glob('[0-9][0-9]-*.png'))),samples_including_reload=len(samples),verified_resource_hashes=len(hashes),pass_scope=(folder/'PASS.txt').read_text().strip())
 specials=[v for v in samples if 'actualServerDetonation' in v or 'actualServerLanding' in v]
 if specials:evidence[run]['actual_server_evidence']=specials
result=dict(passed=True,jar=str(jar.relative_to(REPO)),jar_sha256=sha(jar.read_bytes()),models=[m['id'] for m in validation['models']],native_runs=args.native,scope=f'{len(hashes)} resources match current validated art, production JAR and all listed immutable actual Forge snapshots; prior accepted hashes unchanged. Native art acceptance only; full gameplay requirements remain.',native_evidence=evidence,resource_sha256=hashes,verified_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'))
(OUT/args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print('PASS',len(hashes),'resource hashes / production JAR /',len(evidence),'actual native snapshots; QA excluded')
